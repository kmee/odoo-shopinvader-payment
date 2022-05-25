#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

import requests
from odoo.addons.base_rest.components.service import to_int
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
        """ Create charge from sale order"""
        sale_order_id = params.get("sale_order_id")
        partner_id = params.get("partner_id")
        cc_holder_name = params.get("cc_holder_name")
        cc_token = params.get("cc_token")
        payable = self.payment_service._invader_find_payable_from_target(
            target, **params
        )

        acquirer_id = self.env.ref(
            "payment_pagseguro.payment_acquirer_pagseguro"
        ).id
        sale_order = self.env['sale.order'].browse(sale_order_id)

        payload = {
            "jsonrpc": "2.0",
            "params": {
                "acquirer_id": acquirer_id,
                "partner_id": partner_id,
                "cc_holder_name": cc_holder_name,
                "cc_token": cc_token,
            }
        }
        _logger.info("Sending payload: %s" % payload)

        base_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        res = requests.get(
            base_url + "/pagseguro_s2s_create_json_3ds", json=payload
        )

        return {
            "res": str(sale_order_id),
            "result": True
        }

    def _get_schema_confirm_payment(self):
        res = self.payment_service._invader_get_target_validator()
        res.update(
            {
                "sale_order_id": {
                    "coerce": to_int,
                    "type": "integer",
                    "required": True,
                },
                "partner_id": {
                    "coerce": to_int,
                    "type": "integer",
                    "required": False,
                },
                "cc_holder_name": {
                    "type": "string",
                    "required": True,
                },
                "cc_token": {
                    "type": "string",
                    "required": True,
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
