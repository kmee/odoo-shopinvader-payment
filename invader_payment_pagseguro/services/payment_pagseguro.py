#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

import requests

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

        payable = self.payment_service._invader_find_payable_from_target(
            target, **params
        )
        self.payment_service._check_provider(
            payable.payment_mode_id, "pagseguro"
        )

        token = self._get_token(card, payable)
        transaction = self._pagseguro_prepare_payment_transaction_data(
            payable, token
        )
        transaction.pagseguro_s2s_do_transaction()

        return {
            "res": str(transaction.id),
            "result": True,
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
            "payment_method": card.get("payment_method"),
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
                        "payment_method": {
                            "type": "string",
                            "required": True,
                            "allowed": ["CREDIT_CARD"],
                        },
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
            "result": {"type": "boolean", "required": True},
            "res": {"type": "string", "required": True},
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
