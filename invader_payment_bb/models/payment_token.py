# Copyright 2023 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentToken(models.Model):
    _inherit = "payment.token"

    bb_payment_method = fields.Char(string="Banck of Brazil Payment Method")
    
    bb_tx_id = fields.Char(string="Banck of Brazil PIX Transaction Id") # TODO talvez este não seja usado...
