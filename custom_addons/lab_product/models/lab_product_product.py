from odoo import models, api
import logging

from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)


class LabProductProduct(models.Model):
    _inherit = "product.product"

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

    default_code = fields.Char(
        string="Internal Reference",
        copy=False,
        index=True,
    )

    @api.model
    def create(self, vals):
        if not vals.get("default_code"):
            vals["default_code"] = self._get_default_code()
        return super().create(vals)

    @api.model
    def get_product_quantity(self, default_code):
        """
        Retrieve the quantity of a product based on its default code.

        :param default_code: The internal reference of the product.
        :return: A dictionary with product reference and its quantity.
        """
        product = self._get_product_by_default_code(default_code)
        if not product:
            raise ValueError(f"Product with default code {default_code} not found.")

        return self._product_quantity_response(product)

    @api.model
    def update_quantity(self, default_code, quantity):
        """
        Update the quantity of a product based on its default code.

        :param default_code: The internal reference of the product.
        :param quantity: The new quantity to set.
        """
        product = self._get_product_by_default_code(default_code)
        if not product:
            raise ValueError(f"Product with default code {default_code} not found.")

        warehouse = self._get_company_warehouse()
        if not warehouse:
            raise ValueError("No warehouse found for the current company.")

        stock_lot = self._get_stock_lot(default_code)

        self.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "lot_id": stock_lot.id,
                "location_id": warehouse.lot_stock_id.id,
                "inventory_quantity": quantity,
            }
        )._apply_inventory()

        _logger.info(
            f"Quantity for product with default code {default_code} update successfully."
        )

        return {
            "message": f"Quantity for product with default code {default_code} update successfully.",
        }

    def _get_product_by_default_code(self, default_code):
        """
        Retrieve product by their default code.

        :param default_code: Product default code.
        :return: Product record or None if not found.
        """
        return self.search([("default_code", "=", default_code)], limit=1)

    def _get_company_warehouse(self):
        """
        Get the warehouse for the current company.

        :return: Warehouse record or None if not found.
        """
        return self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

    def _get_stock_lot(self, default_code):
        """
        Retrieve stock lot by product's default code.

        :param default_code: Product default code.
        :return: Stock lot record or None if not found.
        """
        return self.env["stock.lot"].search([("ref", "=", default_code)], limit=1)

    def _product_quantity_response(self, product):
        """
        Prepare the response for product quantity.

        :param product: Product record.
        :return: Dictionary with product details.
        """
        return {
            "reference": product.default_code,
            "name": product.product_tmpl_id.name,
            "quantity": product.qty_available,
            "weight_uom": product.product_tmpl_id.weight_uom_id.name,
            "volume_uom": product.product_tmpl_id.volume_uom_id.name,
        }

    def _get_default_code(self):
        code = self.env["ir.sequence"].next_by_code("product.template.default_code") # product.template.default_code zato da ostane sljedivost 
        if not code:
            raise ValueError("No sequence found for product.product.default_code")
        return code