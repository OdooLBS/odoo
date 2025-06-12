from datetime import timedelta, datetime
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LabStockLot(models.Model):
    _inherit = "stock.lot"

    expiration_date = fields.Datetime(
        string="Expiration Date",
        compute="_compute_expiration_date",
        inverse="_inverse_expiration_date",
        store=True,
        readonly=False,
        help="Editable field. Syncs with product's opened_date + expiration_time.",
    )

    @api.depends("product_id")
    def _compute_expiration_date(self):
        for lot in self:
            product_template = lot.product_id.product_tmpl_id
            if product_template.opened_date and product_template.expiration_time:
                lot.expiration_date = self._calculate_expiration_date(
                    product_template.opened_date,
                    product_template.expiration_time,
                )
            else:
                lot.expiration_date = False

    def _inverse_expiration_date(self):
        for lot in self:
            product_template = lot.product_id.product_tmpl_id
            if (
                product_template
                and product_template.opened_date
                and lot.expiration_date
            ):
                try:
                    new_exp_time = (
                        lot.expiration_date.date() - product_template.opened_date
                    ).days
                    if product_template.expiration_time != new_exp_time:
                        product_template.expiration_time = new_exp_time
                        _logger.info(
                            f"[INVERSE] Updated product expiration_time to {new_exp_time}"
                        )
                except Exception as e:
                    _logger.error(f"[INVERSE ERROR] {e}")

    @api.model
    def create(self, vals):
        if not vals.get("expiration_date") and vals.get("product_id"):
            product_template = (
                self.env["product.product"].browse(vals["product_id"]).product_tmpl_id
            )
            vals["expiration_date"] = self._calculate_expiration_date(
                product_template.opened_date, product_template.expiration_time
            )

        return super().create(vals)

    @api.model
    def get_stock_lots(self):
        """
        Retrieve all stock lots with their reference, lot number, and expiration date.
        :return: List of dictionaries containing stock lot details.
        """
        stock_lots = self.search([], order="ref ASC")
        result = [
            {
                "id": lot.id,
                "reference": lot.ref,
                "lot_number": lot.name,
            }
            for lot in stock_lots
        ]
        return result

    def write(self, vals):
        res = super().write(vals)
        if "expiration_date" in vals:
            self._inverse_expiration_date()
        return res

    def _calculate_expiration_date(self, oepened_date, expiration_time):
        if oepened_date and expiration_time:
            return oepened_date + timedelta(days=expiration_time)
