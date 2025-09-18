from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class LowStockAlertRunner(models.Model):
    _name = 'low.stock.alert.runner'
    _description = 'Low Stock Alert Runner (cron)'

    @api.model
    def run_low_stock_checks(self):
        """ Check all active orderpoints and create alerts if stock is below minimum."""
        orderpoint = self.env['stock.warehouse.orderpoint'].sudo()
        activity = self.env['mail.activity'].sudo()
        activity_type = self.env.ref('mail.mail_activity_data_todo')

        # Send alert to users in Inventory User group
        group = self.env.ref('stock.group_stock_user', raise_if_not_found=False)
        recipients = group.users if group else self.env['res.users']

        irModel = self.env['ir.model'].sudo()
        product_model = irModel.search([('model', '=', 'product.product')], limit=1)
        if not product_model:
            return
        
        active_orderpoints = orderpoint.search([('active', '=', True)])
        today = fields.Date.context_today(self)

        for o in active_orderpoints:
            product = o.product_id
            location = o.location_id

            _logger.debug("Checking product %s at location %s", product.display_name, location.display_name)

            # Forecasted quantity at orderpoint location
            # virtual_available is forecasted qty; with location context it becomes per-location
            forecast = (product.with_context(location=location.id).virtual_available) or 0.0
            min_qty = o.product_min_qty or 0.0

            _logger.debug("Forecast: %.2f, Min Qty: %.2f", forecast, min_qty)

            if min_qty <= 0:
                continue
            if forecast >= min_qty:
                continue

            # Build a unique summary to prevent duplicates per day
            summary = _("Low stock quantity: forecasted %.2f < min %.2f") % (forecast, min_qty)

            for u in recipients:
                exists = activity.search([
                    ('res_model', '=', 'product.product'),
                    ('res_model_id', '=', product_model.id),
                    ('res_id', '=', product.id),
                    ('summary', '=', summary),
                    ('user_id', '=', u.id),
                    ('active', '=', True),
                    ('date_deadline', '=', today),
                ], limit=1)

                _logger.debug("Existing activity: %s", bool(exists))

                if exists:
                    continue

                # Assign to responsible user/group if available; fallback to no user (visible to managers)
                vals = {
                    'activity_type_id': activity_type.id if activity_type else False,
                    'res_model': 'product.product',
                    'res_model_id': product_model.id,
                    'res_id': product.id,
                    'user_id': u.id,
                    'summary': summary,
                    'note': _(
                        "Forecasted quantity %(f).2f is below Min %(m).2f for rule '%(r)s' at %(loc)s."
                    ) % {'f': forecast, 'm': min_qty, 'r': o.display_name, 'loc': location.display_name},
                    'date_deadline': today,
                }

                _logger.debug("Creating activity with vals: %s", vals)

                activity.create(vals)

            # Log a message on the product message section for traceability
            product.message_post(
                body=_("Low stock alert at %s: forecasted %.2f < min %.2f (rule %s).") %
                (location.display_name, forecast, min_qty, o.display_name)
            )