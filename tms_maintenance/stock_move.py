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

# Agregamos manejar una secuencia por cada tienda para controlar viajes 
class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    
    _columns = {
            'tms_product_line_id' : fields.many2one('tms.product.line', 'Product Line', readonly=True),
            'maintenance_order_id': fields.many2one('tms.maintenance.order','Order'),
            'maintenance_order_state' : fields.related('maintenance_order_id','state',type='char',string='MRO Order State',store=True,readonly=True),
            'unit_id'             : fields.related('maintenance_order_id','unit_id',type='many2one',relation='fleet.vehicle',string='Vehicle',store=True,readonly=True),
            'activity_id'         : fields.many2one('tms.maintenance.order.activity','Task'),            
        }

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj  

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################

    def action_confirm(self, cr, uid, ids, context=None):
        #print '==============================================  stock_move----action_confirm'
        #print '==============================================  stock_move----action_confirm'
        #print '==============================================  stock_move----action_confirm'
        arreglo = super(stock_move, self).action_confirm(cr, uid, ids, context)
        for move_line in self.browse(cr,uid,ids):
            if move_line['tms_product_line_id']: 
                if move_line.state in ('confirmed'): 
                    move_line['tms_product_line_id'].change_state_to_pending(context)
        return arreglo    

    def cancel_assign(self, cr, uid, ids, context=None): ##creo que ya quedo
        #print '==============================================  stock_move----cancel_assign' 
        #print '==============================================  stock_move----cancel_assign' 
        #print '==============================================  stock_move----cancel_assign'  
        arreglo = super(stock_move, self).cancel_assign(cr, uid, ids, context) 
        for move_line in self.browse(cr,uid,ids):
            if move_line['tms_product_line_id']:
                if move_line.state in ('cancel'):   
                    move_line['tms_product_line_id'].change_state_to_cancel(context)
        return arreglo   

    def action_cancel(self, cr, uid, ids, context=None):
        #print '==============================================  stock_move----action_cancel'
        #print '==============================================  stock_move----action_cancel'
        #print '==============================================  stock_move----action_cancel'
        band = super(stock_move, self).action_cancel(cr, uid, ids, context)
        for move_line in self.browse(cr, uid, ids, context=context):
            #if move_line.state in ('confirmed', 'waiting', 'assigned', 'draft'):
            if move_line.state in ('cancel'):
                if move_line['tms_product_line_id']:
                    move_line['tms_product_line_id'].change_state_to_cancel() 
        return band

    def force_assign(self, cr, uid, ids, context=None): ##creo que ya quedo    
        #print '==============================================  stock_move----force_assign'
        #print '==============================================  stock_move----force_assign'
        #print '==============================================  stock_move----force_assign'
        arreglo = super(stock_move, self).force_assign(cr, uid, ids, context)
        for move_line in self.browse(cr,uid,ids):
            if move_line['tms_product_line_id']: 
                    if move_line.state in ['assigned']: 
                        move_line['tms_product_line_id'].change_state_to_pending(context)
        return arreglo   

    def action_done(self, cr, uid, ids, context=None): ##creo que ya quedo
        #print '==============================================  stock_move----action_done'
        #print '==============================================  stock_move----action_done'
        #print '==============================================  stock_move----action_done'
        band = super(stock_move, self).action_done(cr, uid, ids, context)
        for move_line in self.browse(cr,uid,ids):
            #print "move_line.tms_product_line_id ", move_line.tms_product_line_id.id
            #print "move_line.state ", move_line.state
            if move_line['tms_product_line_id']:  
                if move_line.state in ['done']:
                    move_line['tms_product_line_id'].change_state_to_delivered(move_line.product_qty ,context)
                    move_line['tms_product_line_id'].product_line_set_list_price()
        return band

    def action_assign(self, cr, uid, ids, *args):
        #print '==============================================  stock_move----action_assign'
        #print '==============================================  stock_move----action_assign'
        #print '==============================================  stock_move----action_assign'
        check_assign = super(stock_move, self).action_assign(cr, uid, ids, *args)
        return check_assign

    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################
    ##########################################################################################

    #def action_confirm(self, cr, uid, ids, context=None): ##creo que ya quedo
    #    arreglo = super(stock_move, self).action_confirm(cr, uid, ids, context)
    #    return arreglo    

    #def cancel_assign(self, cr, uid, ids, context=None): ##creo que ya quedo
    #    for move_line in self.browse(cr,uid,ids):
    #        if move_line['tms_product_line_id']:
    #            move_line['tms_product_line_id'].change_state_to_pending(context) 
    #    arreglo = super(stock_move, self).cancel_assign(cr, uid, ids, context)   
    #    return arreglo   

    #def action_cancel(self, cr, uid, ids, context=None): ##Lo invoca stock_picking desde action_cancel(self, cr, uid, ids, context=None)
    #    for move_line in self.browse(cr, uid, ids, context=context):
    #        if move_line.state in ('confirmed', 'waiting', 'assigned', 'draft'):
    #            if move_line['tms_product_line_id']:
    #                move_line['tms_product_line_id'].change_state_to_cancel() 
    #    band = super(stock_move, self).action_cancel(cr, uid, ids, context)
    #    return band

    #def force_assign(self, cr, uid, ids, context=None): ##creo que ya quedo
    #    for move_line in self.browse(cr,uid,ids):
    #        if move_line['tms_product_line_id']:  
    #            move_line['tms_product_line_id'].change_state_to_pending(context)      
    #    arreglo = super(stock_move, self).force_assign(cr, uid, ids, context)
    #    return arreglo   

    #def action_done(self, cr, uid, ids, context=None): ##creo que ya quedo
    #    band = super(stock_move, self).action_done(cr, uid, ids, context)
    #    for move_line in self.browse(cr,uid,ids):
    #        if move_line['tms_product_line_id']:  
    #            if move_line.state in ['done']:
    #                move_line['tms_product_line_id'].change_state_to_delivered(context)
    #    return band


    def create(self, cr, uid, vals, context=None):
        print "vals: ", vals
        xvals = vals
        if 'tms_product_line_id' not in vals and 'maintenance_order_id' in vals and vals['maintenance_order_id']:
            order = self.pool.get('tms.maintenance.order').browse(cr, uid, [vals['maintenance_order_id']])[0]
            
            xvals['location_id'] = order.stock_origin_id.id
            xvals['location_dest_id'] = order.product_id.property_stock_production.id            
            res = super(stock_move, self).create(cr, uid, xvals, context=context)
        
            prod_line_obj = self.pool.get('tms.product.line')            
            line = {
                    'quantity'      : vals['product_qty'],
                    'state'         : 'draft',
                    'product_id'    : vals['product_id'],
                    'activity_id'   : vals['activity_id'],
                    'stock_move_id' : res,
                    'state'         : 'pending',
                    }
            x = prod_line_obj.create(cr, uid, line)
            
            self.write(cr, uid, [res], {'tms_product_line_id': x})
        elif 'tms_product_line_id' in vals and vals['tms_product_line_id'] and 'maintenance_order_id' in vals: # Check if it's returning products
            res = super(stock_move, self).create(cr, uid, vals, context=context)
            sql = "select count(tms_product_line_id) from stock_move where tms_product_line_id = %s;" % (str(vals['tms_product_line_id']))
            print "sql: ", sql
            cr.execute(sql)
            data = filter(None, map(lambda x:x[0], cr.fetchall()))
            
            if len(data) and data[0]:
                prod_line_obj = self.pool.get('tms.product.line')            
                line = {
                    'quantity'      : float(vals['product_qty']) * -1.0,
                    'state'         : 'draft',
                    'product_id'    : vals['product_id'],
                    'activity_id'   : vals['activity_id'],
                    'stock_move_id' : res,
                    'state'         : 'pending',
                    }
                x = prod_line_obj.create(cr, uid, line)
            
                self.write(cr, uid, [res], {'tms_product_line_id': x})
        else:
            res = super(stock_move, self).create(cr, uid, vals, context=context)
        return res


    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        #print "Si entra en _create_account_move_line"
        res_prev = super(stock_move, self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None)
        res = res_prev
        if move.unit_id and move.unit_id.id:
            res[0][2].update({'vehicle_id': move.unit_id.id})
            res[1][2].update({'vehicle_id': move.unit_id.id})
            if move.picking_id and move.picking_id.tms_order_id and move.picking_id.tms_order_id.driver_id and move.picking_id.tms_order_id.driver_id.id:
                res[0][2].update({'employee_id' : move.picking_id.tms_order_id.driver_id.id})
                res[1][2].update({'employee_id' : move.picking_id.tms_order_id.driver_id.id})
                
        #print "_create_account_move_line: ", res
        return res


stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
