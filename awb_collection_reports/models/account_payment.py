# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    current = fields.Float(string='Current', readonly=True)
    arrears = fields.Float(string='Arrears', readonly=True)
    advances = fields.Float(string='Advances', readonly=True)