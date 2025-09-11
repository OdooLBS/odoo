from datetime import timedelta
from odoo import models, fields, api


class LabStockLot(models.Model):
    _inherit = "stock.lot"

    expiration_date = fields.Datetime(
        string="Expiration Date (Unopened)",
    )

    opened_date = fields.Datetime(
        string="Date Of Opening", 
        store=True, 
    )

    expiration_date_after_opening = fields.Datetime(
        string="Expiration Date (Opened)",
        compute="_compute_expiration_date_opened",
        store=True,
        readonly=False,
        help="Editable field. Syncs with product's opened_date + expiration_time.",
    )

    @api.depends("expiration_date", "opened_date")
    def _compute_expiration_date_opened(self):
        for lot in self:
            lot.expiration_date_after_opening = self._calculate_expiration_date(
                lot.opened_date,
                30,
                lot.expiration_date or None
            )

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
            return min(opened_date + timedelta(days=expiration_time), expiration_date) if expiration_date else opened_date + timedelta(days=expiration_time)
