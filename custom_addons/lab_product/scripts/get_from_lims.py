import os
import requests
import json
import logging

_logger = logging.getLogger(__name__)

# fix predaja ovaj file ne predavat

try:
    token = os.environ.get("ERP_BEARER_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}
    url = "http://localhost:8000/lab/products/quantity/update/all"

    with open(
        "custom_addons/lab_product/scripts/input/lims_update.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    response = requests.post(
        url=url,
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    data = response.json()

    with open(
        "custom_addons/lab_product/scripts/output/get_from_lims.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    _logger.info(
        "Data successfully logged in /custom_addons/lab_product/scripts/output/get_from_lims.json"
    )

except Exception as e:
    _logger.error(f"Error while retrieving data: {e}")
