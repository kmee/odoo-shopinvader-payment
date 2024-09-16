# Copyright 2023 KMEE
# Lisence AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models,fields

class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[("BB", "Banck of Brazil")])
