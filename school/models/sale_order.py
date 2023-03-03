# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def name_get(self):
        result = super(SaleOrder, self).name_get()
        for record in self:
            prefix = ''
            # Get the dynamic prefix based on some condition
            if record.partner_id.is_company:
                prefix = 'CO'
            else:
                prefix = 'PE'
            name = '%s%s' % (prefix, record.name)
            result.append((record.id, name))
        return result
    
    reservation_id = fields.Many2one(
        'chriamrelax.reservation', string='Opportunity', check_company=True)
    
    type = fields.Selection(
        selection=[
            ('action_advance_invoice', "Advance Invoice (50%)"),
            ('action_balance_bill', "Balance Bill"),
            ('action_energy_bill', "Energy Bill"),
        ],
        string="Type",
        readonly=False, copy=False, index=True,
        tracking=3)
    
    title = fields.Char(
        string="title",
        required=True, copy=False, readonly=True,
        index='trigram',
        state={'option': [('readonly', False)]})

    
    