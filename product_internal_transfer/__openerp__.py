# To change this template, choose Tools | Templates
# and open the template in the editor.
{
    'name': "Products Import Wizard",
    'version': '0.1',
    'depends': ['base','account','stock',
    ],
    'author': 'Bista Solutions',
    'description': '''Wizard to import Products for internal moves''',
    'data': [
         'wizard/product_internal_transfer_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}