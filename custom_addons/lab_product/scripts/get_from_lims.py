import os
import requests
import json
import logging

logging.basicConfig(
    filename="custom_addons/lab_product/scripts/logs/get_from_lims.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)

try:
    # todo ovo je zapravo fja iz limsa

    token = os.environ.get("ERP_BEARER_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    with open(
        "custom_addons/lab_product/scripts/input/lims_update.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    response = requests.post(
        url=f"http://localhost:8000/lab/products/quantity/update/all",
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

    logging.info(
        "Podaci uspješno dohvaćeni i zapisani u /custom_addons/lab_product/scripts/output/get_from_lims.json"
    )

except Exception as e:
    logging.error(f"Greška pri dohvaćanju ili zapisivanju podataka: {e}")
    print(f"Došlo je do greške: {e}")
