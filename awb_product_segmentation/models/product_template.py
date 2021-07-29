
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    product_segmentation = fields.Selection([
        ('month_service','Monthly Service Fee'),
        ('device','Device Fee'),
        ('security_deposit','Security Deposit Fee'),
        ('others','Others')], string="Product Segmentation" ,tracking=True)
        