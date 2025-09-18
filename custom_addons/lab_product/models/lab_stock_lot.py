from odoo import models, fields, api
from odoo.exceptions import ValidationError
import datetime

ALERT_DAYS_DEFAULT = 7


class LabStockLot(models.Model):
    _inherit = "stock.lot"

    expiration_date = fields.Datetime(
        string="Expiration Date (Unopened)",
        compute="_compute_expiration_date_unopened",
        help="Expiration date from package or label.",
    )

    use_date = fields.Datetime(compute="_compute_dates")
    removal_date = fields.Datetime(compute="_compute_dates")
    alert_date = fields.Datetime(compute="_compute_dates")

    product_expiry_alert = fields.Boolean(compute="_compute_product_expiry_alert")

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

    @api.depends("product_id", "expiration_date", "expiration_date_after_opening")
    def _compute_dates(self):
        for lot in self:
            if not lot.product_id.use_expiration_date:
                lot.use_date = False
                lot.removal_date = False
                lot.alert_date = False
            elif lot.expiration_date_after_opening:
                lot.use_date = lot.expiration_date_after_opening
                lot.removal_date = lot.expiration_date_after_opening
                lot.alert_date = lot.expiration_date_after_opening - datetime.timedelta(ALERT_DAYS_DEFAULT)
            elif lot.expiration_date:
                lot.use_date = lot.expiration_date
                lot.removal_date = lot.expiration_date
                lot.alert_date = lot.expiration_date - datetime.timedelta(ALERT_DAYS_DEFAULT)
            else:
                lot.use_date = False
                lot.removal_date = False
                lot.alert_date = False

    @api.depends("alert_date")
    def _compute_product_expiry_alert(self):
        for lot in self:
            if lot.alert_date:
                lot.product_expiry_alert = lot.alert_date <= fields.Datetime.now()
            else:
                lot.product_expiry_alert = False

    
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
