//alert('Odoo Js ?');
odoo.define('school.formation_', function (require) {
    "use strict";

    var core = require('web.core');
    var Dialog = require('web.Dialog');     
    var publicWidget = require('web.public.widget'); 
    
    var _t = core._t;

    var $pay_button = $('#o_form_formation');
    
    console.log($pay_button);
    console.log('Odoo Js .... ');
     
     publicWidget.registry.FormationForm = publicWidget.Widget.extend({ 
        selector: '.o_formation_form',
        events: {
            'click #o_form_formation': 'forEvent',
        },

        start: function () {
            console.log('Start fct .......');
            window.addEventListener('pageshow', function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.options = _.extend(self.$el.data(), self.options);
                $('[data-toggle="tooltip"]').tooltip();
            });
        },
        
        forEvent: function (ev) {
            
            ev.preventDefault();
            var form = this.el;
            var checked_radio = this.$('input[type="radio"]:checked');
            var self = this;
            if (ev.type === 'submit') {
                var button = $(ev.target).find('*[type="submit"]')[0]
            } else {
                var button = ev.target;
            }
            console.log('ev.target :',ev.target);
            console.log('ev.type   :',ev.type);
            console.log('self      :',self);
            var $pay_button = $('#o_form_formation');
            console.log(self.$('#formation_input').val());
            var partner_id = parseInt(self.$('#formation_input').val())

            var values = {'partner_id': partner_id};
            this._rpc({
                model: 'res.partner',
                method: 'method_formation_mediclic',
                args : [[partner_id]],
                kwargs:{arg1 : 'Mediclic',arg2 : 'Inwi',arg3 : 'Anfa'}
            }).then(function (result) { 
                console.log('Type Partner : ',typeof(result)); 
                console.log('Name Partner : ',result); 
                alert(result);
            });
            
        },
 
    });
     
    return publicWidget.registry.FormationForm;
});
