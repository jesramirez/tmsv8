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

import sys
reload(sys)  
sys.setdefaultencoding('utf8')


class tms_product_line(osv.Model):
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.product.line'
    _description = 'Material Line'
    _rec_name='product_id'
    
    def _get_cost(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.quantity * record.list_price
        return res    

########################### Columnas : Atributos #######################################################################
    _columns = {
        'quantity'      : fields.float('Quantity'),
        'state_activity': fields.related('activity_id','state', type='char', string='Activity State', readonly=True),
        'state'         : fields.selection([('cancel','Cancelled'), ('draft','Draft'), ('pending','Pending'),('delivered','Delivered')],'State'),
        'list_price'    : fields.float('List Price'),
        ######## Many2One ##########################
        'product_id'    : fields.many2one('product.product','Product Material', domain=[('tms_category','=','maint_part')], required=True, ondelete='restrict'),
        'product_uom_id': fields.related('stock_move_id','product_uom',type='many2one', relation='product.uom', string='UdM', readonly=True, store=True),
        'stock_move_id' : fields.many2one('stock.move','Stock Move', required=False, ondelete='restrict'),
        ######## Many2One request One2Many##########
        'activity_id'   : fields.many2one('tms.maintenance.order.activity','Activity id', readonly=True, ondelete='restrict'),
        ######## Related ########
        'office_id'       : fields.related('activity_id','office_id', type='char', string='Shop', readonly=True ,store=True),
        'cost_amount'      : fields.function(_get_cost, string='Cost Amount', method=True, type='float',
                                          digits_compute=dp.get_precision('Sale Price'), multi=False, store=False),
    }
    
    
########################### Metodos ####################################################################################

    def on_change_product_id(self,cr,uid,ids, product_id):
        if not product_id:
            return {'value':{ 'product_uom_id' : False,}}
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        return {'value':{ 'product_uom_id' : product and product.uom_id.id or False,}}



    def set_list_price(self,cr,uid,ids, list_price=0.0):
        self.write(cr, uid, ids, {'list_price':list_price})

    def get_product_product_list_price(self,cr,uid,ids):
        this = self.get_current_instance(cr, uid, ids)
        return this['product_id']['standard_price'] 

    def product_line_set_list_price(self,cr,uid,ids, context=None):
        price = self.get_product_product_list_price(cr,uid,ids)
        self.set_list_price(cr,uid,ids, price)

    ########## Metodos para el 'state' ##########
    def action_draft(self,cr,uid,ids,context={}):
        self.write(cr, uid, ids, {'state':'draft'})
        return True

    def action_pending(self, cr, uid, ids, context=None):
        if self.get_activity_obj(cr,uid,ids)['state'] in ('cancel','pending'):
            raise osv.except_osv(_('Warning!'),_('You can use this Button only when  Activity is in State Process or Done'))
        self.write(cr, uid, ids,{'state':'pending'}) 

        this = self.get_current_instance(cr, uid, ids)
        ############################################## Si es Taller Externo Omitir La Creacion del albaran
        if this['activity_id']['external_workshop']:
            self.write(cr, uid, ids, {'state':'delivered'})
            return True
        ##################################################################
        self.generate_stock_move_to_product_line(cr,uid,ids)
        return True

    def action_delivered(self,cr,uid,ids,context={}): 
        #### cambiar a delivered el stock move de albaran si es que se genero
        product_line = self.get_current_instance(cr, uid, ids)
        stock_move = product_line['stock_move_id']
        if stock_move:
            stock_move.action_done(context)
        #### cambiar el estado de product line a 'delivered'
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        #### cancelar el stock move de albaran si es que se genero
        product_line = self.get_current_instance(cr, uid, ids)
        stock_move = product_line['stock_move_id']
        #print "stock_move: ", stock_move
        if stock_move:
            #stock_move.unlink(context)
            #print "stock_move.state: ", stock_move.state
            #print "stock_move.product_id: ", stock_move.product_id.name
            stock_move.action_cancel(context)
            #print "stock_move.state: ", stock_move.state
            stock_move.unlink(context)
            #res = self.pool.get('stock.move').unlink(cr, uid, [stock_move.id] )
        #### cambiar el estado de product line a 'cancel'
        self.write(cr, uid, ids, {'state':'cancel'})
        return True

    def get_current_instance(self, cr, uid, id):
        obj = None
        for i in self.browse(cr,uid,id):
            obj = i
        #print "obj: ", obj
        return obj

######################### Metodos Manipulacion de Stock_picking ########
######################### Metodos Manipulacion de Stock_picking ########
######################### Metodos Manipulacion de Stock_picking ########

    def create_stock_picking(self,cr,uid,id,context=None):

        product_line_obj = self.get_current_instance(cr, uid, id)
        activity_obj = product_line_obj['activity_id']

        return activity_obj.create_stock_picking()

    def is_exist_stock_picking(self,cr,uid,id):

        product_line_obj = self.get_current_instance(cr, uid, id)
        activity_obj = product_line_obj['activity_id']

        return activity_obj.is_exist_stock_picking()

    def get_stock_picking_obj_list(self,cr,uid,id):
        activity = self.get_activity_obj(cr,uid,id)
        return activity.get_stock_picking_obj_list()

    ################################################
    ################################################

    ################################################
    ################################################

    ################################################
    ################################################

    ################################################
    ################################################
    #def get_stock_picking_open(self,cr,uid,id):
    #    stocks = self.get_stock_picking_obj_list(cr,uid,id)
    #    for line in stocks:
    #        if not self.is_done_stock_picking(line):
    #            if not self.is_cancel_stock_picking(line):
    #                return line
    #    return self.create_stock_picking(cr,uid,id,None)

    def get_stock_picking_open(self,cr,uid,id):
        stocks = self.get_stock_picking_obj_list(cr,uid,id)
        for line in stocks:
            if not self.is_done_stock_picking(line):
                if not self.is_cancel_stock_picking(line):
                    return line
        return self.create_stock_picking(cr,uid,id,None) ##None
    
    def generate_stock_move_to_product_line(self,cr,uid,id):
        stock_picking = self.get_stock_picking_open(cr,uid,id)###########

        #if not stock_picking:
        #    new_stock_picking = True
        #    stock_picking = self.create_stock_picking(cr,uid,id,None)###########  
        #    stock_picking.write({'state': 'confirmed'})      

        stock_move    = self.create_stock_move(cr,uid,id,stock_picking,None)########### 

        stock_move.action_confirm() 

    def is_done_stock_picking(self, stock_picking):
        if stock_picking['state'] == 'done':
            return True
        return False

    def is_cancel_stock_picking(self, stock_picking):
        if stock_picking['state'] == 'cancel':
            return True
        return False
        

    #######################################################
    def get_location_origin_id(self,cr,uid,id):
        return self.get_order_obj(cr,uid,id)['stock_origin_id']['id']
        #return 12

    def get_location_dest_id(self,cr,uid,ids):
        this = self.get_current_instance(cr, uid, ids)
        order = this.get_order_obj()[0]
        #print "order: ", order
        return order.product_id.property_stock_production.id

    def get_location_dest_id2(self,cr,uid,id):
        return self.get_order_obj(cr,uid,id)['stock_dest_id']['id']
        #return 12       

    def create_stock_move(self,cr,uid,id,stock_picking, context=None):

        product_line = self.get_current_instance(cr, uid, id)
        product_id = product_line['product_id']['id']
        qty= product_line['quantity']

        vals = {
                'name':''+str( product_line['product_id']['name_template'] ),
                'product_id' : ''+str( product_id ),
                'product_qty': ''+str(qty),
                'product_uom': product_line['product_id']['product_tmpl_id']['uom_id']['id'],
                'location_id':''+str(self.get_location_origin_id(cr,uid,id)),
                'location_dest_id':''+str(self.get_location_dest_id(cr,uid,id)),  
                ##Add
                ## One2Many Request, Many2One  de Stock_Move a Stock_Picking
                'picking_id': ''+str( stock_picking['id'] ),
                'tms_product_line_id':''+str( product_line['id'] ),
                'maintenance_order_id': product_line['activity_id']['maintenance_order_id']['id'],
                'activity_id'         : product_line['activity_id']['id'],

                ##End Add
               } 

        #print 'Impresion Pruebaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        stock_id  = self.pool.get('stock.move').create(cr, uid, vals, context)
        stock_obj = self.pool.get('stock.move').browse(cr, uid, stock_id)
        ##Add
        ## One2Many de Stock_Picking a Stoc_Move
        stock_move = stock_obj
        stock_picking['move_lines'].append(str(stock_move['id']))
        # 'stock_move_id':
        valores = {
                    'stock_move_id':stock_move['id']
                  }
        self.write(cr,uid,id,valores,None)
        ##End Add
        return stock_obj

        ################################################################################

    def get_activity_obj(self,cr,uid,id):
        return self.get_current_instance(cr, uid, id)['activity_id']      
        
    def get_order_obj(self,cr,uid,id):
        return self.get_activity_obj(cr,uid,id)['maintenance_order_id']

        
        ######################### Metodos Para Escribir Genericos ################################
    def write_custom(self, cr, uid, id, vals, context=None):
        self.write(cr,uid,id,vals,context)

    def set_state(self, cr, uid, id, state, context=None):
        vals = {'state':''+str(state)}
        self.write_custom(cr, uid, id, vals, context)
        
        ######################### Metodos Para Cambiar Estados ################################

    def change_state_to_draft(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'draft')

    def change_state_to_cancel(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'cancel')

    def change_state_to_pending(self, cr, uid, id, context=None):  
        self.set_state(cr, uid, id, 'pending')

    def change_state_to_delivered(self, cr, uid, id, qty, context=None):
        self.write(cr, uid, id, {'quantity' : qty})
        self.set_state(cr, uid, id, 'delivered')
        #print "Si entra aqui..."
        #for rec in self.browse(cr, uid, id):
        #    print "Tambien aqui..."
        #    print "rec.activity_id.id: ", rec.activity_id.id 
        #    self.pool.get('tms.maintenance.order.activity').write(cr, uid, [rec.activity_id.id], {'dummy_field' : not rec.activity_id.dummy_field})
    
        

########################################################################################################################
#####################################  Metodos de prueba Impresion  ####################################################
########################################################################################################################
    def metodo_cambiar_estados_print(self,cr,uid,id, context=None):
        this = self.get_current_instance(cr, uid, id)
        self.change_state_to_pending(cr, uid, id, None)
        
    
    def print_stock_picking(self,cr,uid,id, context=None): 

        product_line_obj = self.get_current_instance(cr, uid, id)
        activity_obj = product_line_obj['activity_id']

        activity_obj.print_stock_picking()

    def crear_stock_picking(self,cr,uid,id, context=None):

        product_line_obj = self.get_current_instance(cr, uid, id)
        activity_obj = product_line_obj['activity_id']

        activity_obj.crear_stock_picking() 

    def crear_stock_move(self,cr,uid,id, context=None):

        stock_picking = self.create_stock_picking(cr,uid,id)  

        stock_move    = self.create_stock_move(cr,uid,id, stock_picking, None)
        
        
########################### Valores por Defecto ########################################################################
    _defaults = {
        'state'                 : lambda *a: 'draft',
        'quantity'              : lambda *a: 1,
        #'user_id'               : lambda obj, cr, uid, context: uid,
    }
########################### Criterio de ordenamiento ###################################################################
    _order = 'stock_move_id'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
