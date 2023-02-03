#-*- coding: utf-8 -*-
from odoo import http, _
from odoo.osv import expression
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request

class School(http.Controller):
    @http.route('/school', auth='public')
    def index(self, **kw):
        # name = partner = request.env['res.users'].browse(request.uid).partner_id.name
        # return "Hello, School, we are happy to receive you , how are you %s ?"%(name)
        partner_id = partner = request.env.user.partner_id
        vals = {}
        vals.update({"partner_id"  : partner_id})
        return http.request.render('website.school-2', vals)
        
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
