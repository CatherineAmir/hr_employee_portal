# -*- coding: utf-8 -*-
{
    'name': 'Employee Portal',
    'version': '1.0',
    'summary': 'Brief description of the module',
    'description': '''
        Detailed description of the module
    ''',
    'category': 'Uncategorized',
    'author': 'SITA-EGYPT',
    'company': 'SITA-EGYPT',
    'maintainer': 'SITA-EGYPT',
    'website': 'https://sita-eg.com',
    'depends': ['base', 'mail','hr','hr_payroll','hr_work_entry','account','portal','hr_holidays',"attendance_rule"],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_payslip.xml',
        'templates/employee_portal_payslip.xml',
        'templates/attendance_portal.xml',
        'templates/time_off_portal.xml',
        'views/hr_leave.xml',
        'views/hr_leave_type.xml',
    ],
    "assets":{
        'web.assets_frontend': [
           'employee_portal/static/src/js/employee_portal.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}