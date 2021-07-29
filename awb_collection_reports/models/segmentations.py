from odoo import api, fields, models, _

import logging


_logger = logging.getLogger(__name__)

class AWBSegmentationInvoice(models.Model):
	_inherit = 'account.move'

	monthly_service = fields.Float()
	device = fields.Float()
	security_deposit = fields.Float()
	others = fields.Float()
	segmentation_price = fields.Monetary(related='invoice_line_ids.price_subtotal')
	segmentation_boolean = fields.Boolean(compute='segmentation_recompute')

	@api.depends('segmentation_boolean')
	def segmentation_recompute(self):
		for rec in self:
			rec.segmentation_boolean = True
			self.compute_segmentations()

	def compute_segmentations(self):
		total1 = 0
		total2 = 0
		total3 = 0
		total4 = 0
		if self.invoice_line_ids:
			for rec in self.invoice_line_ids:
				if rec.product_id.product_tmpl_id.product_segmentation == "month_service":
					total1 += rec.price_subtotal
					self.monthly_service = total1
					continue
				elif rec.product_id.product_tmpl_id.product_segmentation == "device":
					total2 += rec.price_subtotal
					self.device = total2
					continue
				elif rec.product_id.product_tmpl_id.product_segmentation == "security_deposit":
					total3 += rec.price_subtotal
					self.security_deposit = total3
					continue
				elif rec.product_id.product_tmpl_id.product_segmentation == "others":
					total4 += rec.price_subtotal
					self.others = total4
					continue
				

class AWBSegmentationPayment(models.Model):
	_inherit = 'account.payment'

	monthly_service = fields.Float()
	device = fields.Float()
	security_deposit = fields.Float()
	others = fields.Float()

	segmentation_price = fields.Monetary(related='invoice_line.invoice_amount')
	segmentation_boolean = fields.Boolean(compute='segmentation_recompute')

	@api.depends('segmentation_boolean')
	def segmentation_recompute(self):
		for rec in self:
			rec.segmentation_boolean = True
			self.compute_segmentations_payments()

	def compute_segmentations_payments(self):
		total1 = 0
		total2 = 0
		total3 = 0
		total4 = 0
		if self.invoice_line:
			for rec in self.invoice_line:
				for line in rec.invoice:
					for x in line.invoice_line_ids:
						if x.product_id.product_tmpl_id.product_segmentation == "month_service":
							total1 += x.price_subtotal
							self.monthly_service = total1
							continue
						elif x.product_id.product_tmpl_id.product_segmentation == "device":
							total2 += x.price_subtotal
							self.device = total2
							continue
						elif x.product_id.product_tmpl_id.product_segmentation == "security_deposit":
							total3 += x.price_subtotal
							self.security_deposit = total3
							continue
						elif x.product_id.product_tmpl_id.product_segmentation == "others":
							total4 += x.price_subtotal
							self.others = total4
							continue