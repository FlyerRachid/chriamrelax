#-*- coding: utf-8 -*-
from odoo import http, _
from odoo.osv import expression
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
from datetime import timedelta
import logging
import requests
import json
_logger = logging.getLogger(__name__)
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
import re
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_number


class CustomerPortal(portal.CustomerPortal):

    def _reservation_get_page_view_values(self, reservation, access_token, **kwargs):
        values = {
            'page_name': 'reservation',
            'reservation': reservation,
            'reservation_link_section': [],
        }
        return self._get_page_view_values(reservation, access_token, values, 'my_reservation_history', False, **kwargs)


    @http.route([
        "/chriamrelax/reservation/<int:reservation_id>",
        "/chriamrelax/reservation/<int:reservation_id>/<access_token>",
        '/my/reservation/<int:reservation_id>',
        '/my/reservation/<int:reservation_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def reservations_followup(self, reservation_id=None, access_token=None, **kw):
        try:
            reservation_sudo = self._document_check_access('chriamrelax.reservation', reservation_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        values = self._reservation_get_page_view_values(reservation_sudo, access_token, **kw)
        _logger.info("values  :::::::::::::::::::: %s",(values))
        return request.render("school.reservation_followup", values)

    

class School(http.Controller):
    
    @http.route('/school', type='http', auth="user", csrf=False, website=True)
    def index(self, **kw):
        partner_id = partner = request.env.user.partner_id
        vals = {}
        vals.update({"partner_id"  : partner_id})
        return http.request.render('school.listing', vals)
    
    
    def _check_email(self,email):
        # Make a regular expression
        # for validating an Email
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        # pass the regular expression
        # and the string into the fullmatch() method
        return re.fullmatch(regex, email)
    
    def _check_phone(self,val):
        _logger.info("isValidNumber :::::::  %s",(val.get('isValidNumber') ))
        #code_    = request.env['res.country'].sudo().browse(int(country_id)).code
        isValidNumber = val.get('isValidNumber') or False
        isValidNumber_SELECTION = {
                'false'      : False,
		        'true'       : True,
	    }
        if isValidNumber:
            return isValidNumber_SELECTION[isValidNumber]
        else:
            return False
            
    
    @http.route(['/request'], type='http', auth="public", csrf=False)
    def request(self, **kw):
        _logger.info("params  :::::::: %s",(kw))
        
        data = {}
        data['error'] = True
        
        email   = kw.get('partner_email')    or False
        name    = kw.get('partner_name')     or False
        phone   = kw.get('partner_phone')    or False
        street  = kw.get('partner_street')   or False
        zip     = kw.get('partner_zip')      or False
        country = kw.get('partner_country')  or False
        
        if not email or not name or not phone or not street or not zip or not country:
            data['html'] = "<strong> Warning ! </strong><span>Please complete all required fields marked with *. </span>"
            return json.dumps(data)
        
        check_email = self._check_email(email)
        if not check_email:
            data['html'] = "<strong> Warning ! </strong><span>Please enter a valid email.</span>";
            return json.dumps(data)
        
        check_phone = self._check_phone(kw)
        if not check_phone:
            data['html'] = "<strong> Warning ! </strong><span>Please enter a valid phone number compatible with your country code.</span>";
            return json.dumps(data)
        
        
        domaine = []
        domaine.append(('token','=',kw.get('token')))
        record = request.env['chriamrelax.price'].sudo().search(domaine)
        if len(record) == 1:
            data['error'] = False
            vals = {}
            vals.update({'partner_name'  : name})
            vals.update({'partner_email' : email})
            vals.update({'partner_phone' : phone})
            vals.update({'partner_street': street})
            vals.update({'partner_zip'          : zip})
            vals.update({'partner_country_id'   : int(country)})
            vals.update({'token': record.token})
            vals.update({'start': record.start})
            vals.update({'stop' : record.stop})
            vals.update({'residence_id': record.residence_id.id})
            vals.update({'residence': record.residence})
            reservation      = http.request.env['chriamrelax.reservation'].sudo().create(vals)
            reservation.title = 'Booking %s  (%s - %s)'%(reservation.residence,record.start_date,record.stop_date)
            reservation.action_send_email()
            
        _logger.info("reservation  ::::: %s",(reservation.access_token)) 
        
        return json.dumps(data)

    
    @http.route('/calendar/<string:residence_name>', type='http', auth="public", csrf=False, website=True)
    def calendar(self, residence_name = None, **kw):
        
        _logger.error('')
        _logger.info("")     
        _logger.exception("")
        
        vals = {}
        
        backgroundColor_SELECTION = {
                'Semaine'      : '#FFE033',
		        'Week-end'     : '#C7FF33',
                'Mi-Semaine' : '#33E6FF',
	    }
        
        borderColor_SELECTION = {
                'Semaine'      : 'red',
		        'Week-end'     : 'green',
                'Mi-Semaine'   : 'red',
	    }
        
        state_SELECTION = {
                'reserved'      : 'true',
		        'option'        : 'true',
                'open'          : 'false',
	    }

        domain = []
        domain.append(('residence_id.name','=',residence_name.title()))
        availablity_ids = request.env['chriamrelax.price'].sudo().search(domain)
        
        events = [] 
        for rec in availablity_ids :
            """
            domain = []
            domain.append(('token','=',rec.token))
            reservation_ids = request.env['chriamrelax.reservation'].sudo().search(domain)
            _logger.info("reservation_ids =================================> %s",(reservation_ids))
            state = state_SELECTION[reservation_id.state] if reservation_id else false
            _logger.info("state =================================> %s",(state))
            """
            state = state_SELECTION[rec.state]
            _logger.info("state =================================> %s",(rec.state,state_SELECTION[rec.state]))
            
            data = {}
            data.update({"system_id" : rec.id})
            data.update({"residence_name" : rec.residence_id.name})
            data.update({"residence_id"   : rec.residence_id.id})
            data.update({"price"     : rec.price})
            data.update({"id"        : rec.id})
            data.update({"title"     : rec.name})
            data.update({"start"     : str(rec.start_date)})
            data.update({"end"       : str(rec.stop_date + timedelta(days=1))})   
            data.update({"backgroundColor" :  backgroundColor_SELECTION[rec.name]})   
            country_code = request.geoip.get('country_code')
            data.update({"country_code" :  country_code})
            data.update({"token"        :  rec.token})
            events.append(data)
        
        calendar_js = "<script> var calendarEl = null;  document.addEventListener('DOMContentLoaded', function() {  calendarEl = document.getElementById('calendar'); var calendar = new FullCalendar.Calendar(calendarEl, {themeSystem: 'bootstrap4',locale : 'fr',initialView: 'dayGridMonth',header: {left: 'prev,next today',center: 'title',right: 'month,basicWeek,basicDay'},navLinks: true,height: 'auto',aspectRatio: 2,events: "+str(events)+",eventClick: function(info) {open_modalRequest(info)},}); calendar.render();}); </script>"
        
        calendar_js = "<script> var calendarEl = null;  document.addEventListener('DOMContentLoaded', function() {  calendarEl = document.getElementById('calendar'); var calendar = new FullCalendar.Calendar(calendarEl, {themeSystem: 'bootstrap4',locale : 'fr',initialView: 'dayGridMonth',header: {left: 'prev,next today',center: 'title',right: 'month,basicWeek,basicDay'},navLinks: true,height: 'auto',aspectRatio: 2,events: "+str(events)+",eventClick: function(info) {open_modalRequest(info)}, eventDidMount: function(info) {},}); calendar.render();}); </script>"
        
        vals.update({"calendar_js"      : calendar_js})
        vals.update({"availablity_ids"  : availablity_ids})
        
        countries = request.env['res.country'].sudo().search([])
        vals.update({"countries"  : countries})
        
        country_code = request.geoip.get('country_code')
        if country_code:
           country = request.env['res.country'].search([('code', '=', country_code)], limit=1)
           vals.update({"country"  : country})
        
        _logger.error('= = = > %s %s',(countries,country_code))

        return http.request.render('school.calendar_chriamrelax', vals)
        
