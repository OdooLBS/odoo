from odoo import models, fields, api
import logging

#from ..scripts.sync import sync_erp_to_lims

_logger = logging.getLogger(__name__)


class LabProductTemplate(models.Model):
    _inherit = "product.template"

    _sql_constraints = [
        (
            "default_code_uniq",
            "unique(default_code)",
            "Internal Reference must be unique.",
        )
    ]

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "default_code" in fields_list:
            defaults["default_code"] = self._get_default_code()
        return defaults

    sale_ok = fields.Boolean(default=False)
    use_expiration_date = fields.Boolean(default=True)
    default_code = fields.Char(
        string="Internal Reference",
        copy=False,
        index=True,
    )
    CAS_number = fields.Char(string="CAS Number")
    weight_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Weight Unit",
        domain="[('category_id.name', '=', 'Weight')]",
    )
    volume_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Volume Unit",
        domain="[('category_id.name', '=', 'Volume')]",
    )
    list_price = fields.Float(
        string="Sales Price", 
        default=0.0,
        digits="Product Price",
        tracking=True,
        help="Price at which the product is sold to customers.",
    )

    @api.model
    def create(self, vals):
        if not vals.get("default_code"):
            vals["default_code"] = self._get_default_code()
        return super().create(vals)

    @api.model
    def get_full_name(self):
        """ Get a list of all products with their default codes and names. """
        products = self._get_products()
        return [f"[{p.default_code}] {p.name}" for p in products]

    @api.model
    def get_all_products(self):
        """ Get a list of all products with their default codes, names, and quantities. """
        products = self._get_products()

        _logger.info("Get data for all products")

        return [
            {
                "default_code": p.default_code,
                "name": p.name,
                "quantity": p.qty_available,
            }
            for p in products
        ]

    """
    def sync_with_lims(self):
        all_data = self.get_all_products()
        lims_response = sync_erp_to_lims(all_data)
        if lims_response:
            _logger.info("Sync successful")

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Sinkronizacija završena",
                    "message": "Proizvodi su uspješno sinkronizirani s LIMS-om.",
                    "sticky": False,
                    "type": "success",
                },
            }
        else:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Greška pri sinkronizaciji",
                    "message": "Došlo je do greške prilikom sinkronizacije s LIMS-om. Provjerite logove za detalje.",
                    "sticky": True,
                    "type": "danger",
                },
            }
    """

    def _get_default_code(self):
        """ Generate a new default code using a sequence."""
        code = self.env["ir.sequence"].next_by_code("product.template.default_code")
        if not code:
            raise ValueError("No sequence found for product.template.default_code")
        return code

    def _get_products(self):
        """ Retrieve all products ordered by their default code."""
        return self.search([], order="default_code ASC")
