# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    
    reservation_id = fields.Many2one(
        'chriamrelax.reservation', string='Opportunity', check_company=True)