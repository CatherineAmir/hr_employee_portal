# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    """ This model represents hr.employee."""
    _inherit = "hr.employee"

    time_off_approver=fields.Many2one('res.users', string="Time of Approver (Manager)")
    leave_manager_id=fields.Many2one('res.users', string="Leave Manager",compute='_compute_leave_manager',store=True)

    @api.depends('time_off_approver')
    def _compute_leave_manager(self):
        for employee in self:
            if  employee.time_off_approver and not employee.time_off_approver._is_portal():
                employee.leave_manager_id = employee.time_off_approver.id
            else:
                employee.leave_manager_id=False



    def create_user_portal(self):
        for employee in self:
            if not employee.user_id and employee.work_email:
                portal_group = self.env.ref('base.group_portal')
                user = self.env['res.users'].sudo().create({
                    'name': employee.name,
                    'login': employee.work_email,
                    'password':'12345',
                    'groups_id': [(6, 0, [portal_group.id])],
                })
                employee.user_id = user
                employee.work_email = user.login
                user.with_context(create_user=1).sudo().action_reset_password()