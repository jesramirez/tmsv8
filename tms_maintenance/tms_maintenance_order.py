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

class tms_maintenance_order(osv.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.maintenance.order'
    _description = 'Order Maintenace'

########################### Metodos ####################################################################################
    ########## Copy ##########
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'tms.maintenance.order'),
        })
        return super(tms_maintenance_order, self).copy(cr, uid, id, default, context=context)

    def _get_costs(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):            
            x_manpower = x_spare_parts = y_manpower = y_spare_parts = 0.0            
            for task in record.activities_ids:
                if task.state != 'cancel':
                    for xline in task.product_line_ids:
                        x_spare_parts += xline.cost_amount if not task.external_workshop else 0.0
                        y_spare_parts += xline.cost_amount if task.external_workshop else 0.0
                    if not task.external_workshop:
                        for line in task.control_time_ids:
                            cost_mechanic = line.hr_employee_id.job_id.tms_global_salary or 0.0
                            x_manpower += (cost_mechanic * line.hours_mechanic)
                    else:
                        y_manpower += task.cost_service_external
            res[record.id] = {
                'manpower'             : x_manpower,
                'spare_parts'          : x_spare_parts,
                'manpower_external'    : y_manpower,
                'spare_parts_external' : y_spare_parts,
            }
        return res    

    def _get_order(self, cr, uid, ids, context=None):
        #print "Si entra aqui... "
        result = {}
        for line in self.pool.get('tms.maintenance.order.activity').browse(cr, uid, ids, context=context):
            result[line.maintenance_order_id.id] = True
        #print "result.keys(): ", result.keys()
        return result.keys()

    def _get_activity1(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tms.product.line').browse(cr, uid, ids, context=context):
            result[line.activity_id.maintenance_order_id.id] = True
        #print "result tms.product.line : ", result
        return result.keys()
    
    def _get_activity2(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('tms.activity.control.time').browse(cr, uid, ids, context=context):
            result[line.activity_id.maintenance_order_id.id] = True
        #print "result tms.activity.control.time : ", result
        return result.keys()

    def _get_duration(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = {
                'duration': 0.0,
                'duration_real': 0.0,
            }
            if record.date_end and record.date_start:
                dur1 = datetime.strptime(record.date_end, '%Y-%m-%d %H:%M:%S') - datetime.strptime(record.date_start, '%Y-%m-%d %H:%M:%S')
                x1 = ((dur1.days * 24.0*60.0*60.0) + dur1.seconds) / 3600.0 if dur1 else 0.0
                res[record.id]['duration'] = x1    
            if record.date_end_real and record.date_start_real:
                dur2 = datetime.strptime(record.date_end_real, '%Y-%m-%d %H:%M:%S') - datetime.strptime(record.date_start_real, '%Y-%m-%d %H:%M:%S')
                x2 = ((dur2.days * 24.0*60.0*60.0) + dur2.seconds) / 3600.0 if dur2 else 0.0
                res[record.id]['duration_real'] = x2
        return res


########################### Columnas : Atributos #######################################################################
    _columns = {#maint_service_type
        'name'                 : fields.char('Name', readonly=True),
        'state'                : fields.selection([('cancel','Cancelled'), ('draft','Draft'), ('open','Open'), ('released','Released'), ('done','Done')],'State'),
        'description'          : fields.char('Description'),
        'notes'                : fields.text('Notes', readonly=False, states={'cancel':[('readonly',True)]}),

        'partner_id'           : fields.many2one('res.partner', 'Customer', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}, ondelete='restrict'),
        'internal_repair'      : fields.boolean('Internal Repair', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),
        'date_start'           : fields.datetime('Date Start Sched', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_end'             : fields.datetime('Date End Sched', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_start_real'      : fields.datetime('Date Start Real', readonly=True),
        'date_end_real'        : fields.datetime('Date End Real', readonly=True),
        'date'                 : fields.datetime('Date', readonly=True, states={'draft':[('readonly',False)]}, required=True),
        'duration'             : fields.function(_get_duration, string='Scheduled Duration', method=True, type='float', digits=(18,6), multi=True,
                                                 store = {'tms.maintenance.order': (lambda self, cr, uid, ids, c={}: ids, ['date_start','date_end','date_start_real','date_end_real'], 10)}, help="Scheduled duration in hours"),
        'duration_real'        : fields.function(_get_duration, string='Duration Real', method=True, type='float', digits=(18,6), multi=True,
                                                 store = {'tms.maintenance.order': (lambda self, cr, uid, ids, c={}: ids, ['date_start','date_end','date_start_real','date_end_real'], 10)}, help="Real duration in hours"),

        #'cost_service'         : fields.float('Service Cost', readonly=True),
        #'parts_cost'           : fields.float('Parts Cost', readonly=True),

        'manpower'              : fields.function(_get_costs, method=True, digits_compute=dp.get_precision('Sale Price'), 
                                                 string='Manpower Cost', type='float', multi=True,
                                                 store = {'tms.maintenance.order': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                          'tms.activity.control.time': (_get_activity2, ['state','hours_mechanic'], 10),}),

        'spare_parts'           : fields.function(_get_costs, method=True, digits_compute= dp.get_precision('Sale Price'), 
                                                 string='Spare Parts Cost', type='float', multi=True,
                                                 store = {'tms.maintenance.order': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                          'tms.product.line': (_get_activity1, ['quantity','list_price'], 10),}),

        'manpower_external'     : fields.function(_get_costs, method=True, digits_compute= dp.get_precision('Sale Price'), 
                                                 string='External Manpower Cost', type='float', multi=True,
                                                 store = {'tms.maintenance.order': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                          'tms.maintenance.order.activity': (_get_order, ['cost_service_external'], 10),}),

        'spare_parts_external'  : fields.function(_get_costs, method=True, digits_compute= dp.get_precision('Sale Price'), 
                                                 string='External Spare Parts Cost', type='float', multi=True,
                                                 store = {'tms.maintenance.order': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                          'tms.maintenance.order.activity': (_get_order, ['parts_cost_external'], 10),}),


        ########Many2One###########
        'office_id'              : fields.many2one('tms.office','Office', required=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'unit_id'              : fields.many2one('fleet.vehicle','Unit', required=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'product_id'           : fields.many2one('product.product','Service', required=True, domain=[('tms_category','=','maint_service_type')], readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'driver_id'            : fields.many2one('hr.employee','Driver',domain=[('tms_category', '=', 'driver'),('tms_supplier_driver', '=', False)], required=True, readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'supervisor_id'        : fields.many2one('hr.employee','Supervisor',domain=[('tms_category', '=', 'mechanic')], required=True, readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}, ondelete='restrict'),
        'user_id'              : fields.many2one('res.users','User', readonly=True, ondelete='restrict'), 
              
        'stock_origin_id'      : fields.many2one('stock.location','Stock Origin', required=True, readonly=True, states={'draft':[('readonly',False)]}, domain=[('usage', '=', 'internal')], ondelete='restrict'),
        'stock_dest_id'        : fields.many2one('stock.location','Stock Dest', ondelete='restrict'),


        'accumulated_odometer' : fields.float('Accum. Odometer', readonly=True, states={'draft':[('readonly',False)]}),
        'current_odometer'     : fields.float('Current Odometer', readonly=True, states={'draft':[('readonly',False)]}),
        'program_sequence'     : fields.integer('Preventive Program Seq.', readonly=True, states={'draft':[('readonly',False)]}),
        'maint_program_id'     : fields.many2one('product.product', 'Preventive Program', domain=[('tms_category', '=', 'maint_service_program')], readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),
        'maint_cycle_id'       : fields.many2one('product.product', 'Preventive Cycle', domain=[('tms_category', '=', 'maint_service_cycle')], readonly=True, states={'draft':[('readonly',False)]}, ondelete='restrict'),

        
        ########One2Many###########
        'activities_ids'       : fields.one2many('tms.maintenance.order.activity','maintenance_order_id','Tasks', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),
        #'stock_picking_ids': fields.one2many('stock.piking','tms_order_id','Stock_pickings'),
        'dummy_field'          : fields.boolean('Dummy'),
    }


    ########## Metodo para revisar si el Tipo de Servicio es Preventivo y por tanto, revisar que secuencia del Programa Preventivo le toca a la unidad ##########
    #def check_program(self,cr,uid,ids,context=None):


    ########## Metodos para crear la factura ##########
    def button_generate_invoices(self,cr,uid,ids,context={}):
        this = self.get_current_instance(cr, uid, ids)
        #self.write(cr, uid, ids, {'state':'draft'})

        activities_external_done_not_invoice = self.get_activities_external_done_not_invoice(cr,uid,ids,context)
        activities = activities_external_done_not_invoice 
        #band = False        
        #for line in activities:
        #    band = True
        #if not band:
        #    raise osv.except_osv(_('Warning!'),_('No Existen Actividades Externas en Esta Orden o Ya estan Facturadas')) 
        #partner = activities[0]['supplier_id']

        self.create_invoices_from_activities_not_invoice_and_done(cr,uid,ids, activities)
        #self.create_invoice_based_by_activities(cr,uid,ids, partner, activities)

        

        return True

    def create_invoices_from_activities_not_invoice_and_done(self,cr,uid,ids, activities):
        partners = []

        for activity in activities:
            if not activity['supplier_id'] in partners:
                partners.append(activity['supplier_id'])
        #print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ partner: '+str(partners)

        for partner in partners:
            activities_to_partner = []
            for activity in activities:
                if activity['supplier_id']['id'] == partner['id']:
                    activities_to_partner.append(activity)
            ###COnstruir las facturas basadas en este parner
            self.create_invoice_based_by_activities(cr,uid,ids, partner, activities_to_partner)
            #print 'Parner : '+str(partner)+str(', ........... '+str(activities_to_partner))

    def create_invoice_lines_from_activity(self,cr,uid,ids, activity):
        return invoice_lines

    def get_activities_external_done(self,cr,uid,ids,context={}):
        this = self.get_current_instance(cr, uid, ids)
        external_done = []
        for line in  self.get_activity_lines(cr,uid,ids):
            if line['state'] in 'done':
                if line['external_workshop']:
                    external_done.append(line)
        return external_done

    def get_activities_external_done_not_invoice(self,cr,uid,ids,context={}):
        this = self.get_current_instance(cr, uid, ids)
        not_invoice = []
        for line in self.get_activities_external_done(cr,uid,ids,context):
            #if not line['invoiced']:
            if not line['invoiced']:
                not_invoice.append(line)
        return not_invoice

    def synchronize_invoice_one_to_many(self,cr,uid,ids, factura, invoice_lines):
        this = self.get_current_instance(cr, uid, ids)
        
        #print 'synchronize Factura: '+str(factura)
        #print 'synchronize invoice_lines: '+str(invoice_lines)  

    def create_invoice_based_by_activities(self,cr,uid,ids, partner, activities):
        invoice_lines = [] 
        for activity in activities:             
            a = activity['maintenance_order_id']['product_id']['property_stock_production']['valuation_in_account_id']['id']
            if not a:
                a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context).id
            a = self.pool.get('account.fiscal.position').map_account(cr, uid, False, a)
            
            descripcion = str(activity['maintenance_order_id']['name']) +str(', ') +str(activity['product_id']['name_template'])
            inv_line = (0,0,{
                        'name': descripcion, #Descripcion
                        'origin': activity['maintenance_order_id']['product_id']['name_template'],
                        'account_id': a,
                        'price_unit': activity['cost_service']+activity['parts_cost'],
                        'quantity': 1,
                        'uos_id': activity['product_id'].uos_id.id,
                        'product_id': activity['product_id']['id'],
                        'invoice_line_tax_id': [(6, 0, [x.id for x in activity['product_id'].supplier_taxes_id])],
                        'note': 'Notasss',
                        'account_analytic_id': False,
                       })
            invoice_lines.append(inv_line)

        #################### Generar La Factura ################################
        #################### Generar La Factura ################################
        #################### Generar La Factura ################################

        journal_id = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'purchase')], context=None)
        journal_id = journal_id and journal_id[0] or False
        
        
        vals = {
                    'name'              : 'Invoice TMS Maintenance',
                    'origin'            : 'MRO',
                    'type'              : 'in_invoice',
                    'journal_id'        : journal_id,
                    'reference'         : 'Maintenance Invoice',
                    'account_id'        : partner.property_account_payable.id,
                    'partner_id'        : partner.id,
                    'address_invoice_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                    'address_contact_id': self.pool.get('res.partner').address_get(cr, uid, [partner.id], ['default'])['default'],
                    'invoice_line'      : [x for x in invoice_lines],                      #account.invoice.line
                    #'currency_id'       : data[1],                                     #res.currency
                    'comment'           : 'Siiiiin Comentarios',
                    #'payment_term'      : pay_term,                                    #account.payment.term
                    'fiscal_position'   : partner.property_account_position.id,
                    'date_invoice'      : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }

        invoice_id = self.pool.get('account.invoice').create(cr, uid, vals)
        invoice_obj= self.pool.get('account.invoice').browse(cr,uid,ids,invoice_id)

        #################### Direccionar la Factura generada a las actividades ################################
        for activity in activities:
            activity.write({'invoice_id':invoice_id, 'invoiced':True})
        return invoice_obj
            
 
########################### Metodos ####################################################################################, readonly=True

    ########## Metodos para el costo de productos y servicio ########## 
    def set_cost_service(self,cr,uid,ids, cost_service=0.0):
        self.write(cr, uid, ids, {'cost_service':cost_service})

    def set_parts_cost(self,cr,uid,ids, parts_cost=0.0):
        self.write(cr, uid, ids, {'parts_cost':parts_cost})

    def calculate_parts_cost(self,cr,uid,ids,context=None):
        suma = 0.0
        for line in self.get_activity_lines(cr,uid,ids):
            line.calculate_parts_cost()
            suma = suma + line['parts_cost']
        self.set_parts_cost(cr,uid,ids, suma)

    def calculate_cost_service(self,cr,uid,ids,context=None):
        suma = 0.0
        this = self.get_current_instance(cr, uid, ids)
        for line in self.get_activity_lines(cr,uid,ids):
            line.calculate_cost_service()
            suma = suma + line['cost_service']
        self.set_cost_service(cr,uid,ids, suma)

    def on_change_unit_id(self,cr,uid,ids, unit_id):
        unit = self.pool.get('fleet.vehicle').browse(cr, uid, unit_id)
        return {'value':{ 'accumulated_odometer' : unit.odometer,
                          'current_odometer'     : unit.current_odometer_read,
                          'driver_id'        : unit.employee_id.id,
                          }
                }


    def get_tasks_from_cycle(self, cr, uid, cycle_id, date):
        #print "cycle_id: ", cycle_id
        for cycle in self.pool.get('product.product').browse(cr, uid, [cycle_id]):
            #print cycle.name
            task_ids = []
            for task in cycle.mro_activity_ids:
                task_ids.append([0, False, {'breakdown': True, 
                                             'message_follower_ids': False, 
                                             'supplier_id': False, 
                                             'product_id': task.id, 
                                             'cost_service_external': 0, 
                                             'date_start': date,
                                             'state': 'pending', 
                                             'mechanic_ids': [[6, False, []]], 
                                             'product_line_ids': [], 
                                             'external_workshop': False, 
                                             'parts_cost_external': 0, 
                                             'message_ids': False, 
                                             'date_end': date}])
            for sub_cycle in cycle.mro_cycle_ids:
                task_ids = task_ids + self.get_tasks_from_cycle(cr, uid, sub_cycle.id, date)
        return task_ids



        

    def on_change_product_id(self,cr,uid,ids, product_id, unit_id, date):
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        location_id = product['property_stock_production']['id']        
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, unit_id)
        if product.mro_preventive and vehicle.mro_program_id.id and vehicle.main_odometer_next_service \
                and vehicle.odometer_next_service and vehicle.sequence_next_service and vehicle.cycle_next_service.id:            
            task_ids = self.get_tasks_from_cycle(cr, uid, vehicle.cycle_next_service.id, date)
                
            return {'value':{ 'program_sequence' : vehicle.sequence_next_service,
                              'maint_program_id' : vehicle.mro_program_id.id,
                              'maint_cycle_id'   : vehicle.cycle_next_service.id,
                              'activities_ids'   : task_ids,
                              }
                    }

        return {}

    def on_change_activities_ids(self,cr,uid,ids, activities_ids):
        #print activities_ids
        return {}

    def set_stock_dest(self,cr,uid,ids, stock_dest_id):
        self.write(cr, uid, ids, {'stock_dest_id':stock_dest_id})
        return True

###################################################################################################        

    ########## Metodos para el 'state' ##########
    def action_draft(self,cr,uid,ids,context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def process_activities_in_pending(self, cr, uid, ids, context=None):
        this = self.get_current_instance(cr, uid, ids)
        for line in this['activities_ids']:
            if line['state'] in 'pending':
                line.action_process()
        
    def action_open(self, cr, uid, ids, context=None):
        this = self.get_current_instance(cr, uid, ids)
        band = False
        for band in this['activities_ids']:
            band = True
        if not band:
            raise osv.except_osv(_('Warning!'),_('For Open should be exist Activities Asigned')) 
        
               
        self.write(cr, uid, ids,{'state':'open'}) 
        self.write(cr, uid, ids,{'date_start_real':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}) 
        self.process_activities_in_pending(cr, uid, ids, context)
        return True

    def action_done(self,cr,uid,ids,context={}): 
        #self.calculate_parts_cost(cr,uid,ids)
        #self.calculate_cost_service(cr,uid,ids)
        
        for service_order in self.browse(cr, uid, ids):
            if service_order.maint_program_id.id:
                vehicle_obj = self.pool.get('fleet.vehicle')
                vehicle_obj.write(cr, uid, [service_order.unit_id.id], {'last_preventive_service': service_order.id})
                program_obj = self.pool.get('fleet.vehicle.mro_program')
                prog_id = program_obj.search(cr, uid, [('vehicle_id', '=', service_order.unit_id.id), ('sequence','=', service_order.program_sequence)])
                if prog_id:
                    program_obj.write(cr, uid, prog_id, {'mro_service_order_id'   : service_order.id})
                    prog_ids = program_obj.search(cr, uid, [('vehicle_id', '=', service_order.unit_id.id), ('sequence','>', service_order.program_sequence)], order='sequence')
                    service_trigger = service_order.accumulated_odometer
                    diference = program_obj.read(cr, uid, prog_id, ['diference'])[0]['diference']
                    x = 0
                    for rec in program_obj.browse(cr, uid, prog_ids):
                        prog_next_trigger = rec.trigger + diference
                        program_obj.write(cr, uid, [rec.id], {'trigger' : prog_next_trigger})
                        if not x:
                            #print "service_order.date_end: ", service_order.date_end
                            #date_origin = datetime.strptime(service_order.date_end, '%Y-%m-%d %H:%M:%S')
                            #if not service_order.unit_id.avg_odometer_uom_per_day:
                            #    raise osv.except_osv(_('Warning!'),_('I can not calculate Next Preventive Service Date because you have not defined Average distance/time per day for this vehicle')) 
                            #delta = timedelta(days=int((rec.trigger - prog_last)/service_order.unit_id.avg_odometer_uom_per_day))
                            #date_next_service = date_origin + delta
                            #print "date_next_service : ", date_next_service
                            vehicle_obj.write(cr, uid, [service_order.unit_id.id], \
                                              {'cycle_next_service'     : rec.mro_cycle_id.id, 
                                               #'date_next_service'      : date_next_service, 
                                               'main_odometer_next_service': prog_next_trigger, 
                                               'odometer_next_service'  : service_order.current_odometer + (rec.trigger + diference), 
                                               'sequence_next_service'  : rec.sequence,
                                               })
                        x += 1
                        service_trigger = prog_next_trigger
                vehicle_obj.get_next_service_date(cr, uid, [service_order.unit_id.id])
                        
        
        self.write(cr, uid, ids, {'state':'done', 'date_end_real':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        return True 

    def action_released(self,cr,uid,ids,context={}): 
        prod_line_obj = self.pool.get('tms.product.line')
        exist_activites = self.is_exist_activity_lines(cr,uid,ids)

        ##### Cerrar Todas las Actividades si es posible
        for act in self.get_current_instance(cr, uid, ids)['activities_ids']:
            if act['state'] in 'process':
                act.action_done()
        #####

        if (self.is_exist_activities_done(cr, uid, ids) | self.is_exist_activities_cancel(cr, uid, ids) | (not exist_activites)): ## IF 1
            if not (self.is_exist_activities_process(cr, uid, ids)):                                                              ## IF 2
                if (self.is_exist_activities_pending(cr, uid, ids)):                                                              ## IF 3
                    for line in self.get_activity_lines(cr, uid, ids):                                                            ## For
                        if line['state'] in 'pending':
                            x = 0
                            for prod_line in line.product_line_ids:
                                if prod_line.state=='delivered':
                                    x += 1
                                else:
                                    prod_line_obj.action_cancel(cr, uid, [prod_line.id])
                            if not x:
                                line.action_cancel()
                            else:
                                line.action_done()
                            
                    ## End For
                ## END IF 3
                self.write(cr, uid, ids, {'state':'released'})
                return True
            ## END IF 2
        ## END IF 1

        raise osv.except_osv(_('Warning!'),_('All Activity Lines should be not State Process')) 
        return False  

    def action_cancel(self, cr, uid, ids, context=None): 

        exist_activites = self.is_exist_activity_lines(cr,uid,ids)

        if (self.is_exist_activities_done(cr, uid, ids) | self.is_exist_activities_cancel(cr, uid, ids) | (not exist_activites)): ## IF 1
            if not (self.is_exist_activities_process(cr, uid, ids)):                                                              ## IF 2
                if (self.is_exist_activities_pending(cr, uid, ids)):                                                              ## IF 3
                    for line in self.get_activity_lines(cr, uid, ids):                                                            ## For
                        if line['state'] in 'cancel':                                                    
                            line.action_cancel()
                    ## End For
                ## END IF 3
                self.write(cr, uid, ids, {'state':'cancel'})
                return True
            ## END IF 2
        ## END IF 1

        raise osv.except_osv(_('Warning!'),_('All Activity Lines should be not State Process')) 
        return False  

    ########## Metodo Create ##########
    def create(self, cr, uid, vals, context=None):
        shop = self.pool.get('tms.office').browse(cr, uid, vals['office_id'])
        seq_id = shop.tms_maintenance_seq.id
        if shop.tms_maintenance_seq:
            seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
            vals['name'] = seq_number
            vals['date'] = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        else:
            raise osv.except_osv(_('Order Maintenance Sequence Error !'), _('You have not defined Maintenance Sequence for shop ' + shop.name))
        return super(tms_maintenance_order, self).create(cr, uid, vals, context=context)

    ########## Metodo Create Sequence ##########
    def create_sequence(self, cr, uid, vals, context=None):
        shop = self.pool.get('tms.office').browse(cr, uid, vals['office_id'])
        seq_id = shop.tms_maintenance_seq.id
        secuencia = ''
        if shop.tms_maintenance_seq:
            seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
            vals['name'] = seq_number
            secuencia = seq_number
        else:
            raise osv.except_osv(_('Order Maintenance Sequence Error !'), _('You have not defined Maintenance Sequence for shop ' + shop.name))
        return secuencia

    ########## Metodo Copy ##########
    def copy(self, cr, uid, id, default=None, context=None):
        maintenance = self.browse(cr, uid, id, context=context)
        if not default:
            default = {}
        default.update({
                        'name'          : False, 
                        'state'         : 'draft',
                        })
        return super(tms_maintenance_order, self).copy(cr, uid, id, default, context=context)

##################### Metodos basicosssssssss #####################################################################################
  
    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj

    def get_activity_lines(self,cr,uid,id):
        order_obj = self.get_current_instance(cr, uid, id)       
        activity_lines = order_obj['activities_ids']  
        return activity_lines

    def is_exist_activity_lines(self, cr, uid, id): 
        order_obj = self.get_current_instance(cr,uid,id)
        activity_lines = self.get_activity_lines_obj(cr, uid, id)
        if not activity_lines:
            #print 'Activity line Array es None...................##########################################################'
            return False
        return True   

    def get_activity_lines_obj(self, cr, uid, id):
        return self.get_current_instance(cr, uid, id)['activities_ids']        

    ##########  comprueba el state de un objeto (activity_line) #########
    def get_state_activity(self, activity_line):
        return activity_line['state']

    ##########  Comprueban si existen actividades en cancel, pending, process, done #########

    def is_cancel_activity_line(self, activity_line):
        if self.get_state_activity(activity_line) in 'cancel':
            return True
        return False

    def is_pending_activity_line(self, activity_line):
        if self.get_state_activity(activity_line) in 'pending':
            return True
        return False

    def is_process_activity_line(self, activity_line):
        if self.get_state_activity(activity_line) in 'process':
            return True
        return False

    def is_done_activity_line(self, activity_line):
        if self.get_state_activity(activity_line) in 'done':
            return True
        return False


    ##########  Comprueban si existen actividades en cancel, pending, process, done #########

    def is_exist_activities_cancel(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        for activity_line in activities:
            if self.is_cancel_activity_line(activity_line):
                return True
        #Si no escontro algo en el for y en el if un true, pues devuelve un false
        return False 
    #End Def   

    def is_exist_activities_pending(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        for activity_line in activities:
            if self.is_pending_activity_line(activity_line):
                return True
        #Si no escontro algo en el for y en el if un true, pues devuelve un false
        return False 
    #End Def   

    def is_exist_activities_process(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        for activity_line in activities:
            if self.is_process_activity_line(activity_line):
                return True
        #Si no escontro algo en el for y en el if un true, pues devuelve un false
        return False 
    #End Def   

    def is_exist_activities_done(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        for activity_line in activities:
            if self.is_done_activity_line(activity_line):
                return True
        #Si no escontro algo en el for y en el if un true, pues devuelve un false
        return False 
    #End Def   


    ##########  Comprueban si solo existen actividades en cancel, pending, process, done ######### ('cancel','Cancelled'), ('pending','Pending'), ('process','Process'),('done','Done')   

    def is_only_exist_activities_cancel(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False

        if self.is_exist_activities_pending(cr, uid, id):
            return False
        if self.is_exist_activities_process(cr, uid, id):
            return False
        if self.is_exist_activities_done(cr, uid, id):
            return False

        return self.is_exist_activities_cancel(cr, uid, id)  
    #End Def   

    def is_only_exist_activities_pending(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        
        if self.is_exist_activities_cancel(cr, uid, id):
            return False
        if self.is_exist_activities_process(cr, uid, id):
            return False
        if self.is_exist_activities_done(cr, uid, id):
            return False

        return self.is_exist_activities_pending(cr, uid, id) 
    #End Def   

    def is_only_exist_activities_process(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        
        if self.is_exist_activities_cancel(cr, uid, id):
            return False
        if self.is_exist_activities_pending(cr, uid, id):
            return False
        if self.is_exist_activities_done(cr, uid, id):
            return False

        return self.is_exist_activities_process(cr, uid, id)  
    #End Def   

    def is_only_exist_activities_done(self, cr, uid, id):
        order = self.get_current_instance(cr, uid, id)
        activities = self.get_activity_lines(cr,uid,id)
        if not activities:
            #print 'This order not have activity_lines .........' 
            return False
        
        if self.is_exist_activities_cancel(cr, uid, id):
            return False
        if self.is_exist_activities_pending(cr, uid, id):
            return False
        if self.is_exist_activities_process(cr, uid, id):
            return False

        return self.is_exist_activities_done(cr, uid, id)  
    #End Def  
 
######################### Metodos Manipulacion de Stock_picking ########

    def create_stock_picking(self,cr,uid,id,context=None):
        seq_order=(self.get_current_instance(cr, uid, id))['name']
        id_order=(self.get_current_instance(cr, uid, id))['id']
        vals = {
                'origin':':'+str(seq_order),
                'type':'internal',
                'state':'draft',
                'move_type':'direct', # Delivery Method : partial=direct
                'tms_order_id':''+str(id_order)
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
        id_order=(self.get_current_instance(cr, uid, id))['id']
        args = [('tms_order_id','=',id_order)]

        # busca los stock_picking donde su atributo tms_order_id sea = al order_id, 
        # y devuelve una lista de id de stock_picking que encontro
        stocks_id = self.pool.get('stock.picking').search(cr,uid,args)

        # obtiene una lista de instancias de stock_picking, mediante una lista de ids de stock_piking
        stocks_objs = self.pool.get('stock.picking').browse(cr,uid,stocks_id)  

        return stocks_objs

################################# Metodos Para Escribir Genericos ################################
    def write_custom(self, cr, uid, id, vals, context=None):
        self.write(cr,uid,id,vals,context)

    def set_state(self, cr, uid, id, state, context=None):
        vals = {'state':''+str(state)}
        self.write_custom(cr, uid, id, vals, context)
        
        ######################### Metodos Para Cambiar Estados ################################

    def change_state_to_cancel(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'cancel')

    def change_state_to_draft(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'draft')

    def change_state_to_open(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'open')

    def change_state_to_released(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'released')

    def change_state_to_done(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'done')

#####################################  Metodos de prueba Impresion  ####################################################
    def print_stock_picking(self,cr,uid,id, context=None):
        band = self.is_exist_stock_picking(cr,uid,id)

    def crear_stock_picking(self,cr,uid,id, context=None):
        stock_line = self.create_stock_picking(cr,uid,id,context)
        
########################### Valores por Defecto ########################################################################
    _defaults = {
        'state'                 : lambda *a: 'draft',
        'date'                  : lambda self, cr, uid, context: datetime.utcnow().replace(tzinfo = pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'date_start'            : lambda self, cr, uid, context: datetime.utcnow().replace(tzinfo = pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'date_end'              : lambda self, cr, uid, context: datetime.utcnow().replace(tzinfo = pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'user_id'               : lambda obj, cr, uid, context: uid,
        'internal_repair'       : True,
    }

########################### Criterio de ordenamiento ###################################################################
    _order = 'date, name'

    def _check_unique_draft_open_state_per_vehicle(self, cr, uid, ids, context=None):
        val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'tms_maint_restrict_more_than_one_service_order_in_draft_open', context=context)
        restrict = int(val) or 0
        if restrict:
            for record in self.browse(cr, uid, ids, context=context):
                res = self.search(cr, uid, [('unit_id','=',record.unit_id.id),('state','in',('draft','open')),('office_id','=',record.office_id.id)])
                return not(res and res[0] and res[0] != record.id and record.state in ('draft','open'))
        return True

    def _check_unique_released_state_per_vehicle(self, cr, uid, ids, context=None):
        val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'tms_maint_restrict_more_than_one_service_order_in_released_state', context=context)
        restrict = int(val) or 0
        if restrict:
            for record in self.browse(cr, uid, ids, context=context):
                res = self.search(cr, uid, [('unit_id','=',record.unit_id.id),('state','=','released'),('office_id','=',record.office_id.id)])
                return not(res and res[0] and res[0] != record.id and record.state=='released')
        return True

    
    _constraints = [
        (_check_unique_draft_open_state_per_vehicle, 'Error ! You can''t have more than one Service Order in Draft / Open state for this Vehicle', ['state']),
        (_check_unique_released_state_per_vehicle, 'Error ! You can''t have more than one Service Order in Released state for this Vehicle', ['state']),        
        ]



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
