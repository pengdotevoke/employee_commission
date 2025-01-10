{
    'name': 'Employee Commission',
    'version': '1.0',
    'author': 'James Otieno',
    'depends': ['sale', 'point_of_sale', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_commission_menu.xml',
        'views/employee_commission_search.xml',
        'views/employee_commission_tree.xml',
        'views/employee_commission_form.xml',
        'views/employee_commission_views.xml',
    ],
    'installable': True,
    'application': True,
}
