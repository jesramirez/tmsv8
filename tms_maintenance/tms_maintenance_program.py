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

########################### Columnas : Atributos #######################################################################
    _columns = {
        'name'               : fields.char('Order Number', readonly=True),
        'state'              : fields.selection([('cancel','Cancelled'), ('draft','Draft'), ('open','Open'), ('released','Released'), ('done','Done')],'State'),
        'description'        : fields.char('Description'),
        'notes'              : fields.text('Notes', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),

        'partner_id':     fields.many2one('res.partner','Partner', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),
        'internal_repair' : fields.boolean('Internal Repair', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),
        'date_start': fields.datetime('Scheduled Date Start', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_end': fields.datetime('Scheduled Date End', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'date_start_real': fields.datetime('Scheduled Date Start Real', readonly=True),
        'date_end_real': fields.datetime('Scheduled Date End Real', readonly=True),
        'date': fields.datetime('Date', readonly=True, states={'draft':[('readonly',False)]}),

        'cost_service':    fields.float('Service Cost', readonly=True),
        'parts_cost':      fields.float('Parts Cost', readonly=True),

        ########Many2One###########
        'office_id':       fields.many2one('tms.office','Shop', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'unit_id':       fields.many2one('fleet.vehicle','Unit', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'product_id':    fields.many2one('product.product','Service', required=True, domain=[('tms_category','=','maint_service_type')], readonly=True, states={'draft':[('readonly',False)]}),
        'driver_id':     fields.many2one('hr.employee','Driver',domain=[('tms_category', '=', 'driver')], required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'supervisor_id': fields.many2one('hr.employee','Supervisor',domain=[('tms_category', '=', 'driver')], required=True, readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),        
        'user_id':       fields.many2one('res.users','User', readonly=True), 
              
        'stock_origin_id': fields.many2one('stock.location','Stock Origin', required=True, readonly=True, states={'draft':[('readonly',False)]}),  
        'stock_dest_id':   fields.many2one('stock.location','Stock Dest'),
        
        
        ########One2Many###########
        'activities_ids': fields.one2many('tms.maintenance.order.activity','maintenance_order_id','Tasks', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)], 'released':[('readonly',False)]}),
        #'stock_picking_ids': fields.one2many('stock.piking','tms_order_id','Stock_pickings'),
    }


   
###################################################################################################        

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

        ### Diccionarios de Invoice Lines
        ### Diccionarios de Invoice Lines
        ### Diccionarios de Invoice Lines
        invoice_lines = [] 

        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        ##Se generan los Diccionarios de Inv_line vasados en la lista de actividades
        for activity in activities: 
            
            a = activity['maintenance_order_id']['product_id']['property_stock_production']['valuation_in_account_id']['id']
        
            if not a:
                a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context).id

            a = self.pool.get('account.fiscal.position').map_account(cr, uid, False, a)
            
            descripcion = str(activity['maintenance_order_id']['name']) +str(', ') +str(activity['product_id']['name_template'])
            inv_line = (0,0,{
                        #'name': activity['product_id']['name_template'],
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
                    'origin'            : 'Maaaantenimiento',
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

    def on_change_product_id(self,cr,uid,ids, product_id):
        producto = self.pool.get('product.product').browse(cr, uid, product_id)
        location_id = producto['property_stock_production']['id']
        return {'value':{'stock_dest_id':location_id}}

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
                line.action_process(context)
        
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
        self.calculate_parts_cost(cr,uid,ids)
        self.calculate_cost_service(cr,uid,ids)

        self.write(cr, uid, ids, {'state':'done'})
        self.write(cr, uid, ids, {'date_end_real':time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}) 
        return True 

    def action_released(self,cr,uid,ids,context={}): 

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
                            line.action_cancel()
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
######################### Metodos Manipulacion de Stock_picking ########
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

########################################################################################################################
#####################################  Metodos de prueba Impresion  ####################################################
########################################################################################################################
    def print_stock_picking(self,cr,uid,id, context=None):
        #print '-----------------------------------------------------------------------------------------------------------------------'
        #print '-----------------------------------------------------------------------------------------------------------------------'
        band = self.is_exist_stock_picking(cr,uid,id)
        #print 'Existen stock_picking relacionados a esta ORDEN: '+ str(band)
        #print '-----------------------------------------------------------------------------------------------------------------------'
        #print '-----------------------------------------------------------------------------------------------------------------------'
        
        if band:
            for line in self.get_stock_picking_obj_list(cr,uid,id):
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
        if stock_line:
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
        'state'                 : lambda *a: 'draft',
        'date'                  : lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'user_id'               : lambda obj, cr, uid, context: uid,
        'internal_repair'       : True,
    }

########################### Criterio de ordenamiento ###################################################################
    _order = 'date, name'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
