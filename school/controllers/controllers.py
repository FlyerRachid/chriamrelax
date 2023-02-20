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

    
    
    @http.route(['/request'], type='http', auth="public", csrf=False)
    def request(self, **kw):
        _logger.info("token : %s",(kw)) 
        data = {}
        data['error'] = True
        _logger.info("token : %s",(kw.get('token'))) 
        domaine = []
        domaine.append(('token','=',kw.get('token')))
        record = request.env['chriamrelax.price'].sudo().search(domaine)
        if len(record) == 1:
            data['error'] = False
            vals = {}
            
            vals.update({'partner_name' : kw.get('partner_name')})
            vals.update({'partner_email': kw.get('partner_email')})
            vals.update({'partner_phone': kw.get('partner_phone')})
            vals.update({'token': record.token})
            vals.update({'start': record.start})
            vals.update({'stop' : record.stop})
            vals.update({'residence_id': record.residence_id.id})
            vals.update({'residence': record.residence})

            reservation = http.request.env['chriamrelax.reservation'].sudo().create(vals)
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

        
        

        domain = []
        domain.append(('residence_id.name','=',residence_name.title()))
        availablity_ids = request.env['chriamrelax.price'].sudo().search(domain)
        
        events = [] 
        for rec in availablity_ids :
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
        
