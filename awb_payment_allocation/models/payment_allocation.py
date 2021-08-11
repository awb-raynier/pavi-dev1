# -*- coding: utf-8 -*-
##############################################################################
#
#   ACHIEVE WITHOUT BORDERS
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

class AccountPayment(models.Model):
	_inherit = 'account.payment'

	posting_date = fields.Datetime()


class PaymentAllocationLine(models.Model):
	_inherit = 'payment.allocation.line'
	
	invoice_total = fields.Monetary(related='invoice.amount_total')