# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    reservation_id = fields.Many2one(
        'chriamrelax.reservation', string='Opportunity', check_company=True)
    
    type = fields.Selection(
        selection=[
            ('action_advance_invoice', "action_advance_invoice"),
            ('action_balance_bill', "action_balance_bill"),
            ('action_energy_bill', "action_energy_bill"),
        ],
        string="Type",
        readonly=False, copy=False, index=True,
        tracking=3)
    
    title = fields.Char(
        string="title",
        required=True, copy=False, readonly=True,
        index='trigram',
        state={'option': [('readonly', False)]})
