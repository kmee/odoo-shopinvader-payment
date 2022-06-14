#  Copyright 2022 KMEE
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.http import Controller, request, route

_logger = logging.getLogger(__name__)


class NotificationPagseguroControler(Controller):
    @route("/notification-url", auth="public", type="json", methods=["POST"])
    def notification_url(self):
        """ Receives Pagseguro Charge notification.
        Returns true on success and False on fail.
        Since this is a sensitive public route no further information is given.
        """
        params = request.jsonrequest
        notification_code = params.get("id")
        tx = (
            request.env["payment.transaction"]
            .sudo()
            .search([("acquirer_reference", "=", notification_code)])
        )
        tx.ensure_one()

        # Sends requests to pagseguro to check charge status instead of trusting
        # notification payload
        try:
            tx.pagseguro_check_transaction()
        except Exception as e:
            _logger.error(e)
            return False

        return True
