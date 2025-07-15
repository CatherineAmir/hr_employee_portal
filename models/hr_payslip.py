from odoo import fields, models, api


class Payslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'portal.mixin', 'mail.thread.main.attachment', 'mail.activity.mixin', 'sequence.mixin',
                'product.catalog.mixin']
    publish_payslip=fields.Boolean(string="Publish Payslip",default=False)

    def _compute_access_url(self):
        super()._compute_access_url()
        for payslip in self:
            payslip.access_url = '/my/payslips/%s' % (payslip.id)

    def _get_payslip_pdf(self):
        """ Generate the Proforma of the invoice.
        :return dict: the payslip's data such as
        {'filename': 'INV_2024_0001_proforma.pdf', 'filetype': 'pdf', 'content': ...}
        """
        self.ensure_one()

        content, report_type = self.env['ir.actions.report']._pre_render_qweb_pdf('hr_payroll.report_payslip_lang',
                                                                                  self.ids,
                                                                                  )
        content_by_id = self.env['ir.actions.report']._get_splitted_report('hr_payroll.report_payslip_lang', content,
                                                                           report_type)

        return {

            'filetype': 'pdf',
            'content': content_by_id[self.id],
        }

    def _get_payslip_pdf_report_filename(self):
        """ Get the filename of the generated  PDF Payslip report. """
        self.ensure_one()
        return f"Payslip-Salary Slip - {self.employee_id.name}- {self.payslip_run_id.name}" ".pdf"

    def _get_payslip_legal_documents_all(self, allow_fallback=False):
        """ Retrieve the invoice legal attachments: PDF, XML, ...
        :param bool allow_fallback: if True, returns a Proforma if the PDF invoice doesn't exist.
        :return list: a list of the attachments data such as
        [{'filename': 'INV_2024_0001.pdf', 'filetype': 'pdf', 'content': ...}, ...]
        """
        return [self._get_payslip_pdf()]

    def _get_report_base_filename(self):
        return self.name


    def publish_payslip_on_website(self):
        for r in self:
            r.publish_payslip=True

    def unpublish_payslip_on_website(self):
        for r in self:
            r.publish_payslip=False
