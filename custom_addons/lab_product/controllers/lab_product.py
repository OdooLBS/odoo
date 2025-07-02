# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, json
import logging
from custom_addons.jwt_auth_api.utils.jwt_auth import jwt_required

_logger = logging.getLogger(__name__)


class LabProduct(http.Controller):

    @http.route(
        "/lab/products/all",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
    def get_full_product_name(self):
        result = request.env["product.template"].get_full_name()
        return request.make_response(
            json.dumps(result, indent=4),
            headers=[("Content-Type", "application/json")],
        )

    @http.route(
        "/lab/products/quantity/all",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
    def get_all_products_quantities(self):
        result = request.env["product.template"].get_all_products()
        return request.make_response(
            json.dumps(result, indent=4),
            headers=[("Content-Type", "application/json")],
        )

    @http.route(
        "/lab/products/quantity/<string:default_code>",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    @jwt_required
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
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    @jwt_required
    def update_product_quantity(self, default_code):
        data = request.get_json_data()
        quantity = data.get("quantity")
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

    @http.route(
        "/lab/products/quantity/update/all",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False,
    )
    @jwt_required
    def update_product_quantity_all(self):
        try:
            data = json.loads(http.request.httprequest.data)
        except Exception:
            return http.request.make_response(
                json.dumps({"error": "Invalid JSON"}),
                headers=[("Content-Type", "application/json")],
                status=400,
            )

        _logger.info(
            f"POST request received on /lab/products/quantity/update/all with payload: {data}"
        )

        products = data.get("products", [])

        results = []
        for product in products:
            default_code = product.get("default_code")
            quantity = product.get("quantity")
            if not default_code or quantity is None:
                results.append(
                    {
                        "default_code": default_code,
                        "status": "error",
                        "message": "Missing default_code or quantity",
                    }
                )
                continue
            try:
                result = http.request.env["product.product"].update_quantity(
                    default_code, quantity
                )
                results.append(
                    {
                        "default_code": default_code,
                        "status": "success",
                        "result": result,
                    }
                )
            except ValueError as e:
                _logger.error(
                    f"Error for product with default code {default_code}: {str(e)}"
                )
                results.append(
                    {"default_code": default_code, "status": "error", "message": str(e)}
                )

        return http.request.make_response(
            json.dumps(results, indent=4),
            headers=[("Content-Type", "application/json")],
            status=200,
        )
