from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Call the super method to ensure the order is confirmed
        super(SaleOrder, self).action_confirm()
        
        # Calculate and create commissions after confirming the sale
        self._create_or_update_commission()

    def action_done(self):
        # Call the super method to ensure the order is marked as done
        super(SaleOrder, self).action_done()
        
        # Calculate and create commissions when the sale is completed
        self._create_or_update_commission()

    def _create_or_update_commission(self):
        # Iterate through all confirmed orders to create/update commissions
        for order in self:
            employee = self.env['hr.employee'].search([('user_id', '=', order.user_id.id)], limit=1)
            if employee:
                commission_vals = {
                    'employee_id': employee.id,
                    'sale_id': order.id,
                }
                commission_record = self.env['employee.commission'].search([
                    ('sale_id', '=', order.id)], limit=1)

                if commission_record:
                    # Update existing commission record
                    commission_record.write(commission_vals)
                else:
                    # Create a new commission record
                    self.env['employee.commission'].create(commission_vals)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def action_pos_order_paid(self):
        # Call the super method to ensure the POS order is marked as paid
        super(PosOrder, self).action_pos_order_paid()

        # Calculate and create commissions after the POS order is paid
        self._create_or_update_commission()

    def _create_or_update_commission(self):
        for order in self:
            employee = self.env['hr.employee'].search([('user_id', '=', order.user_id.id)], limit=1)
            if employee:
                commission_vals = {
                    'employee_id': employee.id,
                    'pos_order_id': order.id,
                }
                commission_record = self.env['employee.commission'].search([
                    ('pos_order_id', '=', order.id)], limit=1)

                if commission_record:
                    # Update existing commission record
                    commission_record.write(commission_vals)
                else:
                    # Create a new commission record
                    self.env['employee.commission'].create(commission_vals)
