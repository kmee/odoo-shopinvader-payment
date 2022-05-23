#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from cerberus import Validator

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import AbstractComponent

_logger = logging.getLogger(__name__)

SANDBOX_URL = (
    "https://sandbox.pagseguro.uol.com.br/v2/checkout/payment.html?code="
)


class PaymentServicePagseguro(AbstractComponent):
    _name = "payment.service.pagseguro"
    _inherit = "base.rest.service"
    _usage = "payment_pagseguro"
    _description = "REST Services for Pagseguro payments"

    @property
    def payment_service(self):
        return self.component(usage="invader.payment")

    def checkout_url(self, target, **params):
        """ Get Pagseguro redirect checkout url from current cart """
        sale_order_id = params.get("sale_order_id")
        _logger.warning("Sale Order id: ", sale_order_id)
        code = sale_order_id
        url = SANDBOX_URL + code
        return url

    def _validator_checkout_url(self):
        """
        Validator of checkout_url service
        sale_order_id (int): Payment sale order
        :return: dict
        """
        res = self.payment_service._invader_get_target_validator()
        res.update(
            {
                "sale_order_id": {
                    "coerce": to_int,
                    "type": "integer",
                    "required": True,
                },
            }
        )
        return res

    def _validator_return_confirm_payment(self):
        """
        Return validator of checkout_url service
        checkout_url (str): Redirect checkout url
        """
        return Validator(
            {
                "checkout_url": {"type": "string"},
                "success": {"type": "boolean"},
                "error": {"type": "string"},
            },
            allow_unknown=True,
        )
