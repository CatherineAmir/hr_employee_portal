from datetime import datetime

from odoo.exceptions import AccessError, UserError, ValidationError  # -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrLeave(models.Model):
    """ This model represents hr.leave."""
    _name = 'hr.leave'
    _inherit = ['hr.leave', 'portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin']
    state=fields.Selection(selection_add=[
        ('cancellation_request', "Cancellation Request"),
    ],
    help=" The status is set to 'To Submit', when a time off request is created." +
        "\nThe status is 'To Approve', when time off request is confirmed by user." +
        "\nThe status is 'Refused', when time off request is refused by manager." +
        "\nThe status is 'Approved', when time off request is approved by manager."+
        "\nThe status is 'Request to Cancellation Request', when time off request is Requested to be Cancelled by the employee."+
        "\nThe status is 'Cancelled', when time off request of cancellation is Approved by manager"
        )


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

    @api.depends_context('uid')
    @api.depends('state', 'employee_id')
    def _compute_can_cancel(self):
        now = fields.Datetime.now().date()
        for leave in self:
            leave.can_cancel = (leave.id and leave.employee_id.user_id == self.env.user and leave.state in [
                'validate', 'validate1'] and leave.date_from and leave.date_from.date() >= now) or \
            (leave.id and leave.employee_id.user_id != self.env.user and leave.state in [
                'cancellation_request'] and leave.date_from and leave.date_from.date() >= now)

