from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from werkzeug.utils import redirect

from odoo import fields, http, _
from odoo.osv import expression
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError
import pybase64


class EmployeeTimeOffPortal(CustomerPortal):


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user_id = request.env.user

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        if 'payoff_count' in counters:
            payoff_count = request.env['hr.leave'].search_count(
                [('employee_id', '=', employee_id.id)], limit=1)

            values['payoff_count'] = payoff_count
        if "approval_count" in counters:
            employee_ids=request.env['hr.employee'].sudo().search([('time_off_approver', '=', user_id.id)])

            if len(employee_ids) > 0:
                approval_count = request.env['hr.leave'].search_count([('employee_id', 'in', employee_ids.ids)], limit=1)
            else:
                approval_count = 0

            values['approval_count'] = approval_count
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
            filterby = 'to_approve'
        domain += searchbar_filters[filterby]['domain']

        pager = portal_pager(  # vals to define the pager.
            url=url,
            url_args={'sortby': sortby, 'filterby': filterby},
            total=Leave.search_count(domain) if Leave.has_access('read') else 0,
            page=page,
            step=self._items_per_page,
        )
        allocations = request.env['hr.leave.allocation'].sudo().read_group(
            fields=['employee_id', 'number_of_days:sum', 'holiday_status_id'],
            domain=[('employee_id', '=', employee_id.id), ('state', '=', 'validate')], groupby=['holiday_status_id'])

        time_offs_taken = request.env['hr.leave'].sudo().read_group(
            fields=['employee_id', 'holiday_status_id', 'number_of_days:sum',
                    'number_of_hours:sum'],
            domain=[('employee_id', '=', employee_id.id), ('state', '=', 'validate')], groupby=['holiday_status_id'])
        print("allocations",allocations)
        allocation_dict = {}
        for allocation in allocations:
            leave_type_record=request.env['hr.leave.type'].sudo().browse(allocation['holiday_status_id'][0])
            hide_allocation=leave_type_record.hide_allocation_from_user
            allocation_dict[allocation['holiday_status_id'][1]] = {
                'allocated_days': allocation['number_of_days'] if not hide_allocation else 0,
                'consumed_days': 0,
                'consumed_hours': 0,
                'remaining_days': allocation['number_of_days'] if not hide_allocation else 0,
                'img': request.env['hr.leave.type'].sudo().browse(allocation['holiday_status_id'][0]).icon_id.url,
                'request_unit': "day",
                'hide_allocation': hide_allocation,
            }

        for time_off in time_offs_taken:
            index = time_off['holiday_status_id'][1]

            if index in allocation_dict.keys():


                allocation_dict[index]['consumed_days'] = time_off['number_of_days']
                allocation_dict[index]['consumed_hours'] = time_off['number_of_hours']

                allocation_dict[index]['remaining_days'] = allocation_dict[index]['allocated_days'] - \
                                                           allocation_dict[index]['consumed_days']

                allocation_dict[index]['request_unit'] = request.env['hr.leave.type'].sudo().browse(
                    time_off['holiday_status_id'][0]).request_unit
            else:

                allocation_dict[index] = {
                    'allocated_days': 0,
                    'consumed_days': time_off['number_of_days'],
                    'consumed_hours': time_off['number_of_hours'],

                    'remaining_days': 0,
                    'img': request.env['hr.leave.type'].sudo().browse(time_off['holiday_status_id'][0]).icon_id.url,
                    'request_unit': request.env['hr.leave.type'].sudo().browse(
                        time_off['holiday_status_id'][0]).request_unit,
                    'hide_allocation': True,

                }

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

            'allocation_dict': allocation_dict,
        })

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
        contract_id = employee_id.contract_id
        schedule_id=False
        if contract_id:
            schedule_id = contract_id.resource_calendar_id
        start_hour = 0
        end_hour = 0
        if schedule_id:
            work_from = list(sorted(set(schedule_id.attendance_ids.mapped('hour_from'))))
            work_to = list(sorted(set(schedule_id.attendance_ids.mapped('hour_to')), reverse=True))
            start_hour = work_from[0]
            end_hour = work_to[0]
            hours = int(start_hour)
            minutes = int(round((start_hour - hours) * 60))

            # Format as HH:MM string
            start_hour = f"{hours:02d}:{minutes:02d}"

            hours = int(end_hour)
            minutes = int(round((end_hour - hours) * 60))

            # Format as HH:MM string
            end_hour = f"{hours:02d}:{minutes:02d}"

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

            'start_hour': str(start_hour).replace('.', ':') if start_hour else start_hour,
            'end_hour': str(end_hour).replace('.', ':') if end_hour else end_hour,
        }


        return request.render("employee_portal.portal_my_time_offs_create", values)

    @http.route(['/my/timeoffs/create/request'], type='http', auth="user", website=True, methods=['POST'],
                csrf=False)
    def create_timeoff_request(self, **kw):

        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        time_from = float(kw.get('request_time_from', '').replace(':', '.')) if kw.get(
            'request_time_from',
            '') != '' else False

        if time_from:
            time_from_hour = int(time_from) if time_from else False

            time_from_min = round(( time_from-time_from_hour) *100/ 60,2)

            time_from_correct = time_from_hour + time_from_min
        else:
            time_from_correct = 0.0

        time_to = float(kw.get('request_time_to', '').replace(':', '.')) if kw.get(
            'request_time_to',
            '') != '' else False


        if time_to:
            time_to_hour = int(time_to) if time_to else False

            time_to_min = round((time_to - time_to_hour) * 100/60 ,2)

            time_to_correct = time_to_hour + time_to_min

        else:
            time_to_correct = 0.0


        vals = {
            "employee_id": employee_id.id,
            'request_date_from': kw['request_date_from'],

            'holiday_status_id': int(kw['holiday_status_id']),
            'name': kw['description'],
            'request_unit_half': True if kw.get('half_day', False) == 'true' else False,
            'request_unit_hours': True if kw.get('certain_time', False) == 'true' else False,
            'request_hour_from': time_from_correct,
            'request_hour_to': time_to_correct,
            'request_date_from_period': 'am' if kw.get('morning', False) == 'true' else 'pm' if kw.get('afternoon',
                                                                                                     False) == 'on' else False,
        }
        if  kw.get('request_date_to', False):
            vals.update({
                'request_date_to': kw.get('request_date_to', False) if kw.get('request_date_to',
                                                                              False) != '' else False,
            })
        else:
            vals.update({'request_date_to':kw['request_date_from']})


        request_id = request.env['hr.leave'].sudo().with_context({
            'employee_id': employee_id.id,

        }).create(vals)

        # request_id._compute_duration()
        # request_id._compute_duration_display()

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

    @http.route(['/my/approvals', '/my/approvals/page/<int:page>'], type='http', auth="user", website=True)
    def portal_approvals(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_my_approvals_values(page, sortby, filterby)

        request.session['approvals_history'] = values['approvals'].ids[:100]


        return request.render("employee_portal.portal_my_approvals", values)

    def _prepare_my_approvals_values(self, page, sortby, filterby, domain=None,
                                    url="/my/approvals"):

        values = {}
        Leave = request.env['hr.leave']
        user_id = request.env.user
        employee_ids = request.env['hr.employee'].sudo().search([('time_off_approver', '=', user_id.id)])


        domain = expression.AND([domain or [], [('employee_id', 'in',  employee_ids.ids)]])
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
            'to_approve': {'label': _('To Approve'), 'domain': [("state", 'in', ['confirm',])]},
            'refuse': {'label': _('Refuse'), 'domain': [("state", '=', 'refuse')]},
            'second_approval':{'label':_('Second Approval'), 'domain': [("state", '=', 'validate1')]},
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

            'approvals': Leave.sudo().search(
                domain, order=order, limit=self._items_per_page, offset=pager['offset']),

            'page_name': 'approvals',
            'pager': pager,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,


        })

        return values

    @http.route(['/my/approvals/approve/<int:id>'], type='http', auth="user", website=True)
    def approve_approvals(self, id=0, **kw):
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        leave_id = request.env["hr.leave"].browse(id)

        if leave_id:
            leave_id.sudo().write({
                'state': 'validate1'
            })

        return redirect('/my/approvals')


    @http.route(['/my/approvals/refuse/<int:id>'], type='http', auth="user", website=True)
    def refuse_approvals(self, id=0, **kw):
        user_id = request.env.user
        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])
        leave_id = request.env["hr.leave"].browse(id)
        if leave_id:
            leave_id.sudo().write({
                'state': 'refuse'
            })

        return redirect('/my/approvals')