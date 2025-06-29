from odoo import models, api
import json
import logging

logging.basicConfig(
    filename="custom_addons/lab_product/scripts/logs/send_to_lims.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


class LabStockQuant(models.Model):
    _inherit = "stock.quant"

    def write(self, vals):
        res = super().write(vals)
        if "quantity" in vals:
            for record in self:
                record._sync_with_lims_stock_quant(vals["quantity"])
        return res

    def _sync_with_lims_stock_quant(self, new_quantity):

        data = {
            "product_id": self.product_tmpl_id.default_code,
            "quantity": new_quantity,
        }

        try:
            # todo salji na lims api post
            with open(
                "custom_addons/lab_product/scripts/output/send_to_lims.json",
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logging.info(
                "Podaci uspješno dohvaćeni i zapisani u /custom_addons/lab_product/scripts/output/send_to_lims.json"  # todo ne pise
            )
        except Exception as e:
            logging.error(f"Greška pri dohvaćanju ili zapisivanju podataka: {e}")
            print(f"Došlo je do greške: {e}")
