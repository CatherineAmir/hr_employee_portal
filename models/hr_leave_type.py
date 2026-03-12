# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from odoo.tools.float_utils import float_round


class HrLeaveType(models.Model):
    """ This model represents hr.leave.type."""
    _inherit = 'hr.leave.type'

    hide_allocation_from_user=fields.Boolean(string="Hide allocation from user",default=False)


    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """ fields_get([allfields][, attributes])

        Return the definition of each field.

        The returned value is a dictionary (indexed by field name) of
        dictionaries. The _inherits'd fields are included. The string, help,
        and selection (if present) attributes are translated.

        :param list allfields: fields to document, all if empty or not provided
        :param list attributes: attributes to return for each field, all if empty or not provided
        :return: dictionary mapping field names to a dictionary mapping attributes to values.
        :rtype: dict
        """
        res = super().fields_get(allfields=allfields, attributes=attributes)

        for field in res.keys():

            if self.env.user.has_group("hr_egypt.group_general_manager"):
                res[field]["readonly"] = True

        return res