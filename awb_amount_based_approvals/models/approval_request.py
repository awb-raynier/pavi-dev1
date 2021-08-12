# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    department_id = fields.Many2one('hr.department', String='Department', domain="[('company_id', '=', company_id)]")
    manager_id = fields.Many2one('hr.employee', String='Manager', domain="[('company_id', '=', company_id)]")

    def _get_data_approvers(self, head_id, req_id, sequence, add_seq=0):
        data = {
            'user_id': head_id,
            'request_id': req_id,
            'sequence': sequence + add_seq ,
        }
        _logger.debug(f'Approvers: {data}')
        return data

    def _approval_checker(self, manager, head, owner, *approvers):

        approvers_list = []
        approvers_list.append(manager)
        approvers_list.append(head)

        if manager == head:
            raise UserError(_('Duplicate User found in this approvers'))
        
        for approver in approvers_list:
            if approver == owner:
                raise UserError(_('Request owner must not be one of the approver'))

    def action_confirm(self):

        manager_id = self.mapped('manager_id').user_id.id
        head_id = self.mapped('department_id').operation_head.user_id.id

        data_approvers = []
        add_seq = 0

        args = [
            ('category', '=', self.category_id.id),
            ('min_amount', '<=', self.amount),
            ('max_amount', '>=', self.amount),
        ]
        approval_rule = self.sudo().env['approval.rule'].search(args, limit=1)
        _logger.debug(f'ApprovalRule: {approval_rule}')

        category = self.mapped('category_id')
        rule = category.filtered(lambda x: x.id == approval_rule.category.id).rule_ids
        _logger.debug(f'CategoryID: {rule}')

        self._approval_checker(manager_id, head_id, self.request_owner_id.id, self.mapped('approver_ids').user_id)
        if rule.manager_id:
            if manager_id:
                data = self._get_data_approvers(manager_id, self.id, 1)
                data_approvers.append((0, 0, data))
            else:
                raise UserError(_('You need to set First Approver to Proceed'))
        if rule.operation_head_id:
            if head_id:
                data = self._get_data_approvers(head_id, self.id, 2)
                data_approvers.append((0, 0, data))
            else:
                raise UserError(_('You need to set Second Approver to Proceed'))
        if len(data_approvers) > 0:
            self.sudo().update({'approver_ids': [(5,0,0)]})
            self.sudo().update({'approver_ids': data_approvers})

        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(_("You have to add at least %s approvers to confirm your request.") % self.approval_minimum)
        if self.requirer_document == 'required' and not self.attachment_number:
            raise UserError(_("You have to attach at lease one document."))
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        approvers._create_activity()
        approvers.write({'status': 'pending'})
        self.write({'date_confirmed': fields.Datetime.now()})
    
        res = super(ApprovalRequest, self).action_confirm()
        return res


class ApprovalApprover(models.Model):
    _inherit = 'approval.approver'

    sequence = fields.Integer(string='Sequence', default=1, readonly=True)
    approval_condition = fields.Selection([('and', 'AND'), ('or', 'OR')], string='Condition', default='and')
