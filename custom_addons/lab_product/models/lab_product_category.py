from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class LabProductCategory(models.Model):
    _inherit = "product.category"

    shelf_life_after_opening = fields.Integer(
        string="Shelf Life After Opening (days)",  
        store=True,
        help="Number of days the product remains usable after opening.",
    )