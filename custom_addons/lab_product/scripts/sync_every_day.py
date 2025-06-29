import psycopg2
import json
import logging


from decimal import Decimal

logging.basicConfig(level=logging.INFO)


def serialize_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Type not serializable")


db_params = {
    "host": "localhost",
    # database-2.cdmeoe40abo2.eu-central-1.rds.amazonaws.com
    "port": 5432,
    "dbname": "odoo_dev",
    # odoo
    "user": "odoo",
    "password": "admin",
    # odoo_novi_user123
}

output_file = "custom_addons/lab_product/scripts/output/sync_every_day.json"

try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT 
            product_product.default_code, 
            SUM(stock_quant.quantity) AS quantity
        FROM    
            product_product
        JOIN 
            stock_quant ON product_product.id = stock_quant.product_id
        WHERE
            stock_quant.location_id IN (
                SELECT id FROM stock_location WHERE usage = 'internal'
            )
        GROUP BY 
            product_product.default_code
   """
    )
    columns = [desc[0] for desc in cur.description]
    products = [dict(zip(columns, row)) for row in cur.fetchall()]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2, default=serialize_decimal)
    logging.info(f"Exported {len(products)} products to {output_file}")

    # lims_token = os.environ.get("LIMS_BEARER_TOKEN")
    # lims_headers = {
    #    "Authorization": f"Bearer {lims_token}",
    #    "Content-Type": "application/json",
    # }
    #
    # lims_url = "https://mlims.com/api/erp/products/sync"

    # _logger.info(f"Call {lims_url}")
    #
    # lims_response = requests.post(url=lims_url, headers=lims_headers, json=data)
    # lims_response.raise_for_status()

    # _logger.info(f"Response from LIMS: {lims_response}")
    #
    # lims_resp_json = lims_response.json()
    #
    # logging.info(f"LIMS response: {lims_resp_json}")

    # logging.info("Sync done")

except Exception as e:
    logging.error(f"Error: {e}")
finally:
    if conn:
        conn.close()
