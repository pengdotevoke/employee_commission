from odoo import models, fields, api, exceptions
from datetime import datetime

class EmployeeCommission(models.Model):
    _name = 'employee.commission'
    _description = 'Employee Commissions Based on Profit'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    pos_order_id = fields.Many2one('pos.order', string="POS Order")
    commission_amount = fields.Float(string="Commission", compute="_compute_commission", store=True)
    cost = fields.Float(string="Cost", compute="_compute_cost", store=True)
    sale_amt = fields.Float(string="Sale Amount", compute="_compute_profit", store=True)
    is_paid = fields.Boolean(string="Paid", default=False)
    month = fields.Selection(
        [(str(i), datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)],
        string="Month",
        compute='_compute_month',
        store=True
    )
    
    @api.model
    def get_years(self):
        """Return a list of years dynamically."""
        current_year = fields.Date.context_today(self).year
        return [(str(year), str(year)) for year in range(2024, current_year + 1)]
    
    @api.depends('pos_order_id.date_order')
    def _compute_month(self):
        for record in self:
            if record.pos_order_id and record.pos_order_id.date_order:
                record.month = str(record.pos_order_id.date_order.month)
            else:
                record.month = False


    @api.depends('sale_id', 'pos_order_id')
    def _compute_cost(self):
        for record in self:
            record.cost = 0.0
            if record.sale_id:
                record.cost = sum(line.product_id.standard_price * line.product_uom_qty for line in record.sale_id.order_line)
            elif record.pos_order_id:
                record.cost = sum(line.product_id.standard_price * line.qty for line in record.pos_order_id.lines)

    @api.depends('sale_id', 'pos_order_id', 'cost')
    def _compute_profit(self):
        for record in self:
            record.sale_amt = 0.0
            if record.sale_id:
                #record.sale_amt = record.sale_id.amount_total - record.cost
                record.sale_amt = record.sale_id.amount_total 
            elif record.pos_order_id:
                #record.sale_amt = record.pos_order_id.amount_total - record.cost
                record.sale_amt = record.pos_order_id.amount_total

    @api.depends('sale_amt')
    def _compute_commission(self):
        for record in self:
            record.commission_amount = record.sale_amt * 0.01

    @api.model
    def create(self, vals):
        # Check for existing sale_id
        if 'sale_id' in vals:
            existing_commission = self.search([('sale_id', '=', vals['sale_id'])], limit=1)
            if existing_commission:
                raise exceptions.UserError("A commission record for this sale order already exists.")
        return super(EmployeeCommission, self).create(vals)

    @api.model
    def generate_commissions(self):
        # Fetch all completed sales and POS orders
        #sales_orders = self.env['sale.order'].search([('state', '=', 'sale')])
        pos_orders = self.env['pos.order'].search([('state', '=', 'done')])  # Adjust as needed

        # for sale in sales_orders:
        #     # Check if the employee exists before creating a commission
        #     if sale.user_id:
        #         employee = self.env['hr.employee'].search([('user_id', '=', sale.user_id.id)], limit=1)
        #         if employee and not self.search([('sale_id', '=', sale.id)]):  # Prevent duplicates
        #             self.create({
        #                 'employee_id': employee.id,
        #                 'sale_id': sale.id,
        #             })

        for pos_order in pos_orders:
            # Check if the employee exists before creating a commission
            if pos_order.employee_id:
                employee = self.env['hr.employee'].search([('user_id', '=', pos_order.employee_id.id)], limit=1)
                if employee and not self.search([('pos_order_id', '=', pos_order.id)]):  # Prevent duplicates
                    self.create({
                        'employee_id': employee.id,
                        'pos_order_id': pos_order.id,
                    })
    def action_mark_as_paid(self):
        for record in self:
            record.is_paid = True