from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime


class LabStockLot(models.Model):
    _inherit = "stock.lot"

    expiration_date = fields.Datetime(
        string="Expiration Date (Unopened)",
        compute="_compute_expiration_date_unopened",
        help="Expiration date from package or label.",
    )

    opened_date = fields.Datetime(
        string="Date Of Opening", 
        store=True, 
        help="Date when the product was opened. Time is not important.",
    )

    expiration_date_after_opening = fields.Datetime(
        string="Expiration Date (Opened)",
        compute="_compute_expiration_date_opened",
        inverse="_inverse_expiration_date_opened",
        store=True,
        readonly=False,
        help="Editable field to allow manual adjustments if necessary. If not set, it will be computed based on the product category's shelf life after opening.",
    )

    @api.depends("product_id")
    def _compute_expiration_date_unopened(self):
        self.expiration_date = False

    @api.depends("expiration_date", "opened_date")
    def _compute_expiration_date_opened(self):
        """
        Compute expiration date after opening based on product category's shelf life after opening.
        If the product category does not have a shelf life defined, the field remains empty.
        """
        for lot in self:
            product_category = lot.product_id.product_tmpl_id.categ_id
            if product_category and product_category.shelf_life_after_opening:
                lot.expiration_date_after_opening = self._calculate_expiration_date(
                    lot.opened_date,
                    product_category.shelf_life_after_opening,
                    lot.expiration_date or None
                )

    def _inverse_expiration_date_opened(self):
        """
        Accept user-entered datetime regardless of category rule.
        Optional validations: not after unopened expiration, not before opened date, etc.
        """
        for lot in self:
            if lot.expiration_date and lot.opened_date and lot.expiration_date_after_opening:
                if lot.expiration_date_after_opening > lot.expiration_date:
                    lot.expiration_date_after_opening = lot.expiration_date
    
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

    def _calculate_expiration_date(self, opened_date, expiration_time, expiration_date=None):
        if opened_date and expiration_time:
            return min(opened_date + datetime.timedelta(days=expiration_time), expiration_date) if expiration_date else opened_date + datetime.timedelta(days=expiration_time)
