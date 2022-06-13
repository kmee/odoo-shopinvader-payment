#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.http import Controller, route

_logger = logging.getLogger(__name__)


class NotificationPagseguroControler(Controller):
    @route("/notification-url", auth="public", type="json", methods=["POST"])
    def notification_url(self):
        _logger.info("You have received a notification from Pagseguro.")

        return {"res": True}
