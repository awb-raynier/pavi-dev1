# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    current = fields.Float(string='Current', compute='_compute_current', store=True)
    arrears = fields.Float(string='Arrears', compute='_compute_arrears',store=True)
    advances = fields.Float(string='Advances', compute='_compute_advances', store=True)

    @api.depends('invoice_ids.amount_total', 'amount')
    def _compute_current(self):
        for record in self:
            args = [
                ('id','in', record.invoice_ids.ids),
                ('type','=','out_invoice'),
                ('invoice_payment_state','=','paid'),
                ('state','=','posted'),
                ('invoice_date_due', '>=', record.payment_date)
            ]
            paid_invoices = record.env['account.move'].search(args)
            if record.payment_date:
                record.current = sum(paid_invoices.mapped('amount_total'))

    @api.depends('invoice_ids.amount_total', 'amount')
    def _compute_arrears(self):
        for record in self:
            args = [
                ('id','in', record.invoice_ids.ids),
                ('type','=','out_invoice'),
                ('state','=','posted'),
                ('invoice_date_due', '<', record.payment_date)
            ]
            paid_invoices = record.env['account.move'].search(args)
            if record.payment_date:
                record.arrears = sum(paid_invoices.mapped('amount_total'))

    @api.depends('invoice_ids.amount_residual', 'amount')
    def _compute_advances(self):
        for record in self:
            args = [
                ('id','in', record.invoice_ids.ids),
                ('type','=','out_invoice'),
                ('state','=','posted'),
            ]    
            paid_invoices = record.env['account.move'].search(args)
            if record.payment_date:
                record.advances = record.amount - sum(paid_invoices.mapped('amount_residual'))