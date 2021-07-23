from odoo import api, fields, models, _


class AWBSegmentationInvoice(models.Model):
	_inherit = 'account.move'

	monthly_service = fields.Float()
	device = fields.Float()
	security_deposit = fields.Float()
	others = fields.Float()

	@api.onchange('invoice_line_ids.product_id')
	def compute_segmentations(self):

		for rec in self:
			if rec.invoice_line_ids:
				for line in self.invoice_line_ids:
					if line.product_id.product_tmpl_id.product_segmentation == 'month_service':
						self.monthly_service = line.price_unit * line.quantity
					elif line.product_id.product_tmpl_id.product_segmentation == 'device':
						self.device = line.price_unit * line.quantity
					elif line.product_id.product_tmpl_id.product_segmentation == 'security_deposit':
						self.security_deposit = line.price_unit * line.quantity
					elif line.product_id.product_tmpl_id.product_segmentation == 'others':
						self.others = line.price_unit * line.quantity

class AWBSegmentationPayment(models.Model):
	_inherit = 'account.payment'

	monthly_service = fields.Float()
	device = fields.Float()
	security_deposit = fields.Float()
	others = fields.Float()