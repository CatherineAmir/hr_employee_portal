# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    """ This model represents hr.employee."""
    _inherit = "hr.employee"

    def create_user_portal(self):
        for employee in self:
            if not employee.user_id and employee.work_email:
                portal_group = self.env.ref('base.group_portal')
                user = self.env['res.users'].create({
                    'name': employee.name,
                    'login': employee.work_email,
                    'password':'12345',
                    'groups_id': [(6, 0, [portal_group.id])],
                })
                employee.user_id = user
                employee.work_email = user.login
                user.action_reset_password()