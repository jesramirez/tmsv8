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
from mx import DateTime

class crm_case(osv.osv):
    _inherit = "crm.lead" 
    _columns = {
        'incident_ref': fields.char('Incident Ref', size=64, required=True),
        'external_ref': fields.char('Ticket Code', size=64),
        'fleet_id': fields.many2one('stock.location', 'Fleet', required = False),
        'parent_fleet_id': fields.related('fleet_id', 'location_id', type='many2one', relation='stock.location', string='Fleet', store=True),
        'is_fleet_expired': fields.related('fleet_id', 'is_expired', type='boolean', string='Is Fleet Expired?'),
        'picking_id': fields.many2one('stock.picking', 'Repair Picking', required = False),
        'incoming_picking_id': fields.many2one('stock.picking', 'Incoming Picking', required = False),
        'outgoing_picking_id': fields.many2one('stock.picking', 'Outgoing Picking', required = False),
        'related_picking_state': fields.related('picking_id', 'state', type="char", string="Related Picking State", readonly=True),
        'related_incoming_picking_state': fields.related('incoming_picking_id', 'state', type="char", string="Related Picking State", readonly=True),
        'related_outgoing_picking_state': fields.related('outgoing_picking_id', 'state', type="char", string="Related Picking State", readonly=True),
        'in_supplier_picking_id': fields.many2one('stock.picking', 'Return To Supplier Picking', required = False),
        'out_supplier_picking_id': fields.many2one('stock.picking', 'Return From Supplier Picking', required = False),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', required = False),
        'product_id': fields.related('prodlot_id', 'product_id', type='many2one', relation='product.product', string='Related Product'),
    }
    
    def default_incident_date(self, cr, uid, context={}):
        now = DateTime.now()
        date = DateTime.DateTime(now.year, now.month, now.day, 0, 0, 0.0)
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    
    _defaults = {
        'incident_ref': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'crm.lead'),
        'date_action_last': default_incident_date,
        }
    
    #def copy(self, cr, uid, id, default=None,context={}):#TODO
    
    
    def onchange_prodlot_id(self, cr, uid, ids, prodlot_id):
        result = {}
        result['value'] = {}
        if not prodlot_id:
            return result

        #TODO: will that work with a product return for repair?
        cr.execute("select stock_location.id from stock_location left join stock_move on location_dest_id = stock_location.id where stock_move.prodlot_id = %s and fleet_type = 'sub_fleet' order by stock_move.date_planned ASC LIMIT 1 " % prodlot_id)
        
        results = cr.fetchone()

        if results and len(results) > 0:
            sub_fleet = self.pool.get('stock.location').browse(cr, uid, results[0])
            result['value'].update({'fleet_id': sub_fleet.id})
            result['value'].update({'partner_id': sub_fleet.parent_partner_id.id})
            result['value'].update({'is_fleet_expired': sub_fleet.is_expired})
            product_id = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id).product_id.id
            result['value'].update({'product_id': product_id})
        else:
            result['value'].update({'fleet_id': False})
            result['value'].update({'partner_id': False})
            result['value'].update({'is_fleet_expired': False})


        return result
         
        
crm_case()
