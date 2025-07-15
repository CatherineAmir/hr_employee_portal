from datetime import datetime

from odoo.exceptions import AccessError, UserError, ValidationError  # -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrLeave(models.Model):
    """ This model represents hr.leave."""
    _name = 'hr.leave'
    _inherit = ['hr.leave', 'portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin', 'sequence.mixin']
    state=fields.Selection(selection_add=[
        ('cancellation_request', "Cancellation Request"),
    ])


    def action_approve(self, check_state=True):
        super(HrLeave, self).action_approve(check_state)
        current_employee = self.employee_id

        mandatory_days = current_employee.get_mandatory_days(self.request_date_from, self.request_date_to)

        for key in mandatory_days:
            if self.request_date_from >= datetime.strptime(key,
                                                           "%Y-%m-%d").date() or self.request_date_to <= datetime.strptime(
                key, "%Y-%m-%d").date():
                raise UserError(_("You Can't ask Time off on Mandatory Days %s", list(mandatory_days.keys())))
        return True
