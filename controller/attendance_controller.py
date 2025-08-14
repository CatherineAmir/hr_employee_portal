import json
from datetime import timedelta

from odoo import http
from odoo.http import request
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from werkzeug.utils import redirect

from odoo import fields, http, _
from odoo.osv import expression
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError

from dateutil.relativedelta import relativedelta

class ModelName(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user_id = request.env.user

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        if 'attendance_count' in counters:
            attendance_count=request.env['hr.attendance'].sudo().search([('employee_id', '=', employee_id.id),("check_in","!=","technical")])
            values['attendance_count'] = attendance_count
        return values

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendance(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_my_attendance_values(page, sortby, filterby)
        request.session['attendance_history'] = values['attendance'][:100]
        # return request.render("employee_portal.portal_my_time_offs", values)

    def _prepare_my_attendance_values(self, sortby, filterby, domain=None, page=1,
                                     url="/my/attendance"):

        values = {}

        attendance=request.env['hr.attendance']
        user_id = request.env.user

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        domain = expression.AND([domain or [], [('employee_id', '=', employee_id.id),("in_mode","!=","technical")]])
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'check_in desc'},

        }
        # default sort by order
        if not sortby:
            sortby = 'date'
        # order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'to_approve': {'label': _('To Approve'), 'domain': [("state", 'in', ['confirm', ])]},
            'refuse': {'label': _('Refuse'), 'domain': [("state", '=', 'refuse')]},
            'second_approval': {'label': _('Second Approval'), 'domain': [("state", '=', 'validate1')]},
            'approved': {'label': _('Approved'), 'domain': [("state", '=', 'validate')]},
            'cancellation_request': {'label': _('Cancellation Request'),
                                     'domain': [("state", '=', 'cancellation_request')]},
            'cancel': {'label': _('Cancelled'), 'domain': [("state", '=', 'cancel')]},

        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        all_dates=attendance.sudo().search(domain).mapped("check_in")
        print("all_dates",all_dates)
        if not all_dates:
            return {"pager":{},"attendance":[]}

        period_starts=[]
        seen=set()
        for dt in sorted(all_dates):
            print("dt",dt)
            start,z=self._custom_month_range(dt)
            print("start",z)
            print("end",dt)
            if start not in seen:
                seen.add(start)
                period_starts.append(start)
        print("period_starts",period_starts)
        total_months = len(period_starts)
        page = max(1, min(page, total_months))
        month_start = period_starts[page - 1]
        month_end = month_start + relativedelta(months=1)
        month_domain = expression.AND([domain, [
            ('check_in', '>=', month_start),
            ('check_in', '<', month_end),
        ]])
        print("month_start",month_start)
        print("month_domain",month_domain)
        print("month_end",month_end)
        domain_calculated=expression.AND([domain,month_domain,[("not_calculated_hours","=",False)]])
        print("domain_calculated",domain_calculated)
        attendance=attendance.sudo().read_group(
            fields=["in_mode", "worked_hours", "not_calculated_hours"],
            domain=domain_calculated, limit=self._items_per_page, orderby="check_in desc",
            groupby=['check_in:day',"in_mode"], lazy=False),

        pager = {
            'total': total_months,
            'page': page,
            'has_prev': page > 1,
            'has_next': page < total_months,
            'prev': page - 1 if page > 1 else None,
            'next': page + 1 if page < total_months else None,
            'labels': [
                f"{start.strftime('%d %b %Y')} → {(start + relativedelta(months=1) - timedelta(days=1)).strftime('%d %b %Y')}"
                for start in period_starts]
        }
        print("attendance",attendance)

        values.update({
            # attendance.sudo().read_group(
            #     fields=["in_mode", "worked_hours", "not_calculated_hours"],
            #     domain=domain, limit=self._items_per_page, offset=pager['offset'],
            #     groupby=['check_in:month', "check_in:day"], lazy=False),

            'attendance':attendance,
            'page_name': 'attendance',
            'pager': pager,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'month_start': month_start,
            'month_end': month_end,

        })

        print("values",values)

        return values

    def _custom_month_range(self,ref_date):
        """
        Returns start and end datetime for the custom month
        starting on the 21st of one month and ending on the 20th of the next.
        """
        if ref_date.day >= 21:
            start = ref_date.replace(day=21)
        else:
            start = (ref_date - relativedelta(months=1)).replace(day=21)
        end = start + relativedelta(months=1)
        return fields.Datetime.to_datetime(start), fields.Datetime.to_datetime(end)