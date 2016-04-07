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
class product_template(osv.osv):
    _inherit ='product.template'

    _columns = {
        'tms_category':fields.selection([
                                          ('no_tms_product','No TMS'), 
                                          ('transportable','Transportable'), 
                                          ('freight','Freight'), 
                                          ('move','Move (Freight Related)'), 
                                          ('insurance','Insurance (Freight Related)'), 
                                          ('highway_tolls','Highway Tolls (Freight Related)'), 
                                          ('other','Other (Freight Related)'),
                                          ('real_expense','Real Expense (Travel Expense Related)'),
                                          ('madeup_expense','Made-up Expense (Travel Expense Related)'),
                                          ('salary','Salary (Travel Expense Related)'),
                                          ('salary_retention','Salary Retention (Travel Expense Related)'),
                                          ('salary_discount','Salary Discount (Travel Expense Related)'),
                                          ('negative_balance','Negative Balance (Travel Expense Related)'),
                                          ('fuel','Fuel (Travel Expense Related)'),
                                          ('indirect_expense','Indirect Expense (Agreements)'),
                                          ('maint_part','Spare Part (MRO Related)'),
                                          ('maint_activity','Task (MRO)'),
                                          ('maint_service_type','Work Order Types (MRO)'),
                                          ('maint_service_cycle','Service Cycle (MRO)'),
                                          ('maint_service_program','Service Program (MRO)'),
                                          ], 'TMS Type', required=True,
                                          help="""Product Type for using with TMS Module
  - No TMS: Not related to TMS
  - Transportable: Transportable Product used in Waybills
  - Freight: Represents Freight Price used in Waybills
  - Move (Freight Related): Represents Moves Price used in Waybills
  - Insurance (Freight Related): Represents Insurance of Load used in Waybills
  - Highway Tolls (Freight Related): Represents Highway Tolls used in Waybills
  - Other (Freight Related): Represents any other charge for Freight Service used in Waybills
  - Real Expense: Real expenses related to Travel Expense Checkup.
  - Made-Up Expense: Made-up expenses related to Travel Expense Checkup.
  - Fuel: Fuel related to Travel Expenses used in Fuel Vouchers.
  - Indirect Expense (Agreements): Used to get Expenses registered in Accounts for Agreements.
  - Spare Part (MRO): Parts used for maintenance services.
  - Task (MRO): Tasks related to maintenance services.
  - Work Order Types (MRO): Different types of maintenance services
  - Service Cycles (MRO): Maintenance Cycles
  - Service Program (MRO): Different Service Programs
  All of these products (except for MRO Spare Part) MUST be used as a service because they will never interact with Inventory.
""", translate=True),

        'mro_activity_ids' : fields.many2many('product.product',  'tms_maintenance_program_activity_rel',  'product_id', 'activity_id',  'Tasks', domain=[('tms_category','=','maint_activity')]),
        'mro_frequency'    : fields.integer('Frequency'),
        'mro_preventive'   : fields.boolean('Preventive MRO'),
        'mro_cycle_ids'    : fields.many2many('product.product',  'tms_maintenance_cycle_program_rel',  'program_id', 'program_child_id',  'Service Programs', domain=[('tms_category','=','maint_service_cycle')]),
  
        }


    def _check_tms_product(self,cr,uid,ids,context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.tms_category in ['transportable']:
                return (record.type=='service'  and not record.sale_ok and not record.purchase_ok)
            elif record.tms_category in ['freight', 'move','insurance','highway_tolls','other']:
                return (record.type=='service' and record.sale_ok)
            elif record.tms_category in ['real_expense', 'madeup_expense', 'salary', 'salary_retention', 'salary_discount', 'negative_balance', 'indirect_expense']:
                return (record.type=='service' and record.purchase_ok)
            elif record.tms_category in ['fuel']:
                return (record.type=='product'and record.purchase_ok)
            elif record.tms_category in ['maint_activity', 'maint_service_program', 'maint_service_type', 'maint_service_cycle']:
               return (record.type=='service' and not record.purchase_ok)
            elif record.tms_category in ['maint_part']:
                return (record.type=='product' and record.purchase_ok)
            else:
                True

        return True


    _constraints = [
        (_check_tms_product, 'Error ! Product is not defined correctly...Please see TMS Category tooltip...', ['tms_category'])
        ]




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
