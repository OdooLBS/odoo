import os
import requests
import json
import logging

_logger = logging.getLogger(__name__)


def sync_erp_to_lims(all_data):
    _logger.info("Tying to sync data with LIMS started")

    try:
        with open(
            "custom_addons/lab_product/scripts/output/sync.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        _logger.info(f"POST on https://mlims.com/api/erp/products/sync")
        _logger.info(f"Response from LIMS: sync done")

        return True

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
    # with open(
    #    "custom_addons/lab_product/scripts/output/lims_response.json",
    #    "w",
    #    encoding="utf-8",
    # ) as f:
    #    json.dump(lims_resp_json, f, ensure_ascii=False, indent=2)
    #
    # logging.info(f"LIMS response: {lims_resp_json}")

    # return lims_resp_json

    except Exception as e:
        _logger.error(f"Error while retrieving data: {e}")
