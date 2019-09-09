# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class InvaderPaymentService(Component):

    _name = "invader.payment.service"
    _usage = "invader.payment"

    def _invader_find_payable_from_target(self, target, **params):
        """
        Find an invader.payable from a target parameter (e.g. current cart).

        target and params comply with the schema returned by
        ``_invader_get_target_validator``.
        """
        raise NotImplementedError()

    def _invader_find_payable_from_transaction(self, transaction):
        """
        Find the invader.payble linked to a payment.transaction.

        This method is used to inform the payable when a transaction was
        accepted, in situations where we are informed of payment success
        through a webhook call from the payment acquirer.

        TODO: in a future refactoring, we should eliminate
        ``_invader_payment_accepted`` which is possible if the payable
        "listens" for state change events on its associated
        ``payment.transaction``.
        In that case ``_invader_find_payable_from_transaction`` can be
        removed too.
        """
        raise NotImplementedError()

    def _invader_restrict_payment_mode_ids(self):
        return []

    def _invader_get_target_validator(self):
        """
        Return a cerberus validator schema fragment that specifies the
        target being paid. Implementations must extend it by populating
        the "allowed" field (eg with strings such as 'current_cart') and
        possibly adding other fields.
        """
        validator = {
            "target": {"type": "string", "required": True, "allowed": []},
            "payment_mode_id": {
                "coerce": to_int,
                "type": "integer",
                "required": True,
            },
        }
        ids = self._invader_restrict_payment_mode_ids()
        if ids:
            validator["payment_mode_id"]["allowed"] = ids
        return validator

    def _invader_get_payment_success_reponse_data(
        self, payable, target, **params
    ):
        """
        This is mostly used by ShopInvader to manipulate session and
        store_cache after payment success.

        TODO: this method will go away when a better mechanism for Shopinvader
        session management is in place.
        """
        return {}
