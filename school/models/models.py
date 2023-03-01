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
from odoo.osv import expression
import logging
_logger = logging.getLogger(__name__)



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
    
    
    #sale/models/sale_order.py
    #auth_signup/models/res_users.py
    
    def xml(self):
        import xml.etree.ElementTree as ET
        # create the root element ====
        root = ET.Element('items')

        # create child elements
        item1 = ET.SubElement(root, 'item')
        item1.set('id', '001')
        name1 = ET.SubElement(item1, 'name')
        name1.text = 'Item 1'
        price1 = ET.SubElement(item1, 'price')
        price1.text = '$10.00'

        item2 = ET.SubElement(root, 'item')
        item2.set('id', '002')
        name2 = ET.SubElement(item2, 'name')
        name2.text = 'Item 2'
        price2 = ET.SubElement(item2, 'price')
        price2.text = '$20.00'

        # create the XML file
        tree = ET.ElementTree(root)
        tree.write('/home/odoo/src/user/school/items.xml')

        from lxml import etree

        # create the root element
        root = etree.Element('items')

        # create child elements
        item1 = etree.SubElement(root, 'item')
        item1.set('id', '001')
        name1 = etree.SubElement(item1, 'name')
        name1.text = 'Item 1'
        price1 = etree.SubElement(item1, 'price')
        price1.text = '$10.00'

        item2 = etree.SubElement(root, 'item')
        item2.set('id', '002')
        name2 = etree.SubElement(item2, 'name')
        name2.text = 'Item 2'
        price2 = etree.SubElement(item2, 'price')
        price2.text = '$20.00'

        # create the XML file
        xml_string = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

        # save the XML file to disk
        file_path = '/home/odoo/src/user/school/file.xml'
        with open(file_path, 'wb') as f:
            f.write(xml_string)
    
    def action_send_email(self):
        # send email to users with their signup url        
        template = self.env.ref('school.request_email_template')
        assert template._name == 'mail.template'
        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }
        for user in self.partner_id:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
            # TDE FIXME: make this template technical (qweb)
            with self.env.cr.savepoint():
                force_send = not(self.env.context.get('import_file', False))
                template.send_mail(self.id, force_send=force_send, raise_exception=True, email_values=email_values)
        
    
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
            
    
    @api.depends('partner_street', 'partner_id')
    def _compute_is_partner_street_update(self):
        for rec in self:
            rec.is_partner_street_update = rec._get_partner_street_update()

    
    @api.depends('partner_zip', 'partner_id')
    def _compute_is_partner_zip_update(self):
        for rec in self:
            rec.is_partner_zip_update = rec._get_partner_zip_update()


    
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
    
    @api.depends('partner_id.street')
    def _compute_partner_street(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_street = rec.partner_id.street

    def _get_partner_street_update(self):
        self.ensure_one()
        if self.partner_id and self.partner_street != self.partner_id.street:
            ticket_street_formatted = self.partner_street or False
            partner_street_formatted = self.partner_id.street or False
            return ticket_street_formatted != partner_street_formatted
        return False
    
    def _inverse_partner_street(self):
        for rec in self:
            if rec._get_partner_street_update():
                rec.partner_id.street = rec.partner_street
                

    
    @api.depends('partner_id.zip')
    def _compute_partner_zip(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_zip = rec.partner_id.zip

    def _get_partner_zip_update(self):
        self.ensure_one()
        if self.partner_id and self.partner_zip != self.partner_id.zip:
            ticket_street_formatted = self.partner_zip or False
            partner_street_formatted = self.partner_id.zip or False
            return ticket_street_formatted != partner_street_formatted
        return False
    
    def _inverse_partner_zip(self):
        for rec in self:
            if rec._get_partner_zip_update():
                rec.partner_id.zip = rec.partner_zip
                

    def _get_partner_country_id_update(self):
        self.ensure_one()
        if self.partner_id and self.partner_country_id != self.partner_id.country_id:
            ticket_street_formatted  = self.partner_country_id    or False
            partner_street_formatted = self.partner_id.country_id or False
            return ticket_street_formatted != partner_street_formatted
        return False
    
    def _inverse_partner_country_id(self):
        for rec in self:
            if rec._get_partner_country_id_update():
                rec.partner_id.country_id = rec.partner_country_id.id
          
    @api.depends('partner_id.country_id')
    def _compute_partner_country_id(self):
        for rec in self:
            if rec.partner_id:
                rec.partner_country_id = rec.partner_id.country_id.id
    
    
    partner_id     = fields.Many2one('res.partner', string='Customer', tracking=True)
    partner_name   = fields.Char(string='Customer Name', compute='_compute_partner_name', store=True, readonly=False)
    partner_email  = fields.Char(string='Customer Email', compute='_compute_partner_email', inverse="_inverse_partner_email", store=True, readonly=False)
    partner_phone  = fields.Char(string='Customer Phone', compute='_compute_partner_phone', inverse="_inverse_partner_phone", store=True, readonly=False)
    partner_street = fields.Char(string='Customer Street', compute='_compute_partner_street', inverse="_inverse_partner_street", store=True, readonly=False)
    partner_zip    = fields.Char(string='Customer Zip', compute='_compute_partner_zip', inverse="_inverse_partner_zip", store=True, readonly=False)
    partner_country_id  = fields.Many2one('res.country',compute='_compute_partner_country_id', inverse="_inverse_partner_country_id",string='Customer Country', store=True, readonly=False)
    is_partner_email_update      = fields.Boolean('Partner Email will Update', compute='_compute_is_partner_email_update')
    is_partner_phone_update      = fields.Boolean('Partner Phone will Update', compute='_compute_is_partner_phone_update')
    is_partner_street_update     = fields.Boolean('Partner Street will Update', compute='_compute_is_partner_street_update')
    is_partner_zip_update        = fields.Boolean('Partner Zip will Update', compute='_compute_is_partner_zip_update')
    

    
    
    
                
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
    
    
    order_ids = fields.One2many('sale.order', 'reservation_id', string='Orders')
    
        
    title = fields.Char(
        string="title",
        required=True, copy=False, readonly=True,
        index='trigram',
        state={'option': [('readonly', False)]})
    
    
    def action_view_sale_order(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_reservation_id': self.id,
        }
        action['domain'] = expression.AND([[('reservation_id', '=', self.id)], self._get_lead_sale_order_domain()])
        orders = self.order_ids.filtered_domain(self._get_lead_sale_order_domain())
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action
    
    
    def _get_lead_sale_order_domain(self):
        return [('state', 'not in', ('draft', 'sent', 'cancel'))]
    
    
    def action_advance_invoice(self):
        
        availablity = self.env['chriamrelax.price'].search([('token', '=', self.token)])
        if not availablity:
           return False
        
        title = 'Advance invoice booking %s  (%s - %s)'%(self.residence,availablity.start_date,availablity.stop_date)
        
        product_variant = self.env['product.product'].browse(self.env.ref('school.product_product_advance_50%_Sirius').id)

        _logger.info("product_variant = = = => %s",(product_variant))
        _logger.info("product_tmpl_id = = = => %s",(product_variant.product_tmpl_id))

        # Create a new sale order record
        vals = {}
        vals.update({"partner_id"      : self.partner_id.id})
        vals.update({"reservation_id"  : self.id})
        vals.update({"type"            : 'action_advance_invoice'})
        sale_order = self.env['sale.order'].create(vals)
        
        sale_order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'name': title,
            'display_type': 'line_section',
            'sequence': 10  # Set the sequence to control the order of the sections
        })
        
        sale_order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': product_variant.id,
            'name': product_variant.name,
            'product_uom_qty': 1,
            'price_unit': availablity.price * 0.5 or product_variant.lst_price,
            'tax_id': [(6, 0, [self.env['account.tax'].search([('amount', '=', 6)])[0].id])],
        })
        
        # Go to the new sale order record
        action = self.env.ref('sale.action_orders').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        action['res_id'] = sale_order.id
        return action