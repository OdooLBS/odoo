from odoo import http
from odoo.http import request, json

#from jwt_auth_api.utils.jwt_auth import jwt_required


class LabStockLot(http.Controller):

    @http.route(
        "/lab/stock_lots",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False,
    )
    #@jwt_required
    def get_stock_lots(self):
        try:
            result = request.env["stock.lot"].get_stock_lots()
            return request.make_response(
                json.dumps(result, indent=4),
                headers=[("Content-Type", "application/json")],
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
