# -*- coding: utf-8 -*-
{
    "name": "Lab Product",
    "summary": "This module inherits the product.product model to add logic for custom laboratory products.",
    "description": """
Long description of module's purpose # todo
    """,
    "author": "Nina",
    # 'website': "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Sales/Sales",
    "version": "1.0",
    # any module necessary for this one to work correctly
    "depends": ["base", "product", "account", "stock", "sale", "purchase"],
    # always loaded
    "data": [
        # 'security/ir.model.access.csv',
        "views/lab_product_template_view.xml",
        "views/lab_stock_production_lot_view.xml",
        "data/ir_sequence.xml",
        "data/lab_product_categories.xml",
    ],
    "demo": [
        # "demo/lot_template.csv",
        # "demo/product_template.csv",
    ],
    # "post_init_hook": "_lab_product_init_hook",
    # "pre_init_hook": "_lab_product_pre_init_settings",
    "installable": True,
    "license": "LGPL-3",
}
