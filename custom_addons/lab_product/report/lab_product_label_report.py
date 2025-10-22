# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models

# TODO - modify
def _prepare_data(env, docids, data):
    return super()._prepare_data(env, docids, data)


class ReportProductTemplateLabel2x7Custom(models.AbstractModel):
    _name = 'report.lab_product.report_producttemplatelabel2x7custom' # TODO - nisam sigurna za ovaj path
    _description = 'Product Label Report 2x7 Custom for Lab Products'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)
