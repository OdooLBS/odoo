from odoo import fields, models, _


class LabProductCategory(models.Model):
    _inherit = "product.category"

    shelf_life_after_opening = fields.Integer(
        string="Shelf Life After Opening (days)",  
        store=True,
        help="Number of days the product remains usable after opening.",
    )