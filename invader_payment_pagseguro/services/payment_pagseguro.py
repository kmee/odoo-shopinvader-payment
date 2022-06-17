#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

import requests

from odoo.exceptions import UserError, ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)


class PaymentServicePagseguro(AbstractComponent):
    _name = "payment.service.pagseguro"
    _inherit = "base.rest.service"
    _usage = "payment_pagseguro"
    _description = "REST Services for Pagseguro payments"

    @property
    def payment_service(self):
        return self.component(usage="invader.payment")

    def _get_payable(self, target, params):
        """ Get payable from cart and validate if acquirer is Pagseguro """
        payable = self.payment_service._invader_find_payable_from_target(
            target, **params
        )
        self.payment_service._check_provider(
            payable.payment_mode_id, "pagseguro"
        )

        return payable

    @restapi.method(
        [(["/confirm-payment"], "POST")],
        input_param=restapi.CerberusValidator("_get_schema_confirm_payment"),
        output_param=restapi.CerberusValidator(
            "_get_schema_return_confirm_payment"
        ),
    )
    def confirm_payment(self, target, **params):
        """ Create charge from payable sale order"""
        card = params.get("card")

        payable = self._get_payable(target, params)

        token = self._get_token(card, payable)
        transaction = self._pagseguro_prepare_payment_transaction_data(
            payable, token
        )
        transaction.pagseguro_s2s_do_transaction()

        return {
            "transaction_status": transaction.state,
        }

    def _pagseguro_prepare_payment_transaction_data(self, payable, token):
        transaction_data = payable._invader_prepare_payment_transaction_data(
            payable.payment_mode_id
        )
        transaction_data["payment_token_id"] = token.id

        return self.env["payment.transaction"].create(transaction_data)

    def _get_token(self, card, payable):
        acquirer = payable.payment_mode_id.payment_acquirer_id
        partner = payable.partner_id

        data = {
            "acquirer_id": acquirer.id,
            "partner_id": partner.id,
            "cc_holder_name": card.get("name"),
            "cc_token": card.get("token"),
            "payment_method": "CREDIT_CARD",
            "installments": card.get("installments"),
        }

        return acquirer.pagseguro_s2s_form_process(data)

    def _get_schema_confirm_payment(self):
        res = self.payment_service._invader_get_target_validator()
        res.update(
            {
                "card": {
                    "type": "dict",
                    "required": True,
                    "schema": {
                        "name": {"type": "string", "required": True},
                        "token": {"type": "string", "required": True},
                        "installments": {
                            "type": "integer",
                            "coerce": int,
                            "required": True,
                        },
                    },
                }
            }
        )
        return res

    def _get_schema_return_confirm_payment(self):
        return {
            "transaction_status": {"type": "string", "required": True},
        }

    @restapi.method(
        [(["/public-key"], "GET")],
        input_param=restapi.CerberusValidator("_get_schema_public_key"),
        output_param=restapi.CerberusValidator(
            "_get_schema_return_public_key"
        ),
    )
    def public_key(self, target, **params):
        """ Get public key to encrypt card

        return public_key (string): public key related to acquirer token
        """
        acquirer_id = self.env.ref(
            "payment_pagseguro.payment_acquirer_pagseguro"
        ).id
        payload = {"jsonrpc": "2.0", "params": {"acquirer_id": acquirer_id}}
        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        res = requests.get(
            base_url + "/payment/pagseguro/public_key", json=payload
        )

        content = json.loads(res.content)
        if content.get("result"):
            return {
                "public_key": content.get("result"),
                "success": True,
            }
        elif content.get("error"):
            message = content.get("error", {}).get("data", {}).get("message")
            return {
                "public_key": "",
                "success": False,
                "error": message,
            }
        else:
            return {
                "public_key": "",
                "success": False,
                "error": "Unknown error",
            }

    def _get_schema_public_key(self):
        """ Get default api key and user email validator """
        return self.payment_service._invader_get_target_validator()

    def _get_schema_return_public_key(self):
        """
        Return validator of checkout_url service
        checkout_url (str): Redirect checkout url
        """
        return {
            "public_key": {"type": "string", "required": True},
            "success": {"type": "boolean", "required": True},
            "error": {"type": "string", "required": False},
        }

    @restapi.method(
        [(["/confirm-payment-pix"], "POST")],
        input_param=restapi.CerberusValidator(
            "_get_schema_confirm_payment_pix"
        ),
        output_param=restapi.CerberusValidator(
            "_get_schema_return_confirm_payment_pix"
        ),
    )
    def confirm_payment_pix(self, target, **params):
        # Get body params
        tx_id = params.get("tx_id")

        payable = self._get_payable(target, params)

        token = self._get_token_pix(payable, tx_id)

        transaction = self._pagseguro_prepare_payment_transaction_data(
            payable, token
        )

        try:
            res = transaction.pagseguro_pix_do_transaction()
        except (UserError, ValidationError) as e:
            return {"result": False, "error": str(e)}

        return res

    def _get_token_pix(self, payable, tx_id):
        acquirer = payable.payment_mode_id.payment_acquirer_id
        partner = payable.partner_id

        payment_token = (
            self.env["payment.token"]
            .sudo()
            .create(
                {
                    "acquirer_ref": partner.id,
                    "acquirer_id": acquirer.id,
                    "partner_id": partner.id,
                    "pagseguro_tx_id": tx_id,
                }
            )
        )

        return payment_token

    def _get_schema_confirm_payment_pix(self):
        res = self.payment_service._invader_get_target_validator()
        res.update({"tx_id": {"type": "string", "required": True}})
        return res

    def _get_schema_return_confirm_payment_pix(self):
        return {
            "result": {"type": "boolean", "required": True},
            "location": {"type": "string", "required": False},
            "error": {"type": "string", "required": False},
        }

    @restapi.method(
        [(["/search-payment-pix"], "GET")],
        input_param=restapi.CerberusValidator("_get_schema_search_pix"),
        output_param=restapi.CerberusValidator(
            "_get_schema_return_search_pix"
        ),
    )
    def search_payment_pix(self, **params):
        """Query the payment status of the pix collection"""
        # Get body params
        tx_id = params.get("tx_id") + "?"
        revisao = params.get("revisao")

        r = self.env["payment.transaction"].pagseguro_search_payment_pix(
            tx_id, revisao
        )
        # # cert = acquirer.get_cert()
        # # auth_token = acquirer.pagseguro_pix_acces_token
        # base_url = (
        #     self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        # )
        # _logger.error('base URL >>> ' + base_url)
        # url = 'https://secure.sandbox.api.pagseguro.com'
        #
        # header = {
        #     "Authorization": "Bearer " + auth_token,
        #     "Content-Type": "application/json",
        # }

        res = r.json()
        _logger.info(res)
        return {
            "public_key": "ATIVEI",  # res.get("status"),
            "success": False,
            "error": "Unknown error",
        }

    def _get_schema_search_pix(self):
        """ Get default api key and user email validator """
        return {
            "tx_id": {"type": "string", "required": True},
            "revisao": {"type": "string", "required": True},
        }

    def _get_schema_return_search_pix(self):
        """
        Return validator of checkout_url service
        checkout_url (str): Redirect checkout url
        """
        return {
            "status": {"type": "string", "required": True},
            # "success": {"type": "boolean", "required": True},
            # "error": {"type": "string", "required": False},
        }

    @restapi.method(
        [(["/confirm-payment-boleto"], "POST")],
        input_param=restapi.CerberusValidator(
            "_get_schema_confirm_payment_boleto"
        ),
        output_param=restapi.CerberusValidator(
            "_get_schema_return_confirm_payment_boleto"
        ),
    )
    def confirm_payment_boleto(self, target, **params):
        """ Confirm payment with Boleto.

        Creates a pagseguro charge and change the sale order status to authorized.
        Returns result True when Pagseguro's charge is created successfully.
        """
        payable = self._get_payable(target, params)

        token = self._get_token_boleto(payable)

        transaction = self._pagseguro_prepare_payment_transaction_data(
            payable, token
        )

        try:
            res = transaction.pagseguro_boleto_do_transaction()
        except Exception as e:
            return {"res": {"error": str(e)}}

        return {"res": res}

    def _get_token_boleto(self, payable):
        acquirer = payable.payment_mode_id.payment_acquirer_id
        partner = payable.partner_id

        payment_token = (
            self.env["payment.token"]
            .sudo()
            .create(
                {
                    "acquirer_ref": partner.id,
                    "acquirer_id": acquirer.id,
                    "partner_id": partner.id,
                    "pagseguro_payment_method": "BOLETO",
                }
            )
        )

        return payment_token

    def _get_schema_confirm_payment_boleto(self):
        return self.payment_service._invader_get_target_validator()

    @staticmethod
    def _get_schema_return_confirm_payment_boleto():
        return {
            "res": {"type": "dict", "allow_unknown": True, "required": False}
        }
