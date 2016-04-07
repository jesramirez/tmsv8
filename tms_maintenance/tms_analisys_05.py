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
from openerp.tools import sql
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

class tms_analisys_05(osv.Model):
    _name = 'tms.analisys.05'
    _description = "Order Analisys Tms"
    _rec_name='activity_name'
    _auto = False
    _description = 'Order Maintenace Analisys 4'

########################### Columnas : Atributos #######################################################################
    _columns = {
        ######## Integer ###########
        'id':   fields.integer('Product Line ID'),

        ######## Char ###########
        'product_name':       fields.char('Product Name'),
        'activity_name':      fields.char('Activity Name'),
        'order_name':         fields.char('Order Name'),

        ######## Float ###########
        'quantity':        fields.float('Quantity'),
        'price':           fields.float('Price'),
        'total_price':     fields.float('Total_price'),

        ######## Date ###########
        #'date_begin':       fields.datetime('Date Begin'),

        ######## Many2One ###########
        'product_id':        fields.many2one('product.product','Product ID'),
        'activity_id':       fields.many2one('tms.maintenance.order.activity','Activity ID'),
        'order_id':          fields.many2one('tms.maintenance.order','Order ID'),
    }
    
########################### Metodos ####################################################################################

    def init(self, cr):
        sql.drop_view_if_exists(cr,'tms_analisys_05')
        cr.execute("""
            create or replace view tms_analisys_05 as (

select 
	pl.id                                                                       as id,
	pl.id                                                                       as product_line_id, 
	
	(select p.name_template from product_product as p where p.id=pl.product_id) as product_name,
	(select p.id from product_product as p where p.id=pl.product_id)            as product_id,
	
	pl.quantity                                                                 as quantity,
	pl.list_price                                                               as price,
	(pl.quantity*pl.list_price)                                                 as total_price,

	(select p.name_template  from product_product as p where p.id = activity.product_id) as activity_name,
	(activity.id                                                                       ) as activity_id,
	
	o.name                                                                               as order_name,
	o.id                                                                                 as order_id
	
from tms_product_line as pl, tms_maintenance_order_activity as activity, tms_maintenance_order as o
where pl.state like 'delivered' and pl.activity_id = activity.id and o.id = activity.maintenance_order_id      
                
            )
        """)
    
tms_analisys_05()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
