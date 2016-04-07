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
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import pytz

class tms_maintenance_order_activity(osv.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.maintenance.order.activity'
    _description = 'Activity'
    #_rec_name='product_id'

    def _supplier_invoiced(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            invoiced = (record.invoice_id.id)
            paid = (record.invoice_id.state == 'paid') if record.invoice_id.id else False
            res[record.id] =  { 'supplier_invoiced': invoiced,
                                'supplier_invoice_paid': paid,
                                'supplier_invoice_name': record.invoice_id.supplier_invoice_number
                                }
        return res
    
    def _get_costs(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            spares = manpower = spares_ext = 0.00
            for xline in rec.product_line_ids:
                spares += xline.cost_amount if not rec.external_workshop else 0.0
                spares_ext += xline.cost_amount if rec.external_workshop else 0.0
            if not rec.external_workshop:
                for line in rec.control_time_ids:
                    cost_mechanic = line.hr_employee_id.job_id.tms_global_salary or 0.0
                    manpower += (cost_mechanic * line.hours_mechanic)
            res[rec.id] = {'parts_cost' : spares, 'cost_service': manpower, 'parts_cost_external': spares_ext}
        return res    

    def _get_activity1(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tms.product.line').browse(cr, uid, ids, context=context):
            result[line.activity_id.id] = True
        return result.keys()
    
    def _get_activity2(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tms.activity.control.time').browse(cr, uid, ids, context=context):
            result[line.activity_id.id] = True
        return result.keys()

########################### Columnas : Atributos #######################################################################
    _columns = {
        'state'           : fields.selection([('cancel','Cancelled'), ('pending','Pending'), ('process','Process'),('done','Done')],'State'),

        'state_order'     : fields.related('maintenance_order_id','state',  type='char', string='State Order', readonly=True),

        'date_start'      : fields.datetime('Scheduled Date Start', required=True),
        'date_end'        : fields.datetime('Scheduled Date End', required=True),
        'date_start_real' : fields.datetime('Date Start Real', readonly=True),
        'date_end_real'   :   fields.datetime('Date End Real', readonly=True),
        'date_most_recent_end_mechanic_activity':   fields.datetime('Scheduled Most Recent Activity End of Mechanic'),


        'hours_estimated' : fields.float('Hours Estimated', readonly=True),
        'hours_real'      : fields.float('Hours Real Men', readonly=True),

        #'cost_service'    : fields.float('Service Cost', readonly=True),
        #'parts_cost'      : fields.float('Parts Cost', readonly=True),
        'parts_cost'     : fields.function(_get_costs, method=True, string='Spare Parts', type='float', multi=True, digits_compute=dp.get_precision('Sale Price'), 
                                            store = {'tms.maintenance.order.activity': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                     'tms.product.line': (_get_activity1, ['state', 'quantity', 'list_price'], 10),}),
        'cost_service'     : fields.function(_get_costs, method=True, string='Manpower', type='float', multi=True, digits_compute=dp.get_precision('Sale Price'), 
                                            store = {'tms.maintenance.order.activity': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                     'tms.activity.control.time': (_get_activity2, ['state','hours_mechanic'], 10),}),
        'external_workshop':      fields.boolean('External', help="Check if this task is going to be done bya an external supplier "),
        'breakdown':              fields.boolean('Breakdown'),


        'supplier_invoiced':  fields.function(_supplier_invoiced, method=True, string='Supplier Invoiced', type='boolean', multi='supplier_invoiced', store=True),
        'supplier_invoice_paid':  fields.function(_supplier_invoiced, method=True, string='Supplier Invoice Paid', type='boolean', multi='invoiced', store=True),
        'supplier_invoice_name':  fields.function(_supplier_invoiced, method=True, string='Supplier Invoice', type='char', size=64, multi='invoiced', store=True),



        'invoiced'          :               fields.boolean('Facturado'),
        'invoice_id'        :             fields.many2one('account.invoice','Invoice', readonly=True, ondelete='restrict'),
        'supplier_id':            fields.many2one('res.partner','Supplier', ondelete='restrict'),

        'cost_service_external':    fields.float('Service Cost External', states={'cancel':[('readonly',True)], 'done':[('readonly',True)]}),
        'parts_cost_external'   : fields.function(_get_costs, method=True, string='Spare Parts External', type='float', multi=True, digits_compute=dp.get_precision('Sale Price'), 
                                            store = {'tms.maintenance.order.activity': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                     'tms.product.line': (_get_activity1, ['state', 'quantity', 'list_price'], 10),}),

        

        ######## Many2One ##########################
        'product_id': fields.many2one('product.product','Activity', domain=[('tms_category','=','maint_activity')] , required=True, ondelete='restrict'),
        'name'      : fields.related('product_id', 'name', string="Name", type='char', readonly=True, store=True),
        ######## Many2One request One2Many ##########
        'maintenance_order_id': fields.many2one('tms.maintenance.order','Service Order', readonly=True, ondelete='restrict'),
        ######## Many2Many ##########################
        'mechanic_ids': fields.many2many('hr.employee','tms_maintenance_order_activity_rel','activity_id','maintenance_id','Mechanics',domain=[('tms_category', '=', 'mechanic')]),
        ######## One2Many ###########################
        'product_line_ids': fields.one2many('tms.product.line','activity_id','Material List'),
        'control_time_ids': fields.one2many('tms.activity.control.time','activity_id','Kiosk List'),
        ########Related ###########
        'office_id'       : fields.related('maintenance_order_id', 'office_id', type='many2one', relation='tms.office', string='Shop', store=True, readonly=True),
        'unit_id'       : fields.related('maintenance_order_id', 'unit_id', type='many2one', relation='fleet.vehicle', string='Vehicle', store=True, readonly=True),                
        'dummy_field'   : fields.boolean('Dummy'),
    }
    
########################### Metodos ####################################################################################

    def _check_activity_save(self, cr, uid, ids, context=None):
        this = self.get_current_instance(cr, uid, ids)
        return not(this['maintenance_order_id']['state'] in 'released' and not this['state'] in ('done','cancel'))

    def _check_activity_duplicate(self, cr, uid, ids, context=None):
        this = self.get_current_instance(cr, uid, ids)
        for activity in this['maintenance_order_id']['activities_ids']:
            if activity['id'] != this['id']:
                if activity['product_id'] == this['product_id']:
                    return False
        return True

    _constraints = [
        (_check_activity_save, 'Error ! You can not create Tasks in when Maintenance Service Order is in Released State, please delete any Task recently added to be able to save changes', []),
        (_check_activity_duplicate, 'Error ! You can not create Duplicate Tasks, please delete any Task recently added to be able to save changes', [])
    ]

    ########## Metodo Create ##########
    def create(self, cr, uid, vals, context=None):
        retorno = super(tms_maintenance_order_activity, self).create(cr, uid, vals, context)
        this = super(tms_maintenance_order_activity, self).browse(cr, uid, retorno)  
        #this.create_kiosk_register(context)

        #Sincronizar State de la orden, a state_order de la actividad
        this.synchronize_state_order()
        
        #if this['maintenance_order_id']['state'] in 'released':
        #    #print 'holaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        #    this.action_cancel()
        #    retorno = False
        #    this.unlink()
        
        #    raise osv.except_osv(_('Warning!'),_('Imposible Create Activity in State Released ')) 

        return retorno

    def create_kiosk_register(self,cr,uid,ids, context=None):
        this = self.get_current_instance(cr, uid, ids)
        vals = {
                'order_id':this['maintenance_order_id']['id'],
                'activity_id':this['id'],
                'name_order':this['maintenance_order_id']['name'],
                'name_activity':this['product_id']['name_template'],
               }
        #vals ={}
        control_time_id  = self.pool.get('tms.activity.control.time').create(cr, uid, vals, context)
        control_time_obj = self.pool.get('tms.activity.control.time').browse(cr, uid, control_time_id)
        ## one 2 many a control time
        this['control_time_ids'].append(control_time_id)
        #control_time_obj.action_process(cr, uid, ids, context)

    def create_control_time_to_mechanic(self,cr,uid,ids, mechanic_obj, context=None):
        this = self.get_current_instance(cr, uid, ids)
        vals = {
                'order_id':this['maintenance_order_id']['id'],
                'activity_id':this['id'],
                'name_order':this['maintenance_order_id']['name'],
                'name_activity':this['product_id']['name_template'],
                'hr_employee_id':mechanic_obj['id'],
                #'hr_employe_user_id':mechanic_obj['user_id']['id'],
               }
 
        control_time_id  = self.pool.get('tms.activity.control.time').create(cr, uid, vals, context)
        control_time_obj = self.pool.get('tms.activity.control.time').browse(cr, uid, control_time_id)
        ## one 2 many a control time
        this['control_time_ids'].append(control_time_id)
        #control_time_obj.action_process(cr, uid, ids, context)
        #Agregar el usuario relacionado al Mechanic
        
        if mechanic_obj['user_id']:
            control_time_obj.write({'hr_employee_user_id':mechanic_obj['user_id']['id']})

    def create_control_times(self,cr,uid,ids,context=None):
        this = self.get_current_instance(cr, uid, ids)
        for mechanic_obj in this['mechanic_ids']:
            self.create_control_time_to_mechanic(cr,uid,ids, mechanic_obj, context)
        
        
        
    def done_close_activity_if_is_posible(self,cr,uid,ids,context=None):
        this = self.get_current_instance(cr, uid, ids)
        self.calculate_parts_cost(cr,uid,ids)
        self.calculate_cost_service(cr,uid,ids)
        ### preguntar si existen actividades de los mecanicos
        ### si existen, que todas esten finalizadas
        for mechanic_activity in this['control_time_ids']:
            if not mechanic_activity['state'] in ('end'):
                #print 'All Mechanics Activities, should be in state End'
                return False
        #######################################################################
        if not (self.is_exist_products_lines_pending(cr,uid,ids)):
            for line in self.get_products_lines_obj(cr, uid, ids):
                if line['state'] in 'draft':
                    line.action_cancel()
            self.write(cr, uid, ids, {'state':'done','date_end_real':this['date_most_recent_end_mechanic_activity']})
            return True

        #print 'All Product Lines should be not State Pending or Not Exist Product Lines' 
        return False 
        

    
    ########## Metodos para el costo de productos y servicio ########## 
    def set_cost_service(self,cr,uid,ids, cost_service=0.0):
        self.write(cr, uid, ids, {'cost_service':cost_service})

    def set_parts_cost(self,cr,uid,ids, parts_cost=0.0):
        self.write(cr, uid, ids, {'parts_cost':parts_cost})

    def calculate_parts_cost(self,cr,uid,ids,context=None):
        suma = 0.0
        for line in self.get_products_lines_obj(cr, uid, ids):
            suma = suma + (line['product_id']['standard_price'] * line['quantity'] )
        self.set_parts_cost(cr,uid,ids, suma)
        ### Si es Taller Externo la Actividad entonces ejecutara su propia sumatoria
        this = self.get_current_instance(cr, uid, ids)
        #if this['external_workshop']:
        #    self.calculate_parts_cost_external(cr,uid,ids)

    def calculate_cost_service(self,cr,uid,ids,context=None):
        suma = 0.0
        this = self.get_current_instance(cr, uid, ids)
        for line in this['control_time_ids']:
            cost_mechanic = line.hr_employee_id and line.hr_employee_id.job_id and line.hr_employee_id.job_id.tms_global_salary or 0.0
            suma += (cost_mechanic * line['hours_mechanic'])
        self.set_cost_service(cr,uid,ids, suma)
        ### Si es Taller Externo la Actividad entonces eejecutara su propia sumatoria
        this = self.get_current_instance(cr, uid, ids)
        if this['external_workshop']:
            self.calculate_cost_service_external(cr,uid,ids)

    def calculate_parts_cost_external(self,cr,uid,ids,context=None):
        suma = 0.0
        this = self.get_current_instance(cr, uid, ids)
        ########################################################################### Completar
        ########################################################################### Completar  cost_service_external
        ########################################################################### Completar  parts_cost_external

        if this['breakdown']:
            for line in this['product_line_ids']:
                suma += (line['standard_price'] * line['quantity'])
            self.write(cr, uid, ids, {'parts_cost_external':suma})
        
        if not this['breakdown']:
            suma = this['parts_cost_external']

        self.set_parts_cost(cr,uid,ids, suma)

    def calculate_cost_service_external(self,cr,uid,ids,context=None):
        suma = 0.0
        this = self.get_current_instance(cr, uid, ids)
        ########################################################################### Completar
        ########################################################################### Completar
        ########################################################################### Completar
        suma = this['cost_service_external']
        self.set_cost_service(cr,uid,ids, suma)

    def calculate_cost_service_no_used(self,cr,uid,ids,context=None):
        suma = 0.0
        this = self.get_current_instance(cr, uid, ids)
        for mechanic in self.get_mechanics(cr,uid,ids):
            cost_mechanic = mechanic.job_id.tms_global_salary
            suma += cost_mechanic * this['hours_real']
        self.set_cost_service(cr,uid,ids, suma)

    def get_mechanics(self,cr,uid,ids):
        mechanics_ids = self.get_current_instance(cr, uid, ids)['mechanic_ids']
        mechanics = self.pool.get('hr.employee').browse(cr, uid, mechanics_ids)
        return mechanics

    ########## Metodos para el 'state' ########## 
    def synchronize_state_order(self,cr,uid,ids,context={}):
        this = self.get_current_instance(cr, uid, ids)
        self.write(cr, uid, ids, {'state_order':''+str( this['maintenance_order_id']['state'] ) })

    def generate_stock_product_line(self,cr,uid,ids,context={}):
        this = self.get_current_instance(cr, uid, ids)
        for line in this['product_line_ids']:
            line.action_pending()

    def action_pending(self,cr,uid,ids,context={}):
        self.write(cr, uid, ids, {'state':'pending'})
        return True

    def action_process(self, cr, uid, ids, context={}):
        ##### Comprobar primero si tiene Mecanicos Asignados  ##################################################
        this = self.get_current_instance(cr, uid, ids)
        
        if not this['maintenance_order_id']['state'] in 'open':
            raise osv.except_osv(_('Warning!'),_('For Process should be Order in state OPEN ')) 

        band = False
        ## Poner la bandera en True si es actividad de taller externo para saltar la comprobacion Si o No existen mecanicos
        if this['external_workshop']:
            band = True
        ############### Comprobar si existen mecanicos asignados a la actividad #########################
        for band in this['mechanic_ids']:
            band = True
        if not band:
            raise osv.except_osv(_('Warning!'),_('For Process should be exist Mechanics Asigned'))             
        ##### ################ ###################### ########################################################## 
        self.write(cr, uid, ids,{'state':'process','date_start_real':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}) 
        self.write(cr, uid, ids,{'hours_estimated':this['product_id']['tms_activity_duration']}) 
        ## Lista Materiales hacer la solicitud en almacen si esta desactivada la opcion taller externo
        if not this['external_workshop']:
            self.generate_stock_product_line(cr,uid,ids,context)
        #### Crear los kioskos
        self.create_control_times(cr,uid,ids,context)
        return True

    def action_done(self,cr,uid,ids,context={}): 

        this = self.get_current_instance(cr, uid, ids)
        self.calculate_parts_cost(cr,uid,ids)
        self.calculate_cost_service(cr,uid,ids)
        if this['external_workshop']:
            #self.calculate_parts_cost_external(cr,uid,ids)
            #self.calculate_cost_service_external(cr,uid,ids)
            self.write(cr, uid, ids, {'state':'done','date_end_real':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
            return True

        ### preguntar si existen actividades de los mecanicos
        ### si existen, que todas esten finalizadas
        for mechanic_activity in this['control_time_ids']:
            if not mechanic_activity['state'] in ('end'):
                raise osv.except_osv(_('Warning!'),_('All Mechanics Activities, should be in state End'))
        #######################################################################
        if not (self.is_exist_products_lines_pending(cr,uid,ids)):
            for line in self.get_products_lines_obj(cr, uid, ids):
                if line['state'] in 'draft':
                    line.action_cancel()
            self.write(cr, uid, ids, {'state':'done','date_end_real':this['date_most_recent_end_mechanic_activity']})
            return True

        raise osv.except_osv(_('Warning!'),_('All Product Lines should be not State Pending or Not Exist Product Lines')) 
        return False  

    def action_cancel(self, cr, uid, ids, context={}):
                    
        if not (self.is_exist_products_lines_pending(cr,uid,ids)):
            for line in self.get_products_lines_obj(cr, uid, ids):
                if line['state'] in 'draft':
                    line.action_cancel()
            self.write(cr, uid, ids, {'state':'cancel'})
            return True

        raise osv.except_osv(_('Warning!'),_('All Product Lines should be not State Pending or Not Exist Product Lines')) 
        return False 

    ########## Metodo Copy ##########
    def copy(self, cr, uid, id, default=None, context=None):
        maintenance = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default.update({ 
                        'state'         : 'pending',
                        })
        return super(tms_maintenance_order_activity, self).copy(cr, uid, id, default, context=context)
        
    ##########  Comprobar si solo existen product_line en estado borrador, cancel, pending, delivered #########
    def is_only_exist_products_lines_draft(self,cr,uid,id):
        band = True
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        
        if self.is_exist_products_lines_cancel(cr,uid,id):
            return False
        if self.is_exist_products_lines_pending(cr,uid,id):
            return False
        if self.is_exist_products_lines_delivered(cr,uid,id):
            return False
        return self.is_exist_products_lines_draft(cr,uid,id)       
 
    def is_only_exist_products_lines_cancel(self,cr,uid,id):
        band = True
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        
        if self.is_exist_products_lines_draft(cr,uid,id):
            return False
        if self.is_exist_products_lines_pending(cr,uid,id):
            return False
        if self.is_exist_products_lines_delivered(cr,uid,id):
            return False
        return self.is_exist_products_lines_cancel(cr,uid,id)   

    def is_only_exist_products_lines_pending(self,cr,uid,id):
        band = True
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        
        if self.is_exist_products_lines_draft(cr,uid,id):
            return False
        if self.is_exist_products_lines_cancel(cr,uid,id):
            return False
        if self.is_exist_products_lines_delivered(cr,uid,id):
            return False
        return self.is_exist_products_lines_pending(cr,uid,id)  
  
    def is_only_exist_products_lines_delivered(self,cr,uid,id):
        band = True
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        
        if self.is_exist_products_lines_draft(cr,uid,id):
            return False
        if self.is_exist_products_lines_cancel(cr,uid,id):
            return False
        if self.is_exist_products_lines_pending(cr,uid,id):
            return False
        return self.is_exist_products_lines_delivered(cr,uid,id)   

  
    ##########  Comprobar si existen product_line en estado borrador, cancel, pending, delivered #########
    def is_exist_products_lines_draft(self,cr,uid,id):
        band = False
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        for line in product_lines:
            if self.is_draft_product_line(line):
                band = True
        return band

    def is_exist_products_lines_cancel(self,cr,uid,id):
        band = False
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        for line in product_lines:
            if self.is_cancel_product_line(line):
                band = True
        return band

    def is_exist_products_lines_pending(self,cr,uid,id):
        band = False
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        for line in product_lines:
            if self.is_pending_product_line(line):
                band = True
        return band

    def is_exist_products_lines_delivered(self,cr,uid,id):
        band = False
        actividad = self.get_current_activity(cr,uid,id)
        product_lines = self.get_product_line_list_obj(actividad)
        if not product_lines:
            #print 'This activity not have product_lines .........' 
            return False
        for line in product_lines:
            if self.is_delivered_product_line(line):
                band = True
        return band
            

    ##########  Obtener al objeto actividad de esta clase #########
    def get_current_activity(self,cr,uid,id):
        objs = self.browse(cr,uid,id)
        
        activity_obj = None
        for o in objs:
            activity_obj = o
        return activity_obj

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj

    ##########  Obtener Lista de objetos de tipo (product_line) #########
    def get_product_line_list_obj(self, activity_obj):
        product_lines = activity_obj['product_line_ids']  
        #if not product_lines:
        #    #print 'product line es None...................##########################################################'
        return product_lines

    def get_products_lines_obj(self, cr, uid, ids):
        product_lines = self.get_current_instance(cr, uid, ids)['product_line_ids']
        return product_lines

    ##########  Existe arreglo de product_line (product_line) #########
    def is_exist_products_lines(self,cr,uid,id):
        activity_obj = self.get_current_activity(cr,uid,id)
        product_lines = activity_obj['product_line_ids']
        if not product_lines:
            #print 'product line Array es None...................##########################################################'
            return False
        return True


    ##########  Obtener el objeto product.product desde un (product_line) #########
    def get_product_product(self, product_line):
        return product_line['product_id']

    ##########  comprueba el state de un objeto (product_line) #########
    def is_draft_product_line(self, product_line):
        band = False
        if self.get_state_product_line(product_line) in 'draft':
            band = True
        return band
    def is_cancel_product_line(self, product_line):
        band = False
        if self.get_state_product_line(product_line) in 'cancel':
            band = True
        return band
    def is_pending_product_line(self, product_line):
        band = False
        if self.get_state_product_line(product_line) in 'pending':
            band = True
        return band
    def is_delivered_product_line(self, product_line):
        band = False
        if self.get_state_product_line(product_line) in 'delivered':
            band = True
        return band
    ##########  Obtener state de product_line #########
    def get_state_product_line(self, product_line):
        return product_line['state']


######################### Metodos Manipulacion de Stock_picking ########
######################### Metodos Manipulacion de Stock_picking ########
######################### Metodos Manipulacion de Stock_picking ########

    def create_stock_picking(self,cr,uid,id,context=None):
        seq_order=(self.get_current_instance(cr, uid, id))['maintenance_order_id']['name']
        id_order=(self.get_current_instance(cr, uid, id))['maintenance_order_id']['id']
        vals = {
                'origin':':'+str(seq_order),
                'type':'internal',
                #'type':'out',
                'state':'draft',
                'move_type':'direct', # Delivery Method : partial=direct
                'tms_order_id':''+str(id_order),
                'from_tms_order' : True,
               }    
        stock_id  = self.pool.get('stock.picking').create(cr, uid, vals, context)
        stock_obj = self.pool.get('stock.picking').browse(cr, uid, stock_id)
        return stock_obj

    def is_exist_stock_picking(self,cr,uid,id):
        stocks_objs = self.get_stock_picking_obj_list(cr,uid,id)
        if stocks_objs:
            return True
        
        return False
        
    def get_stock_picking_obj_list(self,cr,uid,id):

        #Obtiene el ID de tms_maintenance_order y construye el args para la busqueda
        id_order=(self.get_current_instance(cr, uid, id))['maintenance_order_id']['id']
        args = [('tms_order_id','=',id_order)]

        # busca los stock_picking donde su atributo tms_order_id sea = al order_id, 
        # y devuelve una lista de id de stock_picking que encontro
        stocks_id = self.pool.get('stock.picking').search(cr,uid,args)

        # obtiene una lista de instancias de stock_picking, mediante una lista de ids de stock_piking
        stocks_objs = self.pool.get('stock.picking').browse(cr,uid,stocks_id)  
        # Retorna la lista de stock_picking relacionada a la orden de mantenimiento
        return stocks_objs

################################# Metodos Para Escribir Genericos ################################
    #def write(self, cr, uid, ids, vals, context=None):
    #    res = super(tms_maintenance_order_activity, self).write(cr, uid, ids, vals, context)
    #    order_ids = [x['maintenance_order_id'] for x in self.read(cr, uid, ids, ['maintenance_order_id'])]
    #    print "order_ids: ", order_ids
        #raise osv.except_osv('Pausa', 'Pausa')
        
    #    self.pool.get('tms.maintenance.order').write(cr, uid, order_ids, {'dummy_field' : True})
    #s    return res
        
    def write_custom(self, cr, uid, id, vals, context=None):
        self.write(cr,uid,id,vals,context)

    def set_state(self, cr, uid, id, state, context=None):
        vals = {'state':''+str(state)}
        self.write_custom(cr, uid, id, vals, context)
        
        ######################### Metodos Para Cambiar Estados ################################

    def change_state_to_process(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'process')

    def change_state_to_cancel(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'cancel')

    def change_state_to_pending(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'pending')

    def change_state_to_done(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'done')

#################################################################################################

    def on_change_product_id(self,cr,uid,ids, product_id, date_start):
        producto = self.pool.get('product.product').browse(cr, uid, product_id)
        duration = producto['tms_activity_duration']
        delta = timedelta(hours=duration or 1)
        origin = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
        end_date = origin + delta
        return {'value':{'hours_estimated':duration, 'date_end': end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}}

    def on_change_date_start(self,cr,uid,ids, hours_estimated, date_start):
        delta = timedelta(hours=hours_estimated or 1)
        origin = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')
        end_date = origin + delta
        return {'value':{'date_end': end_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}}
    
    
    def on_change_external_workshop(self,cr,uid,ids, external_workshop):
        valores = {}
        if not external_workshop:
            valores = {'value':{'breakdown':True}} 
        return valores

########################################################################################################################
#####################################  Metodos de prueba Impresion  ####################################################
########################################################################################################################
    def cambiar_product_line_state(self,cr,uid,id, context=None):
        product_lines = self.get_product_line_list_obj(self.get_current_instance(cr,uid,id))
        
        for line in product_lines:
            line.change_state_to_delivered()
    
    def print_stock_picking(self,cr,uid,id, context=None):
        #print '-----------------------------------------------------------------------------------------------------------------------'
        #print '-----------------------------------------------------------------------------------------------------------------------'
        band = self.is_exist_stock_picking(cr,uid,id)
        #print 'Existen stock_picking relacionados a esta orden proveniente de esta actividad: '+ str(band)
        #print '-----------------------------------------------------------------------------------------------------------------------'
        #print '-----------------------------------------------------------------------------------------------------------------------'
        
        #if band:
        #    for line in self.get_stock_picking_obj_list(cr,uid,id):
                #print 'id    stock:                 '+str(line['id'])  
                #print 'name  stock:                 '+str(line['name'])  
                #print 'state stock:                 '+str(line['state'])
                #print 'maintenance_order_id:        '+str(line['tms_order_id'])  
                #print 'maintenance_order_id[name]:  '+str(line['tms_order_id']['name'])  
                #print 'maintenance_order_id[state]: '+str(line['tms_order_id']['state'])  
                #print 'maintenance_order_id[id]:    '+str(line['tms_order_id']['id'])     
                #print '----------------------------------------------------------------------------------------------------------------' 
    def crear_stock_picking(self,cr,uid,id, context=None):
        stock_line = self.create_stock_picking(cr,uid,id,context)
        #if stock_line:
            #print 'Stock_line Fue Creado Exitosamente----------------------------------------------------------------------------------'
            #print 'id    stock:                 '+str(stock_line['id'])  
            #print 'name  stock:                 '+str(stock_line['name'])  
            #print 'state stock:                 '+str(stock_line['state'])
            #print 'maintenance_order_id:        '+str(stock_line['tms_order_id'])  
            #print 'maintenance_order_id[name]:  '+str(stock_line['tms_order_id']['name']) 
            #print 'maintenance_order_id[state]: '+str(stock_line['tms_order_id']['state'])  
            #print 'maintenance_order_id[id]:    '+str(stock_line['tms_order_id']['id'])  
        
########################### Valores por Defecto ########################################################################
    _defaults = {
        'state'                 : lambda *a: 'pending',
        'breakdown'             : lambda *a: True,
        'date_start'            : lambda self, cr, uid, context: datetime.utcnow().replace(tzinfo = pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'date_end'              : lambda self, cr, uid, context: datetime.utcnow().replace(tzinfo = pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }

########################### Criterio de ordenamiento ###################################################################
    #_order = 'name'


# Wizard que permite asignar Mecánicos a una o varias Tareas a la vez
class tms_maintenance_order_activity_assign_manpower(osv.osv_memory):

    """ To assign internal manpower to several Tasks"""

    _name = 'tms.maintenance.order.activity.assing_manpower'
    _description = 'Assign internal Manpower to several Tasks'

    _columns = {
            
            'mechanic_ids': fields.many2many('hr.employee','tms_maintenance_order_assign_manpower_rel', 'activity_id','maintenance_id','Mechanics', 
                                            domain=[('tms_category', '=', 'mechanic')], required=True),
        }

    def assign_manpower(self, cr, uid, ids, context=None):

        """
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary

        """
        task_obj = self.pool.get('tms.maintenance.order.activity')
        task_ids =  context.get('active_ids',[])
        task_ids = task_obj.search(cr, uid, [('id','in',tuple(task_ids),),('state','=', 'pending')])
        if not task_ids:
            raise osv.except_osv(
                        _('Warning !'),
                        _('Please select at least one Task in Pending state to assign manpower'))
        rec = self.browse(cr,uid, ids)[0]
 
        mechanic_ids = [x.id for x in rec.mechanic_ids]
        if not mechanic_ids:
            raise osv.except_osv(
                            _('Warning !'),
                            _('Please select at least one Mechanic or Technical Staff to assign manpower to selected Tasks'))

        for record in task_obj.browse(cr, uid, task_ids):
            mechanics = [x.id for x in record.mechanic_ids]
            for mechanic_id in mechanic_ids:
                if mechanic_id not in mechanics:
                    mechanics.append(mechanic_id)
            if mechanics != [x.id for x in record.mechanic_ids]:
                task_obj.write(cr, uid, [record.id], {'mechanic_ids': [(6, 0, [x for x in mechanics])]})
        return {'type': 'ir.actions.act_window_close'}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
