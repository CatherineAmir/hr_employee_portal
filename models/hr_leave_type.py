# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.tools.float_utils import float_round


class HrLeaveType(models.Model):
    """ This model represents hr.leave.type."""
    _inherit = 'hr.leave.type'

    hide_allocation_from_user=fields.Boolean(string="Hide allocation from user",default=False)

    # @api.depends('requires_allocation', 'virtual_remaining_leaves', 'max_leaves', 'request_unit')
    # @api.depends_context('holiday_status_display_name', 'employee_id', 'from_manager_leave_form')
    # def _compute_display_name(self):
    #
    #     if not self.requested_display_name():
    #         # leave counts is based on employee_id, would be inaccurate if not based on correct employee
    #
    #         return super()._compute_display_name()
    #     for record in self:
    #         name = record.name
    #         if record.requires_allocation == "yes" and not self._context.get("from_manager_leave_form") and not self.hide_allocation_from_user:
    #             remaining_time = float_round(record.virtual_remaining_leaves, precision_digits=2) or 0.0
    #             maximum = float_round(record.max_leaves, precision_digits=2) or 0.0
    #
    #             if record.request_unit == "hour":
    #                 name = _("%(name)s (%(time)g remaining out of %(maximum)g hours)", name=record.name,
    #                          time=remaining_time, maximum=maximum)
    #             else:
    #                 name = _("%(name)s (%(time)g remaining out of %(maximum)g days)", name=record.name,
    #                          time=remaining_time, maximum=maximum)
    #         record.display_name = name
    #
