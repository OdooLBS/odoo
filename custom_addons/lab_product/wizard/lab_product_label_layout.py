# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class LabProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'

    print_format = fields.Selection(
        selection_add=[('2x7custom', '2 x 7 for lab products')], 
        ondelete={'2x7custom': 'set default'}
    )

    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if '2x7custom' in self.print_format:
            xml_id = 'lab_product.report_product_template_label_2x7_custom'

        # TODO - dodat logiku za dohvacanje datuma i spremit ju u data

        return xml_id, data