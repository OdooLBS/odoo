from odoo import models
import json
import logging

from odoo import api, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class LabStockQuant(models.Model):
    _inherit = "stock.quant"

    qty_used = fields.Float(string="Quantity Used")

    @api.onchange('qty_used')
    def _onchange_qty_used_propose_counted(self):
        for q in self:
            used = q.qty_used or 0.0
            q.inventory_quantity_set = True
            q.inventory_quantity = max(0.0, (q.quantity or 0.0) - used)

            _logger.debug(f"Inventor quantity changed to: {q.inventory_quantity}")

    def write(self, vals):
        _logger.debug(f"LabStockQuant write vals: {vals}") 

        if (self.env.context.get('lab_skip_apply')):
            return super().write(vals)

        if 'qty_used' in vals:
            for q in self:
                used = vals.get('qty_used', q.qty_used) or 0.0
                counted = max(0.0, (q.quantity or 0.0) - used)
                _logger.debug(f"Auto setting inventory_quantity to {counted} for quant id {q.id}")
                super().write({
                     'inventory_quantity': counted,
                     'inventory_quantity_set': True,
                })
                if vals.get('qty_used') != 0.0:
                    _logger.debug(f"Resetting qty_used to 0.0 for quant id {q.id}")
                    vals['qty_used'] = 0.0
                
            quants = self.sudo().with_context(prefetch_fields=False).browse(self.ids)
            to_apply = quants.filtered(lambda q:
                q.product_id and q.location_id and q.inventory_quantity is not None # dodat lot
            ) 
            if to_apply:
                _logger.debug(f"Applying inventory for quants: {to_apply.ids}")
                ctx = dict(self.env.context, lab_skip_apply=True)
                to_apply.with_context(ctx).action_apply_inventory()

        res = super().write(vals)
        return res

"""
    def _sync_with_lims_stock_quant(self, new_quantity):

        data = {
            "default_code": self.product_tmpl_id.default_code,
            "quantity": new_quantity,
        }

        try:
            # fix predaja
            with open(
                "custom_addons/lab_product/scripts/output/send_to_lims.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            lims_url = "https://mlims.com/api/erp/products/quantity/update"

            _logger.info(f"Call {lims_url}")
            _logger.info(f"Response from LIMS: update done")

            # fix predaja
            # lims_token = os.environ.get("LIMS_BEARER_TOKEN")
            # lims_headers = {
            #    "Authorization": f"Bearer {lims_token}",
            #    "Content-Type": "application/json",
            # }

            # lims_url = "https://mlims.com/api/erp/products/quantity/update"

            # _logger.info(f"Call {lims_url}")

            # lims_response = requests.post(url=lims_url, headers=lims_headers, json=data)

            # lims_response.raise_for_status()
            # _logger.info(f"Response from LIMS: {lims_response}")

            # lims_resp_json = lims_response.json()

            # with open(
            #    "custom_addons/lab_product/scripts/output/lims_response.json",
            #    "w",
            #    encoding="utf-8",
            # ) as f:
            #    json.dump(lims_resp_json, f, ensure_ascii=False, indent=2)

            # logging.info(f"LIMS response: {lims_resp_json}")
        except Exception as e:
            logging.error(f"Greška pri dohvaćanju ili zapisivanju podataka: {e}")
            print(f"Došlo je do greške: {e}")
"""