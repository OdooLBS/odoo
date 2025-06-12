# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api


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
    opened_date = fields.Date(string="Date Of Opening")
    expiration_date_computed = fields.Date(
        string="Expiration Date", compute="_compute_expiration_date"
    )

    @api.model
    def create(self, vals):
        if not vals.get("default_code"):
            vals["default_code"] = self._get_default_code()
        return super().create(vals)

    @api.model
    def get_full_name(self):
        products = self._get_product_by_default_code()
        return [f"[{p.default_code}] {p.name}" for p in products]

    def _compute_expiration_date(self):
        for rec in self:
            if rec.opened_date and rec.expiration_time:
                expiration_date = rec.opened_date + timedelta(days=rec.expiration_time)
                rec.expiration_date_computed = expiration_date

                lots = self.env["stock.lot"].search(
                    [("product_id.product_tmpl_id", "=", rec.id)]
                )
                lots.write({"expiration_date": expiration_date})

            else:
                lots = self.env["stock.lot"].search(
                    [("product_id.product_tmpl_id", "=", rec.id)]
                )
                lot_expiration = next(
                    (lot.expiration_date for lot in lots if lot.expiration_date), None
                )
                rec.expiration_date_computed = lot_expiration or False

    def _get_default_code(self):
        code = self.env["ir.sequence"].next_by_code("product.template.default_code")
        if not code:
            raise ValueError("No sequence found for product.template.default_code")
        return code

    def _get_product_by_default_code(self):
        """
        Retrieve product by their default code.

        :param default_code: Product default code.
        :return: Product record or None if not found.
        """
        return self.search([], order="default_code ASC")
