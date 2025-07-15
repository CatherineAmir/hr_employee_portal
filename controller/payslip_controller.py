
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import fields, http, _
from odoo.osv import expression
from collections import OrderedDict
from odoo.exceptions import AccessError, MissingError


class EmployeePortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(EmployeePortal, self)._prepare_portal_layout_values()

        return values

    def _prepare_home_portal_values(self, counters):

        # counters.append('payslip_count')

        values = super(EmployeePortal, self)._prepare_home_portal_values(counters)
        user_id = request.env.user

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        if 'payslip_count' in counters:
            payslip_count = request.env['hr.payslip'].search_count([('employee_id', '=', employee_id.id),("publish_payslip","=",True)], limit=1)

            values['payslip_count'] = payslip_count
        # if allocat
        # print("values",values)
        return values

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_my_payslips_values(page, sortby, filterby)

        # pager
        pager = values['pager']
        if values['payslips']:
        # content according to pager and archive selected
        #     payslips = values['payslips'][pager['offset']]
            request.session['my_payslips_history'] =values['payslips'].ids[:100]
        # else:
        #     payslips=values['payslips']
        # values.update({
        #     'payslips': payslips,
        #     'pager': pager,
        # })

        return request.render("employee_portal.portal_my_payslips", values)

    def _get_payslip_domain(self):
        return [('state', 'not in', ['draft', 'cancel'])]

    def _prepare_my_payslips_values(self, page, sortby, filterby, domain=None,
                                    url="/my/payslips"):
        # values = self._prepare_portal_layout_values()
        values={}

        Payslips = request.env['hr.payslip']
        user_id = request.env.user

        employee_id = request.env['hr.employee'].sudo().search([('user_id', '=', user_id.id)])

        domain = expression.AND([
            domain or [],
            self._get_payslip_domain(),
        ])
        domain=expression.AND([domain,[('employee_id','=', employee_id.id),("publish_payslip",'=',True)]])

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date_from desc'}}
        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {'all': {'label': _('All'), 'domain': []}}
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        pager = portal_pager(  # vals to define the pager.
            url=url,
            url_args={'sortby': sortby, 'filterby': filterby},
            total=Payslips.search_count(domain) if Payslips.has_access('read') else 0,
            page=page,
            step=self._items_per_page,
        )

        print("pager", pager)
        print("pager", pager['offset'])

        values.update({

            'payslips': Payslips.search(
                domain, order=order, limit=self._items_per_page, offset=pager['offset']),

            'page_name': 'payslips',
            'pager': pager,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,

        })
        return values

    @http.route(['/my/payslips/<int:payslip_id>'], type='http', auth="public", website=True)
    def portal_my_payslip_detail(self, payslip_id, access_token=None, report_type=None, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', payslip_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        # print("access_token",access_token)
        # print("report_type",report_type)
        # print("download",download)
        if report_type == 'pdf' and download and payslip_sudo.state not in ['draft','cancel']:
            # Download the official attachment(s) or a Pro Forma invoice
            docs_data = payslip_sudo._get_payslip_legal_documents_all(allow_fallback=True)
            # print("docs_data",docs_data)
            if len(docs_data) == 1:
                headers = self._get_http_headers(payslip_sudo, report_type, docs_data[0]['content'], download)
                return request.make_response(docs_data[0]['content'], list(headers.items()))
            # else:
    #             filename = invoice_sudo._get_invoice_report_filename(extension='zip')
    #             zip_content = _build_zip_from_data(docs_data)
    #             headers = _get_headers(filename, 'zip', zip_content)
    #             return request.make_response(zip_content, headers)
    #
        elif report_type in ('html', 'pdf', 'text'):
            # has_generated_invoice = bool(payslip.invoice_pdf_report_id)
            # request.update_context(proforma_invoice=not has_generated_invoice)
    #         # Use the template set on the related partner if there is.
    #         # This is not perfect as the invoice can still have been computed with another template, but it's a slight fix/imp for stable.
            pdf_report_name = 'hr_payroll.action_report_payslip'
            # pdf_report_name=payslip_sudo._get_payslip_pdf_report_filename()
            return self._show_report(model=payslip_sudo, report_type=report_type, report_ref=pdf_report_name,
                                     download=download)
    #
        values = self._payslip_get_page_view_values(payslip_sudo, access_token, **kw)
        print("my_details_values", values)

        return request.render("employee_portal.portal_payslip_page", values)


    def _payslip_get_page_view_values(self, payslip, access_token, **kwargs):
        values = {
            'page_name': 'payslip',
            'payslip': payslip,

        }
        return self._get_page_view_values(payslip, access_token, values, 'my_payslip_history', False, **kwargs)