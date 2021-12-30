# -*- coding: utf-8 -*-

{
    'name': 'Import Bom Lines',
    'version': '14.0.1.0.0',
    'summary': "Import bom lines from csv file and create product order.",
    'author': 'Apulia Software srlu <info@apuliasoftware.it>',
    'company': 'Apulia Software srlu',
    'depends': ['base', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'view/bom.xml',
        'wizard/eplan_bom_line.xml',
        'wizard/confirmation_wizard.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
