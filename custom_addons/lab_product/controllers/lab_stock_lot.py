from odoo import http
from odoo.http import request, json


class LabStockLot(http.Controller):

    @http.route(
        "/lab/stock_lots",
        type="http",
        auth="public",
        methods=["GET"],
        csrf=False,
    )
    def get_stock_lots(self):
        result = request.env["stock.lot"].get_stock_lots()
        return request.make_response(
            json.dumps(result, indent=4),
            headers=[("Content-Type", "application/json")],
        )
