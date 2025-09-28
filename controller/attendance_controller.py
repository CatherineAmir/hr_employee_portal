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
            attendance_count = request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee_id.id), ("in_mode", "!=", "technical")])
            values['attendance_count'] = attendance_count
        return values

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendance(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_my_attendance_values(page=page, sortby=sortby, filterby=filterby)
        # request.session['attendance_history'] = values['attendance'][:100]
        return request.render("employee_portal.portal_my_attendance", values)

    def _prepare_my_attendance_values(self, page, sortby, filterby, url="/my/attendance"):

        values = {}

        Attendance = request.env['hr.attendance']
        user_id = request.env.user

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        domain = expression.AND([[], [('employee_id', '=', employee_id.id)]])
        searchbar_sortings = {
            'date': {'label': _('Date Desc'), 'order': 'check_in desc'},
            # 'date_2': {'label': _('Date Asc'), 'order': 'check_in'},

        }

        # default sort by order
        if not sortby:
            sortby = 'date'

        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},

        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']
        all_dates = Attendance.sudo().search(domain).mapped("check_in")
        print("all_dates", all_dates)

        if not all_dates:
            return {"pager": {}, "attendance": []}

        period_starts = []
        seen_dates = set()
        for dt in sorted(all_dates):

            start, end = self._custom_month_range(dt)
            # print("start",start)

            if start not in seen_dates:
                seen_dates.add((start,end))
                period_starts.append(start)

        seen = sorted(set(seen_dates), key=lambda t: t[0], reverse=True)
        # print("seen",seen)
        total_months = len(seen)

        # print("total_months", total_months)

        page = max(1, min(page, total_months))
        month_start = list(seen)[page - 1][0]
        # print("month_start",month_start)



        month_end = list(seen)[page - 1][1]
        # print("month_end", month_end)

        month_domain = expression.AND([domain, [
            ('check_in', '>=', month_start),
            ('check_in', '<', month_end),
        ]])

        domain_calculated = expression.AND([domain, month_domain])

        total_count = Attendance.sudo().read_group(domain=domain,fields=['__count'],groupby=['check_in:day'])
        # print("total_count",total_count)
        # print("len(total_count)",len(total_count))
        pager = portal_pager(
            page=page,
            url=url,
            url_args={'sortby': sortby, 'filterby': filterby},
            total=len(seen)*31,
            step=31,

        )

        attendance = Attendance.sudo().read_group(
            fields=["in_mode", "worked_hours", "not_calculated_hours"],
            domain=domain_calculated, orderby="check_in desc",
            groupby=['check_in:day', "in_mode", "not_calculated_hours", "is_leave"], lazy=False),

        total_hours = round(sum(
            round(attendance[0][i]["worked_hours"], 2) if not attendance[0][i]['not_calculated_hours'] else 0 for i in
            range(0, len(attendance[0]))), 2)

        values.update({
            'attendance': attendance,
            'page_name': 'attendance',
            'pager': pager,
            'default_url': url,

            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),

            'searchbar_sortings': searchbar_sortings,

            'filterby': filterby,
            'month_start': month_start.date().strftime('%d %B %Y'),

            'month_end': (month_end.date()-timedelta(days=1)).strftime('%d %B %Y'),
            'total_hours': total_hours,

        })



        print("values",values)
        return values

    def _custom_month_range(self, ref_date):
        """
        Returns start and end datetime for the custom month
        starting on the 21st of one month and ending on the 20th of the next.
        """
        if ref_date.day >= 21:
            start = ref_date.replace(day=21).date()

        else:
            start = ((ref_date - relativedelta(months=1)).replace(day=21)).date()

        end = (start + relativedelta(months=1))

        return fields.Datetime.to_datetime(start), fields.Datetime.to_datetime(end)
