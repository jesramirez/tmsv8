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



# Products => We need flags for some process with TMS Module
class product_product(osv.osv):
    _name = 'product.product'
    _inherit ='product.product'

    _columns = {
#        'mount_court'   : fields.float('Mount Court $:)', digits=(16, 6)),
#        'period_day'    : fields.integer('Period Day', size='2', help="Defines the court day to be taken in agreement this day represent the cutting period of the accounts included in this indirect spending the day always take less than that define or are over the next period will be taken" ),
        'operating_fixed_cost': fields.boolean('Operating Fixed Cost'),
        'administrative_expense': fields.boolean('Administrative Expense'),
        'tms_category_default': fields.boolean('Default', help="Activar Esta casilla para poder Utilizar este producto en Cotizaciones y Acuerdos"),
        'move_ag': fields.boolean('Maiobras', help="Activar Esta casilla para poder Utilizar este producto en Cotizaciones y Acuerdos como Maniobras"),
#         'tms_category':fields.selection([
#                                           ('no_tms_product','No TMS Product'), 
#                                           ('transportable','Transportable'), 
#                                           ('freight','Freight'), 
#                                           ('move','Move'), 
#                                           ('insurance','Insurance'), 
#                                           ('highway_tolls','Highway Tolls'), 
#                                           ('other','Other'),
#                                           ('real_expense','Real Expense'),
#                                           ('madeup_expense','Made-up Expense'),
#                                           ('salary','Salary'),
#                                           ('salary_retention','Salary Retention'),
#                                           ('salary_discount','Salary Discount'),
#                                           ('negative_balance','Negative Balance'),
#                                           ('fuel','Fuel'),
#                                           ('indirect_expense','Indirect Expense (Agreements)'),
#                                           ('maintenance', 'Maintenance'),
#                                           ('tires', 'Tires'),
#                                           ('fixed_operating', 'Fixed Operating Costs'),
#                                           ('administrative_expense', 'Administrative Expenses'),
#                                           ], 'TMS Type', required=True,
#                                           help="""Product Type for using with TMS Module
#   - No TMS Product: Not related to TMS
#   - Transportable: Transportable Product used in Waybills
#   - Freight: Represents Freight Price used in Waybills
#   - Move: Represents Moves Price used in Waybills
#   - Insurance: Represents Insurance for Load used in Waybills
#   - Highway Tolls: Represents Highway Tolls used in Waybills
#   - Other: Represents any other charge for Freight Service used in Waybills
#   - Real Expense: Represent real expenses related to Travel, those that will be used in Travel Expense Checkup.
#   - Made-Up Expense: Represent made-up expenses related to Travel, those that will be used in Travel Expense Checkup.
#   - Fuel: Used for filtering products used in Fuel Vouchers.
#   - Indirect Expense (Agreements): Used to define Accounts for Agreements Indirect Expenses.
#   All of these products MUST be used as a service because they will never interact with Inventory.
# """, translate=True),
        }

  

    _default = {
        'tms_category': lambda *a: 'no_tms_product',
        }
    def button_mount_calculate (self, cr, uid, ids, context=None):
        return True


    def _check_indirect_expenses(self, cr, uid, ids, context=None):
        for quotation in self.browse(cr,uid,ids):
            if quotation.tms_category == 'indirect_expense':
                if quotation.operating_fixed_cost == False and quotation.administrative_expense == False:
                    return False
        return True
    
    def _check_product_type(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids, context=context):
            if record.tms_category in ('move','highway_tolls', 'freight', 'salary','fuel','indirect_expense'):
                if record.type != 'service':
                    return False
        return True

    def _check_tms_default_bool(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        for record in self.browse(cr, uid, ids, context=context):
            if record.tms_category in ('move','highway_tolls', 'insurance', 'fuel'):
                if record.tms_category_default == True:
                    product_id = prod_obj.search(cr, uid, [('tms_category','=',record.tms_category),('tms_category_default','=',True),('id','!=',ids[0])])
                    if product_id:
                        return False
            if record.tms_category == 'real_expense':
                if record.move_ag:
                    product_id = prod_obj.search(cr, uid, [('tms_category','=',record.tms_category),('move_ag','=',True),('id','!=',ids[0])])
                    if product_id:
                        return False
        return True


    def onchange_tms_category(self, cr, uid, ids, tms_category):
            val = {}
            if not tms_category or tms_category=='standard':
                return val
            result =    super(product_product, self).onchange_tms_category(cr, uid, ids, tms_category)
            val= result.get('value',{})
            print "################################################################## VALLLLLLLLLLLLLLLLLLLLLL", val
            print "################################################################## VALLLLLLLLLLLLLLLLLLLLLL", val
            print "################################################################## VALLLLLLLLLLLLLLLLLLLLLL", val
            print "################################################################## VALLLLLLLLLLLLLLLLLLLLLL", val
            print "################################################################## VALLLLLLLLLLLLLLLLLLLLLL", val
            if tms_category in ['transportable', 'freight', 'move','insurance','highway_tolls','other','real_expense','madeup_expense', 'salary', 'salary_retention', 'salary_discount', 'negative_balance','indirect_expense']:
                val = {
                      'type': 'service',
                      'procure_method':'make_to_stock',
                      'supply_method': 'buy',
                      'purchase': False,
                      'sale': False,
                      }
            return {'value': val}

    # _constraints = [
    #   (_check_indirect_expenses, 'Error ! Al Seleccionar el tipo de producto como gasto indirecto es necesario seleccionar si es Gasto Administrativo o Costo Fijo Operativo', ['Gasto Indirecto']),
    #   (_check_product_type, 'Error ! Debes Definir el producto de tipo Servicio', ['tms_category']),
    # ]

    _constraints = [
    (_check_indirect_expenses, 'Error ! Al Seleccionar el tipo de producto como gasto indirecto es necesario seleccionar si es Gasto Administrativo o Costo Fijo Operativo', ['Gasto Indirecto']),
    (_check_tms_default_bool, 'Error ! Solo se puede Definir un solo producto por Default', ['Tipo de Producto tms_category']),
    ]

product_product()