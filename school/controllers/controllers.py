#-*- coding: utf-8 -*-
from odoo import http, _
from odoo.osv import expression
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request

class School(http.Controller):
    @http.route('/school', type='http', auth="user", csrf=False, website=True)
    def index(self, **kw):
        partner_id = partner = request.env.user.partner_id
        vals = {}
        vals.update({"partner_id"  : partner_id})
        return http.request.render('school.listing', vals)
        
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
