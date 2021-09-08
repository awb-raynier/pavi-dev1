from odoo import api, fields, models, _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ProjectMoveIn(models.Model):
	_name = 'project.move.in'

	def _default_project(self):
		project = self.env['project.project'].browse(self.env.context.get('active_ids', []))
		return self.env['project.project'].search([('id', '=', project.id)], limit=1).id

	date = fields.Date(default=datetime.now(), store=True)
	move_in = fields.Integer(required=True, store=True)
	project_id = fields.Many2one('project.project', store=True, default=_default_project)


class CustomProject(models.Model):
	_inherit = 'project.project'

	move_in_lines = fields.One2many('project.move.in', 'project_id', copy=False, ondelete='cascade')
	move_in_number = fields.Integer(compute='_compute_move_in_total', default = 0)
	house_pass_number = fields.Integer(store=True)
	move_in_line_ids = fields.Many2one()


	def move_in_button(self):
		return {
			'name': _('Move In'),
			'view_mode': 'tree',
			'res_model': 'project.move.in',
			'view_id': False,
			'views': [(self.env.ref('awb_subscriber_location.view_project_move_in_tree').id, 'tree')],
			'type': 'ir.actions.act_window',
			'domain': [('project_id', '=', self.id)],
		}

	@api.depends('move_in_lines')
	def _compute_move_in_total(self):
		for rec in self:
			rec.move_in_number = 0
			for lines in rec.move_in_lines:
				if lines.move_in:
					rec.move_in_number += lines.move_in
					

	@api.onchange('house_pass_number')
	def house_pass_checker(self):
		for rec in self:
			if rec.house_pass_number < 0:
				rec.house_pass_number = 0
				return {'warning': {
						'title': ("Warning for negative value"),
						'message': ("Cannot input negative value")
					}}


class SubscriberLocation(models.Model):
	_inherit = 'subscriber.location'

	house_pass = fields.Integer(compute='_compute_house_pass')
	move_in = fields.Integer(compute='_compute_move_in')

	@api.depends('project_ids')
	def _compute_house_pass(self):
		for rec in self:
			rec.house_pass = 0
			for lines in rec.project_ids:
				if lines.house_pass_number:
					rec.house_pass += lines.house_pass_number

	@api.depends('project_ids')
	def _compute_move_in(self):
		for rec in self:
			rec.move_in = 0
			for lines in rec.project_ids:
				if lines.move_in_number:
					rec.move_in += lines.move_in_number