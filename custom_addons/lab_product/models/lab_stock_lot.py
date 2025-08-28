from datetime import timedelta
from odoo import models, fields, api
import logging

from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class LabStockLot(models.Model):
    _inherit = "stock.lot"

    expiration_date = fields.Datetime(
        string="Expiration Date",
        compute="_compute_expiration_date",
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

    @api.model
    def create(self, vals):

        if vals.get("product_id") and vals["expiration_date"]:
            product_template = (
                self.env["product.product"].browse(vals["product_id"]).product_tmpl_id
            )
            if product_template.opened_date:
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
        if self.env.context.get('from_template_recompute'):
            return super().write(vals)

        for lot in self:
            if vals.get("expiration_date"):
                product_template = lot.product_id.product_tmpl_id
                if product_template.opened_date:
                    # dont set expiration_date to new value if opened_date is set, and use calculation instead
                    raise UserError(
                        "Cannot set expiration date directly when date of opening is set."
                    )
        return super().write(vals)

    def _calculate_expiration_date(self, opened_date, expiration_time):
        if opened_date and expiration_time:
            return opened_date + timedelta(days=expiration_time)
