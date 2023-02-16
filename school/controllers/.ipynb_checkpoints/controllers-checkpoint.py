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

class School(http.Controller):
    
    @http.route('/school', type='http', auth="user", csrf=False, website=True)
    def index(self, **kw):
        partner_id = partner = request.env.user.partner_id
        vals = {}
        vals.update({"partner_id"  : partner_id})
        return http.request.render('school.listing', vals)

    
    
    @http.route(['/request'], type='http', auth="public", csrf=False)
    def request(self, **kw):
        
        data = {}
        data['error'] = True
        _logger.info("token : %s",(kw.get('token'))) 
        
        domaine = []
        domaine.append(('token','=',kw.get('token')))
        record = request.env['chriamrelax.price'].sudo().search(domaine)
        
        _logger.info("record ============> : %s",(record)) 
        
        return json.dumps(data)

    
    @http.route('/calendar', type='http', auth="public", csrf=False, website=True)
    def calendar(self, **kw):
        
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

        
        events = []
        
        availablity_ids = request.env['chriamrelax.price'].sudo().search([])
        
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
        
