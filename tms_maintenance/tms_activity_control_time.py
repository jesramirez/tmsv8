# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from dateutil.relativedelta import relativedelta
import pytz

class tms_activity_control_time(osv.Model):
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.activity.control.time'
    _description = 'Activity Control Time'
    _rec_name='state'

########################### Columnas : Atributos #######################################################################
    _columns = {
        'state': fields.selection([('draft','Draft'), ('process','Process'), ('pause','Pause'), ('end','End'), ('cancel','Cancel')],'State'),
        #eventossssss  ('process','Process'), ('pause','Pause'), ('end','End')
        ########One2Many###########
        'tms_time_ids': fields.one2many('tms.time','control_time_id', readonly="True"),

        ########char###########
        'uid': fields.char('uid', readonly="True"),

        ######## Date ###########
        'date_begin': fields.datetime('Date Begin', readonly="True"),
        'date_end': fields.datetime('Date End', readonly="True"),

        ######## Many2One ###########
#        'order_id': fields.many2one('tms.maintenance.order','Order', readonly="True"),
        'activity_id': fields.many2one('tms.maintenance.order.activity','Activity ID', readonly="True", ondelete='restrict'),
        'hr_employee_id': fields.many2one('hr.employee','Mechanic', readonly="True", ondelete='restrict'),
        'hr_employee_user_id': fields.many2one('res.users','User',readonly="True", ondelete='restrict'),
        
        ## Float
        'hours_mechanic':      fields.float('Hours Work', readonly="True"),

        ######## Related ###########
        'name_order': fields.related('activity_id','maintenance_order_id', 'name', type='char', string='Order', readonly=True, store=True),
        'name_activity': fields.related('activity_id','product_id', 'name_template', type='char', string='Activity', readonly=True, store=True),
        'order_id'       : fields.related('activity_id', 'maintenance_order_id', type='many2one', relation='tms.maintenance.order', string='MRO Order', store=True, readonly=True),
        'date'          : fields.related('order_id','date', type='date', string='Date', readonly=True, store=True),
        'office_id'       : fields.related('order_id', 'office_id', type='many2one', relation='tms.office', string='Office', store=True, readonly=True),
        'unit_id'       : fields.related('order_id', 'unit_id', type='many2one', relation='fleet.vehicle', string='Vehicle', store=True, readonly=True),                

    }
    
########################### Metodos ####################################################################################


    def calculate_diference_time(self, date_begin, date_end):
        duration = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S') - datetime.strptime(date_begin, '%Y-%m-%d %H:%M:%S')
        x1 = (duration.seconds / 3600.0) + (duration.days / 24 ) 
        return x1

    def calculate_time_activity(self, cr, uid, ids):
        sum_time = 0.0
        #temp_begin = False
        for time in self.browse(cr,uid,ids)[0].tms_time_ids:
            if time.event in 'process':
                temp_begin = time.date_event
            elif time.event in ('pause','end'):
                sum_time += self.calculate_diference_time(temp_begin, time.date_event)
        #print "sum_time: ", sum_time
        return sum_time

    def create_time_rec(self,cr,uid,ids, date_event, event):        
        this = self.browse(cr, uid, ids)[0]
        vals_time = {
                ## One2Many Request, Many2One  de tms_time a tms_activity_control_time
                'control_time_id'   : ids[0],
                'event'             : event,
                'date_event'        : date_event,
               }
        time_id  = self.pool.get('tms.time').create(cr, uid, vals_time, None)

        this.tms_time_ids.append(str(time_id))
        return

    ########## Metodos para el 'state' ##########

    def action_start(self, cr, uid, ids, context=None):
        z = pytz.timezone(self.pool.get('res.users').browse(cr, uid, [uid])[0].tz) or pytz.utc
        date_start  = datetime.utcnow().replace(tzinfo = pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        #datetime.utcnow().replace(tzinfo = pytz.utc).astimezone(z).strftime('%Y-%m-%d %H:%M:%S')        
        #date_start = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.write(cr, uid, ids, {'date_begin':date_start})
        ## Fijar Suma Fecha Inicio Actividad en (order.activity) campo (date_start_real) 
        this = self.browse(cr, uid, ids)[0]
        if this.activity_id:
            this.activity_id.write({'date_start_real':date_start})
 
        return self.action_process(cr, uid, ids, context)

    def action_process(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state':'process'})
        z = pytz.timezone(self.pool.get('res.users').browse(cr, uid, [uid])[0].tz) or pytz.utc
        date_event  = datetime.utcnow().replace(tzinfo = pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        #datetime.utcnow().replace(tzinfo = pytz.utc).astimezone(z).strftime('%Y-%m-%d %H:%M:%S')
        self.create_time_rec(cr,uid,ids, date_event, 'process')
        return True

    def action_pause(self,cr,uid,ids,context=None): 
        self.write(cr, uid, ids, {'state':'pause'})
        z = pytz.timezone(self.pool.get('res.users').browse(cr, uid, [uid])[0].tz) or pytz.utc
        date_event  = datetime.utcnow().replace(tzinfo = pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        #datetime.utcnow().replace(tzinfo = pytz.utc).astimezone(z).strftime('%Y-%m-%d %H:%M:%S')
        self.create_time_rec(cr,uid,ids, date_event, 'pause')
        return True  

    def action_end(self,cr,uid,ids,context=None):
        z = pytz.timezone(self.pool.get('res.users').browse(cr, uid, [uid])[0].tz) or pytz.utc
        date_end  = datetime.utcnow().replace(tzinfo = pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        #datetime.utcnow().replace(tzinfo = pytz.utc).astimezone(z).strftime('%Y-%m-%d %H:%M:%S')
        #date_end = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.write(cr, uid, ids, {'state':'end','date_end':date_end})
        self.create_time_rec(cr,uid,ids, date_end, 'end')

        ## Fijar Suma Tiempos             en (order.activity) campo (hours_real)
        ## Fijar Suma Fecha Fin Actividad en (order.activity) campo (date_end_real) 
        this = self.browse(cr, uid, ids)[0]
        if this.activity_id:
            time_total_mechanic = self.calculate_time_activity(cr, uid, ids)
            #this.activity_id.write({'hours_mechanic':time_total_mechanic})
            this.write({'hours_mechanic':time_total_mechanic})

            acumulate_of_activity = time_total_mechanic + this.activity_id.hours_real
            this.activity_id.write( {'hours_real':acumulate_of_activity, 
                                        'date_end_real':date_end,
                                        'date_most_recent_end_mechanic_activity':date_end})
            this.activity_id.maintenance_order_id.calculate_cost_service()
        ##### Cerrar La Actividad Padre si es Posible   
        this.activity_id.done_close_activity_if_is_posible()
        #####    
        return True 

    def action_cancel(self,cr,uid,ids,context=None): 
        self.write(cr, uid, ids, {'state':'cancel'})
        return True   

########################### Valores por Defecto ########################################################################
    _defaults = {
        'state'                 : lambda *a: 'draft',
    }

########################### Criterio de ordenamiento ###################################################################
    #_order = 'name'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
