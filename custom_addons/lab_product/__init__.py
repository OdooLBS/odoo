# -*- coding: utf-8 -*-
from . import models
from . import controllers
from odoo import api, SUPERUSER_ID
from odoo.modules.module import get_module_resource
import logging

_logger = logging.getLogger(__name__)


# def _set_default_code(env):
#    env.cr.execute(
#        """ALTER TABLE product_template ALTER COLUMN default_code DROP NOT NULL;"""
#    )


# def _lab_product_init_hook(env):
#   _set_default_code(env)


def _lab_product_pre_init_settings(env):
    try:
        env.ref("stock.group_production_lot").write(
            {"implied_ids": [(4, env.ref("base.group_user").id)]}
        )
        env.ref("stock.group_tracking_lot").write(
            {"implied_ids": [(4, env.ref("base.group_user").id)]}
        )
        _logger.info(
            "Inventory settings updated: Lot and Serial Number tracking enabled."
        )

    except Exception as e:
        _logger.error(f"Failed to update inventory settings: {e}")
