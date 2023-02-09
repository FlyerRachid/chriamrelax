# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Reservation(models.Model):
    _name = 'chriamrelax.reservation'
    _description = 'chriamrelax.reservation'
    _order = 'date_order desc, id desc'

    
    name = fields.Char(
        string="Reservation Reference",
        required=False, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, readonly=False, change_default=True, index=True,
        tracking=1)
    
    state = fields.Selection(
        selection=[
            ('reserved', "Reserved"),
            ('option', "option"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=False, copy=False, index=True,
        tracking=3,
        default='option')
    
    date_order = fields.Datetime(
        string="Order Date",
        required=False, readonly=False, copy=False,
        default=fields.Datetime.now)
    
    start_date = fields.Date(string="Start")
    start_end  = fields.Date(string="End")
    
    residence = fields.Selection(
        selection=[
            ('Leeuw', "Leeuw"),
            ('Sirius', "Sirius"),
            ('Orion', "Orion"),
            ('De Bron', "De Bron"),
            ('Polaris', "Polaris"),
        ],
        string="Home",
        readonly=False, copy=False, index=True,
        tracking=3)

    
    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
