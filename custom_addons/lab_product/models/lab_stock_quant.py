from odoo import models
import json
import logging
import os
import requests

_logger = logging.getLogger(__name__)


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
