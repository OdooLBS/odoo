import os
import requests
import json
import logging

logging.basicConfig(
    filename="custom_addons/lab_product/scripts/logs/sync.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)

try:
    token = os.environ.get("ERP_BEARER_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        url="http://localhost:8000/lab/products/quantity/all", headers=headers
    )
    response.raise_for_status()
    data = response.json()

    # todo salji u lims
    # dohvati token za lims
    # napravi post
    # loggaj reponse, vrati koirnsiku repons
    with open(
        "custom_addons/lab_product/scripts/output/sync.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logging.info(
        "Podaci uspješno dohvaćeni i zapisani u /custom_addons/lab_product/scripts/output/sync.json"
    )

except Exception as e:
    logging.error(f"Greška pri dohvaćanju ili zapisivanju podataka: {e}")
    print(f"Došlo je do greške: {e}")
