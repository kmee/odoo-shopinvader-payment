#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

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

    def confirm_payment(self, target, **params):
        _logger.info("payment confirmed")
