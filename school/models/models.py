# -*- coding: utf-8 -*-

import logging
import math
from collections import defaultdict
from datetime import timedelta
from itertools import repeat

import pytz
import uuid

from odoo import api, fields, models, Command
from odoo.osv.expression import AND
import re



class Price(models.Model):
    _name = 'chriamrelax.residence'
    _description = 'chriamrelax.price'
    _order = 'id desc'
    
    name = fields.Char('Residence Name', required=True)
    
    
class Price(models.Model):
    _name = 'chriamrelax.price'
    _description = 'chriamrelax.price'
    _order = 'id desc'
    
    
    def _default_access_token(self):
        return uuid.uuid4().hex

    @api.depends('start', 'stop')
    def _compute_dates(self):
        """ Adapt the value of start_date(time)/stop_date(time)
            according to start/stop fields and allday. Also, compute
            the duration for not allday meeting ; otherwise the
            duration is set to zero, since the meeting last all the day.
        """
        for meeting in self:
            if  meeting.start and meeting.stop:
                meeting.start_date = meeting.start.date()
                meeting.stop_date = meeting.stop.date()
            else:
                meeting.start_date = False
                meeting.stop_date = False

    @api.depends('stop', 'start')
    def _compute_duration(self):
        for event in self:
            event.duration = self._get_duration(event.start, event.stop)

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if not start or not stop:
            return 0
        duration = (stop - start).total_seconds() / 3600 
        return round(duration, 2)
            
    start = fields.Datetime(
        'Start', required=True, tracking=True, default=fields.Date.today,
        help="Start date of an event, without time for full days events")
    stop = fields.Datetime(
        'Stop', required=True, tracking=True, default=lambda self: fields.Datetime.today() + timedelta(hours=1),
        compute='_compute_stop', readonly=False, store=True,
        help="Stop date of an event, without time for full days events")
    start_date = fields.Date(
        'Start Date', store=True, tracking=True,
        compute='_compute_dates')
    stop_date = fields.Date(
        'End Date', store=True, tracking=True,
        compute='_compute_dates')
    duration = fields.Float('Duration', compute='_compute_duration', store=True, readonly=False)
    
    residence_id = fields.Many2one(
        comodel_name='chriamrelax.residence',
        required=True, index=True)
    
    residence = fields.Selection(
        selection=[
            ('Leeuw', "Leeuw"),
            ('Sirius', "Sirius"),
            ('Orion', "Orion"),
            ('De Bron', "De Bron"),
            ('Polaris', "Polaris"),
        ],
        string="Residence",
        readonly=False, copy=False, index=True,
        tracking=3)

    price = fields.Float(string="Price")
    
    name = fields.Char('Name', required=True)
    token = fields.Char('token', default=_default_access_token)

    
    
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
