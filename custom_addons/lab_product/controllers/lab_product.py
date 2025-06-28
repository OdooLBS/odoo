# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, json
import logging

_logger = logging.getLogger(__name__)


class LabProduct(http.Controller):

    @http.route(
        "/lab/products/full_name",
        type="http",
        auth="bearer",
        methods=["GET"],
        csrf=False,
    )
    def get_full_product_name(self):
        result = request.env["product.template"].get_full_name()
        return request.make_response(
            json.dumps(result, indent=4),
            headers=[("Content-Type", "application/json")],
        )

    @http.route(
        "/lab/products/quantity/<string:default_code>",
        type="http",
        auth="bearer",
        methods=["GET"],
        csrf=False,
    )
    def get_product_quantity(self, default_code):
        try:
            result = request.env["product.product"].get_product_quantity(default_code)

            return request.make_response(
                json.dumps(result, indent=4),
                headers=[("Content-Type", "application/json")],
                status=200,
            )
        except ValueError as e:
            return request.make_response(
                json.dumps(
                    {"error": str(e)},
                    indent=4,
                ),
                headers=[("Content-Type", "application/json")],
                status=404,
            )

    @http.route(
        "/lab/products/quantity/<string:default_code>/update",
        type="http",
        auth="bearer",
        methods=["POST"],
        csrf=False,
    )
    def update_product_quantity(self, default_code):
        quantity = request.params.get("quantity")
        if not quantity:
            return request.make_response(
                json.dumps({"error": "Quantity is required"}),
                headers=[("Content-Type", "application/json")],
                status=404,
            )

        _logger.debug(
            f"Updating quantity for product {default_code} with new quantity {quantity}"
        )
        try:
            result = request.env["product.product"].update_quantity(
                default_code, quantity
            )
            return request.make_response(
                json.dumps(result, indent=4),
                headers=[("Content-Type", "application/json")],
                status=200,
            )
        except ValueError as e:
            return request.make_response(
                json.dumps(
                    {"error": str(e)},
                    indent=4,
                ),
                headers=[("Content-Type", "application/json")],
                status=404,
            )
