from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from werkzeug.utils import redirect

from odoo import fields, http, _
from odoo.osv import expression
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError
import pybase64


class EmployeeTimeOffPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(EmployeeTimeOffPortal, self)._prepare_portal_layout_values()

        return values

    def _prepare_home_portal_values(self, counters):
        values = super(EmployeeTimeOffPortal, self)._prepare_home_portal_values(counters)
        user_id = request.env.user
        print("counters", counters)
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        if 'payoff_count' in counters:
            payoff_count = request.env['hr.leave'].search_count(
                [('employee_id', '=', employee_id.id)], limit=1)

            values['payoff_count'] = payoff_count
        print("values", values)
        return values

    def _get_time_off_domain(self):
        return []

    @http.route(['/my/timeoffs', '/my/timeoffs/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_time_offs(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_my_time_off_values(page, sortby, filterby)
        request.session['timeoffs_history'] = values['timeoffs'].ids[:100]
        return request.render("employee_portal.portal_my_time_offs", values)

    def _prepare_my_time_off_values(self, page, sortby, filterby, domain=None,
                                    url="/my/timeoffs"):

        values = {}
        Leave = request.env['hr.leave']
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        domain = expression.AND([
            domain or [],
            self._get_time_off_domain(),
        ])
        domain = expression.AND([domain, [('employee_id', '=', employee_id.id)]])
        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'request_date_from desc'},
            'last_update': {'label': _('Last Update'), 'order': 'write_date desc'},
        }
        # default sort by order
        if not sortby:
            sortby = 'last_update'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'to_approve': {'label': _('To Approve'), 'domain': [("state", 'in', ['confirm', 'validate1'])]},
            'refuse': {'label': _('Refuse'), 'domain': [("state", '=', 'refuse')]},
            'approved': {'label': _('Approved'), 'domain': [("state", '=', 'validate')]},
            'cancellation_request': {'label': _('Cancellation Request'),
                                     'domain': [("state", '=', 'cancellation_request')]},
            'cancel': {'label': _('Cancelled'), 'domain': [("state", '=', 'cancel')]},

        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        pager = portal_pager(  # vals to define the pager.
            url=url,
            url_args={'sortby': sortby, 'filterby': filterby},
            total=Leave.search_count(domain) if Leave.has_access('read') else 0,
            page=page,
            step=self._items_per_page,
        )

        values.update({

            'timeoffs': Leave.search(
                domain, order=order, limit=self._items_per_page, offset=pager['offset']),

            'page_name': 'timeoffs',
            'pager': pager,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,

        })
        print("values first", values)
        return values

    @http.route(['/my/timeoffs/delete/<int:id>'], type='http', auth="user", website=True)
    def portal_offs_delete(self, id=0, **kw):
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        leave_id = request.env["hr.leave"].browse(id)
        if leave_id.employee_id.id == employee_id.id:
            leave_id.unlink()
        return redirect('/my/timeoffs')

    @http.route(['/my/timeoffs/cancel/<int:id>'], type='http', auth="user", website=True)
    def portal_offs_cancel(self, id=0, **kw):
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        leave_id = request.env["hr.leave"].browse(id)
        if leave_id.employee_id.id == employee_id.id:
            leave_id.sudo().write({
                'state': 'cancellation_request'
            })

        return redirect('/my/timeoffs')

    @http.route(['/my/timeoffs/create/'], type='http', auth="user", website=True)
    def create_timeoff(self, **kw):
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        context = {
            'employee_id': employee_id.id,
        }
        employee_company_id = employee_id.company_id

        domain = [
            ('company_id', 'in', [employee_company_id.id, False]),
            '|',
            ('requires_allocation', '=', 'no'),
            ('has_valid_allocation', '=', True),
        ]
        leave_type = request.env["hr.leave.type"].sudo().with_context(context).search(domain)
        values = {
            "employee_id": employee_id,
            'leave_types': leave_type,
            'page_name': 'create_timeoff_request',

        }

        return request.render("employee_portal.portal_my_time_offs_create", values)

    @http.route(['/my/timeoffs/create/request'], type='http', auth="user", website=True, methods=['POST'], csrf=False)
    def create_timeoff_request(self, **kw):
        print("kw", kw)
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        request_id = request_id = request.env['hr.leave'].sudo().with_context({
            'employee_id': employee_id.id,
        }).create({
            "employee_id": employee_id.id,
            'request_date_from': kw['request_date_from'],
            'request_date_to': kw['request_date_to'],
            'holiday_status_id': int(kw['holiday_status_id']),
            'name': kw['description'],
        })

        file = kw.get('document_attachment', False)
        if file:
            name = kw.get('document_attachment').filename
            Attachments = request.env['ir.attachment']
            file = kw.get('document_attachment', False)
            attachment_id = Attachments.sudo().create({
                'name': name,
                'res_name': name,
                'type': 'binary',
                'res_model': "hr.leave",
                'res_id': request_id.id,
                'datas': pybase64.b64encode(file.read()),
            })

        return redirect('/my/timeoffs')
