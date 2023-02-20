# -*- coding: utf-8 -*-

import logging
import math
from collections import defaultdict
from datetime import timedelta
from itertools import repeat

import pytz
import uuid

from odoo import api, Command, fields, models, tools, _

from odoo.osv.expression import AND
import re



class Residence(models.Model):
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
    _inherit = ['portal.mixin', 'mail.thread.cc', 'utm.mixin', 'rating.mixin', 'mail.activity.mixin']
    
    
    @api.model_create_multi
    def create(self, list_value):
        now = fields.Datetime.now()
        # Manually create a partner now since 'generate_recipients' doesn't keep the name. This is
        # to avoid intrusive changes in the 'mail' module
        # TDE TODO: to extract and clean in mail thread
        for vals in list_value:
            partner_id = vals.get('partner_id', False)
            partner_name = vals.get('partner_name', False)
            partner_email = vals.get('partner_email', False)
            if partner_name and partner_email and not partner_id:
                parsed_name, parsed_email = self.env['res.partner']._parse_partner_name(partner_email)
                if not parsed_name:
                    parsed_name = partner_name
                vals['partner_id'] = self.env['res.partner'].find_or_create(
                    tools.formataddr((parsed_name, parsed_email))
                ).id
        # context: no_log, because subtype already handle this
        reservations = super(Reservation, self).create(list_value)

        # make customer follower
        for rec in reservations:
            if rec.partner_id:
                rec.message_subscribe(partner_ids=rec.partner_id.ids)
            rec._portal_ensure_token()
        return reservations



    @api.depends('partner_email', 'partner_id')
    def _compute_is_partner_email_update(self):
        for rec in self:
            rec.is_partner_email_update = rec._get_partner_email_update()

    @api.depends('partner_phone', 'partner_id')
    def _compute_is_partner_phone_update(self):
        for rec in self:
            rec.is_partner_phone_update = rec._get_partner_phone_update()

    def _get_partner_email_update(self):
        self.ensure_one()
        if self.partner_id and self.partner_email != self.partner_id.email:
            ticket_email_normalized = tools.email_normalize(self.partner_email) or self.partner_email or False
            partner_email_normalized = tools.email_normalize(self.partner_id.email) or self.partner_id.email or False
            return ticket_email_normalized != partner_email_normalized
        return False

    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_id and self.partner_phone != self.partner_id.phone:
            ticket_phone_formatted = self.partner_phone or False
            partner_phone_formatted = self.partner_id.phone or False
            return ticket_phone_formatted != partner_phone_formatted
        return False
    
    @api.depends('partner_id')
    def _compute_partner_name(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_name = rec.partner_id.name

    @api.depends('partner_id.email')
    def _compute_partner_email(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_email = rec.partner_id.email

    def _inverse_partner_email(self):
        for rec in self:
            if rec._get_partner_email_update():
                rec.partner_id.email = rec.partner_email

    @api.depends('partner_id.phone')
    def _compute_partner_phone(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_phone = rec.partner_id.phone

    def _inverse_partner_phone(self):
        for rec in self:
            if rec._get_partner_phone_update():
                rec.partner_id.phone = rec.partner_phone
                
    partner_id     = fields.Many2one('res.partner', string='Customer', tracking=True)
    partner_name   = fields.Char(string='Customer Name', compute='_compute_partner_name', store=True, readonly=False)
    partner_email  = fields.Char(string='Customer Email', compute='_compute_partner_email', inverse="_inverse_partner_email", store=True, readonly=False)
    partner_phone  = fields.Char(string='Customer Phone', compute='_compute_partner_phone', inverse="_inverse_partner_phone", store=True, readonly=False)
    is_partner_email_update = fields.Boolean('Partner Email will Update', compute='_compute_is_partner_email_update')
    is_partner_phone_update = fields.Boolean('Partner Phone will Update', compute='_compute_is_partner_phone_update')
    
                
    name = fields.Char(
        string="Reservation Reference",
        required=False, copy=False, readonly=False,
        index='trigram',
        default=lambda self: _('New'))

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    

    
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

    
    start = fields.Datetime(
        'Start', required=True, tracking=True, default=fields.Date.today,
        help="Start date of an event, without time for full days events")
    stop = fields.Datetime(
        'Stop', required=True, tracking=True, default=lambda self: fields.Datetime.today() + timedelta(hours=1),
         readonly=False, store=True,
        help="Stop date of an event, without time for full days events")
    token = fields.Char('token')
    
    residence_id = fields.Many2one(
        comodel_name='chriamrelax.residence',
        required=True, index=True, tracking=True)
    
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
        tracking=True)
