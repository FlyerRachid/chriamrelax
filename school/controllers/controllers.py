#-*- coding: utf-8 -*-
from odoo import http, _
from odoo.osv import expression
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request
from datetime import timedelta

class School(http.Controller):
    
    @http.route('/school', type='http', auth="user", csrf=False, website=True)
    def index(self, **kw):
        partner_id = partner = request.env.user.partner_id
        vals = {}
        vals.update({"partner_id"  : partner_id})
        return http.request.render('school.listing', vals)
    
    
    @http.route('/calendar', type='http', auth="user", csrf=False, website=True)
    def calendar(self, **kw):
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
            data.update({"title"  : rec.name})
            data.update({"start"  : str(rec.start_date)})
            data.update({"end"    : str(rec.stop_date + timedelta(days=1))})   
            #data.update({"backgroundColor" :  backgroundColor_SELECTION[rec.name]})   
            data.update({"borderColor_SELECTION" :  borderColor_SELECTION[rec.name]})  
           
            events.append(data)
        
        calendar_js = "<script> var calendarEl = null;  document.addEventListener('DOMContentLoaded', function() {  calendarEl = document.getElementById('calendar'); var calendar = new FullCalendar.Calendar(calendarEl, {themeSystem: 'bootstrap4',locale : 'fr',initialView: 'dayGridMonth',header: {left: 'prev,next today',center: 'title',right: 'month,basicWeek,basicDay'},navLinks: true,height: 'auto',aspectRatio: 2,events: "+str(events)+",}); calendar.render();}); </script>"
        
        vals.update({"calendar_js"  : calendar_js})
        vals.update({"availablity_ids"  : availablity_ids})
        
        return http.request.render('school.calendar_chriamrelax', vals)
        
#     @http.route('/school/school/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('school.listing', {
#             'root': '/school/school',
#             'objects': http.request.env['school.school'].search([]),
#         })

#     @http.route('/school/school/objects/<model("school.school"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('school.object', {
#             'object': obj
#         })
