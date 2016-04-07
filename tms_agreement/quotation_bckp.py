# -*- encoding: utf-8 -*-
##############################################################################
#	
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.	 
#
##############################################################################

from osv import osv, fields
import time
import dateutil
import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, time, timedelta
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import decimal_precision as dp
import netsvc
import openerp
import calendar
from pytz import timezone
# Extra data fields for Waybills & Agreement
# Factors

class factor_quotation(osv.osv):
	_name = "factor.quotation"
	_description = "Factors to calculate Payment Client charge"

	def _get_total(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		total = 0.0
		for factor in self.browse(cr, uid, ids, context=context):
			if factor.factor_type != 'special':
				res[factor.id] = factor.factor * factor.variable_amount + (factor.fixed_amount if factor.mixed else 0.0)
			else: 
				res[factor.id] = 0.0 # Pendiente generar cálculo especial
		return res


	_columns = {		
		'name'		  : fields.char('Name', size=64, required=True),
		'category'	  : fields.selection([
										('driver', 'Driver'),
										('customer', 'Customer'),
										('supplier', 'Supplier'),
										], 'Type', required=True),

		'factor_type'   : fields.selection([
										('distance', 'Distance Route (Km/Mi)'),
										('distance_real', 'Distance Real (Km/Mi)'),
										('weight', 'Weight'),
										('travel', 'Travel'),
										('qty', 'Quantity'),
										('volume', 'Volume'),
										('percent', 'Income Percent'),
										('special', 'Special'),
										], 'Factor Type', required=True, help="""
For next options you have to type Ranges or Fixed Amount
 - Distance Route (Km/mi)
 - Distance Real (Km/Mi)
 - Weight
 - Quantity
 - Volume
For next option you only have to type Fixed Amount:
 - Travel
For next option you only have to type Factor like 10.5 for 10.50%:
 - Income Percent
For next option you only have to type Special Python Code:
 - Special
						"""),
		
		'framework'	 : fields.selection([
								('Any', 'Any'),
								('Unit', 'Unit'),
								('Single', 'Single'),
								('Double', 'Double'),
								], 'Framework', required=True),

		'range_start'   : fields.float('Range Start',   digits=(16, 4)),
		'range_end'	 : fields.float('Range End',	 digits=(16, 4)),
		'factor'		: fields.float('Factor',		digits=(16, 4)),
		'fixed_amount'  : fields.float('Fixed Amount', digits=(16, 4)),
		'mixed'		 : fields.boolean('Mixed'),
		'factor_special_id': fields.many2one('tms.factor.special', 'Special'),

        'expense_id'    : fields.many2one('tms.expense', 'Expense', required=False, ondelete='cascade'), #, select=True, readonly=True),
        'route_id'      : fields.many2one('tms.route',   'Route', required=False, ondelete='cascade'), #, select=True, readonly=True),
        'travel_id'     : fields.many2one('tms.travel', 'Travel', required=False, ondelete='cascade'), #, select=True, readonly=True),

		'variable_amount' : fields.float('Variable',  digits=(16, 4)),
		'total_amount'  : fields.function(_get_total, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total', type='float',
											store=True),
		'sequence'	  : fields.integer('Sequence', help="Gives the sequence calculation for these factors."),
		'notes'		 : fields.text('Notes'),
		'control'	   : fields.boolean('Control'),
        'driver_helper' : fields.boolean('For Driver Helper'),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID'),
		'agreement_id': fields.many2one('tms.agreement', 'Agreement ID'),
	}

	_defaults = {
		'mixed'			 : False,
		'sequence'		  : 10,
		'variable_amount'   : 0.0,
		'framework'		 : 'Any',
		'category'		  : 'customer',
	}

	_order = "sequence"

	def on_change_factor_type(self, cr, uid, ids, factor_type):
		if not factor_type:
			return {'value': {'name': False}}
		values = {
					'distance'  : _('Distance Route (Km/Mi)'),
					'distance_real'  : _('Distance Real (Km/Mi)'),
					'weight'	: _('Weight'),
					'travel'	: _('Travel'),
					'qty'	   : _('Quantity'),
					'volume'	: _('Volume'),
					'percent'   : _('Income Percent'),
					'special'   : _('Special'),
			}
		return {'value': {'name': values[factor_type]}}

	def calculate(self, cr, uid, record_type, record_ids, context=None):
		result = 0.0
		if record_type == 'agreement':
			#print "==================================="
			#print "Calculando"
			agreement_obj = self.pool.get('tms.agreement')
			for agreement in agreement_obj.browse(cr, uid, record_ids, context=context):  # No soporta segundo operador
				print "Recorriendo Agreements"
				for factor in (agreement.agreement_customer_factor if calc_type=='client' else agreement.agreement_driver_factor if calc_type=='driver' else agreement.agreement_supplier_factor):
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'): 
						print "Tipo Distancia"
						if not agreement.route_id:
							raise osv.except_osv(
								_('Could calculate Amount for Agreement !'),
								_('Agreement %s is not assigned to Route') % (agreement.name))
						print agreement.route_id.distance
						x = (float(agreement.route_id.distance) if factor.factor_type=='distance' else 0.0)

					elif factor.factor_type == 'weight':
						product_weight = 0.0
						for weight in agreement.agreement_shipped_product:
							product_weight += weight.product_uom_qty
						print "agreement.product_weight", product_weight
						if product_weight <= 0.0:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Weight or Product Qty = 0.0' % agreement.name))

						x = float(product_weight)

					elif factor.factor_type == 'qty':
						product_weight = 0.0
						for weight in agreement.agreement_shipped_product:
							product_weight += weight.product_uom_qty
						print "agreement.product_weight", product_weight
						if product_weight <=0.0 :
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with Quantity > 0.0') % (agreement.name))

						x = float(product_weight)

					elif factor.factor_type == 'volume':
						product_weight = 0.0
						for weight in agreement.agreement_shipped_product:
							product_weight += weight.product_uom_qty
						print "agreement.product_weight", product_weight
						if product_weight <=0.0 :
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('Agreement %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (agreement.name))

						x = float(product_weight)

					elif factor.factor_type == 'percent':
						x = float(agreement.amount_subtotal) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					
					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0)+ (factor.factor * x if factor.factor_type != 'special' else x)) if (((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) and factor.driver_helper==driver_helper) else 0.0
					#print "factor.fixed_amount : ", factor.fixed_amount
					#print "factor.mixed : ", factor.mixed
					#print "factor.factor_type : ", factor.factor_type
					#print "factor.factor : ", factor.factor
					#print "x : ", x
					print "################################################# RESULTADO =================", result
					print "################################################# RESULTADO =================", result
		return result
	
factor_quotation()




class tms_quotation(osv.Model):
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_name = 'tms.quotation'
	_rec_name = 'sequence'
	_description = 'Quotations for TMS'

	def copy(self, cr, uid, id, default=None, context=None):
		if not default:
			default = {}
		default.update({
			'sequence': self.pool.get('ir.sequence').get(cr, uid, 'tms.quotation'),
		})
		return super(tms_quotation, self).copy(cr, uid, id, default, context=context)


	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		cur_obj = self.pool.get('res.currency')
		res = {}
		for quotation in self.browse(cr, uid, ids, context=context):
			res[quotation.id] = {
				'operating_amount_all': 0.0,
				'administrative_amount_all': 0.0,

			}
			operating_amount_all = 0.0
			administrative_amount_all = 0.0

			for operating in quotation.operating_cost_ids:
				operating_amount_all += operating.travel_days

			for administrative in quotation.administrative_expenses_ids:
				administrative_amount_all += administrative.travel_days
			res[quotation.id]['operating_amount_all'] = operating_amount_all
			res[quotation.id]['administrative_amount_all'] = administrative_amount_all

		return res
	_columns = {
		'name': fields.char('Description of the Route', size=128, required=True),
		'partner_id': fields.many2one('res.partner', 'Customer', required=True, readonly=False),
		'agreement_id': fields.many2one('tms.agreement', 'Agreement', readonly=True, help="Representa el Acuerdo que se genero a partir de esta Cotizacion"),
		'type_armed': fields.selection([('tractor','Drive Unit'), ('one_trailer','Single Trailer'), ('two_trailer','Double Trailer')], 'Type of Armed', required=True),
		'days': fields.integer('Travel Days', required=True),
		'month_travel': fields.float('Month Travels', digits=(4,2), required=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_kms': fields.float('Total Kms', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_tons': fields.float('Total Tonnes', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_security': fields.float('Total Insurance', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'total_ingr': fields.float('Total Income', digits=(4,2), readonly=True), # Este campo se debe calcular por onchange o por funcion al guardar
		'unit_ids': fields.many2one('tms.unit.category', 'Unit Category',required=True),

		############ ---  ROUTES FOR QUOTATION --- ############
		'route_ids': fields.one2many('tms.quotation.route','quotation_id'),
		'sequence': fields.char('Sequence', size=64),

		############ --- PARAMETERS ---######################
		'parameter_id': fields.many2one('tms.quotation.config', 'Parameters', required=True),

		########### ---- COSTOS FIJOS OPERATIVOS ---- #########
		'operating_cost_ids': fields.one2many('tms.operating.cost', 'quotation_id' ,'Fixed Operating Costs'),
		'load_operating_cost': fields.boolean('Cargar Costos Operativos Automaticamente'),
		'amount_acumulated_fixed': fields.float('Amount Acumulated Fixed', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_monthly_fixed': fields.float('Amount Acumulated Monthly', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_daily_fixed': fields.float('Amount Acumulated Daily', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_travel_days_fixed': fields.float('Amount Acumulated Travel Days', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_percentage_fixed': fields.float('Amount Acumulated Percentage', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena

		######### ---- SUMATORIA DE LOS GASTOS FIJOS Y ADMINISTRATIVOS ---- #######
		'operating_amount_all': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'),string='Operating Amount', multi='sums', store=True),
		'administrative_amount_all': fields.function(_amount_all, method=True, digits_compute= dp.get_precision('Sale Price'),string='Administratives Exenses Amount', multi='sums', store=True),

		########### ---- COSTOS VARIABLES OPERATIVOS ---- #########
		'diesel_cost': fields.float('Cost of Diesel', digits=(9,2), required=True),
		'diesel_mtto_monthly': fields.char('Daily Average', size=0, readonly=False),
		'diesel_mtto_travel_days': fields.char('Travel Days', size=0, readonly=False),
		'diesel_mtto_percent': fields.char('%', digits=(9,2), size=0, readonly=False),

		'factor_mtto': fields.float('Maintenance Factor', digits=(9,2), required=True),
		'factor_mtto_monthly': fields.float('Daily Average', digits=(9,2), required=False, help="Maintenance Factor Daily Average"),
		'factor_mtto_travel_days': fields.float('Travel Days', digits=(9,2), required=False, help="Maintenance Factor Travel Days"),
		'factor_mtto_percent': fields.float('%', digits=(9,2), required=False, help="Maintenance Factor %"),

		'factor_tires': fields.float('Tires Factor', digits=(9,2), required=True),
		'factor_tires_monthly': fields.float('Daily Average', digits=(9,2), required=False, help="Tires Factor Daily Average"),
		'factor_tires_travel_days': fields.float('Travel Days', digits=(9,2), required=False, help="TiresFactor Travel Days"),
		'factor_tires_percent': fields.float('%', digits=(9,2), required=False, help="Tires Factor %"),

		'performance_loaded': fields.float('Performance Loaded', digits=(9,2), required=True),
		'uncharged_performance': fields.float('Uncharged Performance', digits=(9,2), required=True),

		'liters_diesel': fields.float('Liters of Diesel', digits=(9,2), required=True),

		'money_diesel': fields.char('$ Diesel', size=0, readonly=True),
		'amount_total_diesel': fields.float('$ Diesel', digits=(9,2), required=False),
		'diesel_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'diesel_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'diesel_percent': fields.float('Percentage', digits=(9,2), required=False),

		'total_highway_toll': fields.float('Highway Tolls', digits=(9,2), required=True), #### Se calculara en base a las casetas que se tengan definidas en cada ruta
		'toll_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'toll_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'toll_percent': fields.float('Percentage', digits=(9,2), required=False),

		'operator_salary': fields.float('Operator Salary', digits=(9,2), required=False), #### Se calculara en base al sueldo definido en cada ruta
		'salary_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'salary_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'salary_percent': fields.float('Percentage', digits=(9,2), required=False),

		'move_amount': fields.float('Shunting', digits=(9,2), required=False), #### Se calculara en base al sueldo definido en cada ruta
		'move_monthly': fields.float('Daily Average', digits=(9,2), required=False),
		'move_travel_days': fields.float('Travel Days', digits=(9,2), required=False),
		'move_percent': fields.float('Percentage', digits=(9,2), required=False),

		'amount_daily_variable': fields.float('Total Daily', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_travel_days_variable': fields.float('Total Travel Days', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_percentage_variable': fields.float('Total %', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena

		######## ---- GASTOS ADMINISTRATIVOS ----- ################
		'administrative_expenses_ids': fields.one2many('tms.administrative.cost', 'quotation_id' ,'Administrative Expenses'),
		'load_administrative_expenses': fields.boolean('Cargar Gastos Administrativos'),
		'amount_acumulated_administrative': fields.float('Amount Acumulated Fixed', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_monthly_administrative': fields.float('Amount Acumulated Monthly', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_daily_administrative': fields.float('Amount Acumulated Daily', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_travel_days_administrative': fields.float('Amount Acumulated Travel Days', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena
		'amount_percentage_administrative': fields.float('Amount Acumulated Percentage', digits=(9,2), required=False), ### Seran campos calculados ?? valdra la pena

		####### ---- SUMMARY ----- ########
		'summary_income_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_income_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_income_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_expenditures_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_expenditures_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_expenditures_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_utility_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_utility_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_utility_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_km_productive_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_km_productive_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_km_productive_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_mk_shot_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_mk_shot_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_mk_shot_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_cost_km_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_cost_km_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_cost_km_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_utility_km_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_utility_km_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_utility_km_percent': fields.float('Percentage', digits=(3,2) ),

		'summary_margin_monthly': fields.float('Daily Average', digits=(9,2) ),
		'summary_margin_travel_days': fields.float('Travel Days', digits=(9,2) ),
		'summary_margin_percent': fields.float('Percentage', digits=(3,2) ),


		####### --- Notas ----- #############
		'notes': fields.text('Notes'),
		'state': fields.selection([('draft','Draft'), ('confirmed','Confirmed'), ('done','Done'), ('cancel','Cancelled')], 'Quotation State', readonly=True),

		###### ---- FACTORES ---- ######
		#'factor_ids': fields.one2many('factor.quotation', 'quotation_id', 'Factors Quote'),

		###### ---- DATOS PARA LA VISTA KANBAN ---- ########
		'image': fields.related('partner_id', 'image', type="binary", string="Logo", readonly=True),
		'image_medium': fields.related('partner_id', 'image_medium', type="binary", string="Logo"),
		'image_small': fields.related('partner_id', 'image_small', type="binary", string="Logo"),
		'currency_id': fields.many2one('res.currency','Currency',states={'confirmed': [('readonly', True)],'done':[('readonly',True)],'cancel':[('readonly',True)]}, required=True),


	}


	def _get_parameter(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		parameter_obj = self.pool.get('tms.quotation.config')
		parameter_ids = parameter_obj.search(cr, uid, [], limit=1)
		if not parameter_ids:
			raise osv.except_osv(
						_('Error !'),
						_('Configuration Error Found no Predefined Parameters !!!'))
		return parameter_ids[0]

	_defaults = {
	#'sequence': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'tms.quotation'),
	'type_armed': 'tractor',
	'parameter_id': _get_parameter,
	'days': 1,
	'state': 'draft',
	'load_operating_cost': True,
	'load_administrative_expenses': True,
	'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,

	}

	_order = "sequence desc"

	def create(self, cr, uid, vals, context=None):
		seq_number = self.pool.get('ir.sequence').get(cr, uid, 'tms.quotation'),
		vals['sequence'] = seq_number[0]
		return super(tms_quotation, self).create(cr, uid, vals, context=context)

	def action_calculate(self, cr, uid, ids, context=None):
		product_obj = self.pool.get('product.product')
		for rec in self.browse(cr, uid, ids, context=context):
			total_kms = 0.0
			total_income = 0.0
			total_insurance = 0.0
			total_tons = 0.0
			for routes in rec.route_ids:
				total_kms += routes.kms
				total_tons += routes.product_weight
				total_insurance += routes.insurance
				# if not rec.factor_ids:
				total_income += routes.income
				# else:
				# 	for factor in rec.factor_ids:
				# 		factor_obj = self.pool.get('factor.quotation')
				#		total_income = factor_obj.calculate(cr, uid, 'quotation', ids, context) 
			rec.write({ 'total_kms': total_kms, 'total_tons': total_tons, 'total_security': total_insurance,'total_ingr': total_income})

			# for factor in rec.factor_ids:
			# 	factor_obj = self.pool.get('factor.quotation')
			# 	total_income = factor_obj.calculate(cr, uid, 'quotation', ids, context) 

			total_acumulated_fixed = 0.0
			total_acumulated_monthly = 0.0
			total_acumulated_dailt = 0.0
			total_acumulated_days = 0.0
#			total_acumulated_percentage = 0.0
			for fixes in rec.operating_cost_ids:
				total_acumulated_fixed += fixes.acumulated_moth
				total_acumulated_monthly += fixes.average_moth
				total_acumulated_dailt += fixes.daily_average
				travel_days = fixes.daily_average * rec.days
				fixes.write({'travel_days':travel_days})
				total_acumulated_days += travel_days
#				total_acumulated_percentage += fixes.percent
			rec.write({ 'amount_acumulated_fixed': total_acumulated_fixed, 
						'amount_monthly_fixed': total_acumulated_monthly, 
						'amount_daily_fixed': total_acumulated_dailt, 
						'amount_travel_days_fixed': total_acumulated_days, 
						#'amount_percentage_fixed': total_acumulated_percentage
						})

			########### ---- COSTOS VARIABLES OPERATIVOS ---- #########
			#### OBTENIENDO LOS COSTOS VARIABLES
			factor_mtto_travel_days = rec.factor_mtto * total_kms
			factor_mtto_monthly = factor_mtto_travel_days / rec.days
			print "########################### FACTOR MTTO", factor_mtto_monthly
			factor_tires_travel_days = rec.factor_tires * total_kms
			factor_tires_monthly = factor_tires_travel_days / rec.days
			print "########################### FACTOR TIRES", factor_tires_monthly
			performance_loaded = 0.0
			uncharged_performance = 0.0
			
			for performance in rec.route_ids:
				if performance.uncharged == True or performance.product_weight == 0.0:
					result_loader = performance.kms / rec.uncharged_performance
					performance_loaded += result_loader
				elif performance.uncharged == False or performance.product_weight > 0.0:
					result_uncharged = performance.kms / rec.performance_loaded
					performance_loaded += result_uncharged
			performance_total = performance_loaded + uncharged_performance

			diesel_travel_days = performance_total * rec.diesel_cost
			diesel_monthly = diesel_travel_days / rec.days
#			diesel_percent = (rec.total_ingr/performance_total) * 100

			rec.write({ 'factor_mtto_monthly': factor_mtto_monthly, 
						'factor_mtto_travel_days': factor_mtto_travel_days, 
						'factor_tires_travel_days': factor_tires_travel_days, 
						'factor_tires_monthly': factor_tires_monthly, 
						'liters_diesel': performance_total,
						'diesel_travel_days' : diesel_travel_days,
						'diesel_monthly': diesel_monthly,
#						'diesel_percent': 0.0,

						})

			####### ---- CALCULANDO LAS CASETAS ---- ###################

			total_highway_toll = 0.0

			for highway in rec.route_ids:
				amount_axis_credit = 0.0
				amount_axis = 0.0
				for toll in highway.route_id.tms_route_tollstation_ids:
					if toll.credit:
						for axis in toll.tms_route_tollstation_costperaxis_ids:
							print "####################################### MONTOS", axis.cost_credit
							if axis.unit_type_id.id == rec.unit_ids.id:
								amount_axis_credit += axis.cost_credit
					else:
						for axis in toll.tms_route_tollstation_costperaxis_ids:
							print "####################################### MONTOS", axis.cost_cash
							if axis.unit_type_id.id == rec.unit_ids.id:
								amount_axis_credit += axis.cost_cash

					amount_toll_station_route = amount_axis_credit + amount_axis
					print "################################################# TOTAL Highway Tolls", amount_toll_station_route
					total_highway_toll += amount_toll_station_route
				print "################################################# TOTAL Highway Tolls", total_highway_toll

			toll_monthly = 0.0
#			toll_percent = 0.0
			if total_highway_toll > 0.0 :
				toll_monthly = total_highway_toll / rec.days

			rec.write({ 'total_highway_toll': total_highway_toll if total_highway_toll > 0.0 else 0.0,
						'toll_travel_days': total_highway_toll if total_highway_toll > 0.0 else 0.0,
						'toll_monthly': toll_monthly,
#						'toll_percent': toll_percent,
						})

			###### ---- CALCULANDO EL FACTOR OPERADOR --- #####
			operator_salary = 0.0

			for quotation in rec.route_ids:
				result = 0.0
				for factor in (quotation.route_id.expense_driver_factor):
					print "Recorriendo factors"
					print "Tipo de factor: ", factor.factor_type
					if factor.factor_type in ('distance', 'distance_real'):
						print "Tipo Distancia"
						print "####################################################### DISTANCIA"
						if not quotation.route_id.id:
							raise osv.except_osv(
								_('Could calculate Freight amount for quotation !'),
								_('quotation %s is not assigned to a Travel') % (quotation.name))
						print quotation.route_id.distance
						x = (float(quotation.route_id.distance) if factor.factor_type=='distance' else float(quotation.route_id.distance_extraction)) if factor.framework == 'Any' or factor.framework == quotation.route_id.framework else 0.0
					elif factor.factor_type == 'weight':
						print "quotation.product_weight", quotation.product_weight
						if not quotation.product_weight:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('quotation %s has no Products with UoM Category = Weight or Product Qty = 0.0' % quotation.name))

						x = float(quotation.product_weight)

					elif factor.factor_type == 'qty':
						if not quotation.product_qty:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('quotation %s has no Products with Quantity > 0.0') % (quotation.name))

						x = float(quotation.product_qty)

					elif factor.factor_type == 'volume':
						if not quotation.product_volume:
							raise osv.except_osv(
								_('Could calculate Freight Amount !'),
								_('quotation %s has no Products with UoM Category = Volume or Product Qty = 0.0') % (quotation.name))

						x = float(quotation.product_volume)

					elif factor.factor_type == 'percent':
						x = float(quotation.amount_freight) / 100.0

					elif factor.factor_type == 'travel':
						x = 0.0

					elif factor.factor_type == 'special':
						exec factor.factor_special_id.python_code

					result += ((factor.fixed_amount if (factor.mixed or factor.factor_type=='travel') else 0.0) + (factor.factor * x if factor.factor_type != 'special' else x)) if ((x >= factor.range_start and x <= factor.range_end) or (factor.range_start == factor.range_end == 0.0)) else 0.0
					print "factor.fixed_amount : ", factor.fixed_amount
					print "factor.mixed : ", factor.mixed
					print "factor.factor_type : ", factor.factor_type
					print "factor.factor : ", factor.factor
					print "x : ", x

					operator_salary += result

			salary_monthly = 0.0
#			salary_percent = 0.0
			if operator_salary > 0.0:
				salary_monthly = operator_salary / rec.days

			rec.write({ 'operator_salary': operator_salary if operator_salary > 0.0 else 0.0,
						'salary_travel_days': operator_salary if operator_salary > 0.0 else 0.0,
						'salary_monthly': salary_monthly,
#						'salary_percent': salary_percent,
						})

			######## -----  MANIOBRAS ----- ########

			move_amount = rec.move_amount
			move_monthly = 0.0
#			move_percent = 0.0
			if move_amount > 0.0:
				move_monthly = move_amount / rec.days

			rec.write({ 'move_amount': move_amount if move_amount > 0.0 else 0.0,
						'move_travel_days': move_amount if move_amount > 0.0 else 0.0,
						'move_monthly': move_monthly,
#						'move_percent': move_percent,
						})
			######### ------- RESULTADOS FINALES DE GASTOS VARIABLES ------- #########

			amount_daily_variable = move_amount + operator_salary + total_highway_toll + factor_mtto_travel_days + factor_tires_travel_days + diesel_travel_days
			amount_travel_days_variable = amount_daily_variable / rec.days
#			amount_percentage_variable = (amount_daily_variable / rec.total_ingr)*100

			rec.write({ 'amount_daily_variable': amount_travel_days_variable if amount_travel_days_variable > 0.0 else 0.0,
						'amount_travel_days_variable':  amount_daily_variable if amount_daily_variable > 0.0 else 0.0,
#						'amount_percentage_variable': amount_percentage_variable,
						})



			############ ---------- GASTOS ADMINISTRATIVOS --------------- ###########
			amount_acumulated_administrative = 0.0
			amount_monthly_administrative = 0.0
			amount_daily_administrative = 0.0
			amount_travel_days_administrative = 0.0
#			amount_percentage_administrative = 0.0

			for administrative in rec.administrative_expenses_ids:
				amount_acumulated_administrative += administrative.acumulated_moth
				amount_monthly_administrative += administrative.average_moth
				amount_daily_administrative += administrative.daily_average
				travel_days = administrative.daily_average * rec.days
				administrative.write({'travel_days':travel_days})
				amount_travel_days_administrative += travel_days

			rec.write({
						'amount_acumulated_administrative': amount_acumulated_administrative ,
						'amount_monthly_administrative': amount_monthly_administrative,
						'amount_daily_administrative': amount_daily_administrative,
						'amount_travel_days_administrative': amount_travel_days_administrative,
#						'amount_percentage_administrative': amount_percentage_administrative,
				})


			############ --------- RESUMEN DE TODOS LOS CALCULOS ---------- ##############

			summary_income_monthly = total_income / rec.days
			summary_income_travel_days = total_income
			summary_income_percent = 100

			summary_expenditures_travel_days = total_acumulated_days + amount_daily_variable + amount_travel_days_administrative + rec.total_security
			summary_expenditures_monthly = summary_expenditures_travel_days / rec.days
			summary_expenditures_percent = ( summary_expenditures_travel_days / summary_income_travel_days ) * 100

			summary_utility_travel_days = summary_income_travel_days - summary_expenditures_travel_days
			summary_utility_monthly = summary_utility_travel_days / rec.days
			summary_utility_percent = ( summary_utility_travel_days / summary_income_travel_days ) * 100


			#### KMS Productivos
			km_pro = 0.0
			for pro in rec.route_ids:
				if pro.uncharged == False or pro.product_weight > 0.0:
					km_pro += pro.kms

			summary_km_productive_travel_days = summary_income_travel_days / km_pro
			summary_km_productive_monthly = summary_km_productive_travel_days / rec.days
			summary_km_productive_percent = ( summary_km_productive_travel_days / summary_income_travel_days ) *100

			summary_mk_shot_travel_days = summary_income_travel_days / total_kms
			summary_mk_shot_monthly = summary_mk_shot_travel_days / rec.days
			summary_mk_shot_percent = ( summary_mk_shot_travel_days / summary_income_travel_days ) * 100

			summary_cost_km_travel_days = summary_expenditures_travel_days / total_kms
			summary_cost_km_monthly = summary_cost_km_travel_days / rec.days
			summary_cost_km_percent = ( summary_cost_km_travel_days / summary_income_travel_days ) * 100

			summary_utility_km_travel_days = summary_utility_travel_days / total_kms
			summary_utility_km_monthly = summary_utility_km_travel_days / rec.days			
			summary_utility_km_percent = ( summary_utility_km_travel_days / summary_income_travel_days ) * 100


			######## Terminar el Margen Operativo
			
			summary_margin_travel_days = summary_income_travel_days - diesel_travel_days - operator_salary - total_highway_toll - move_amount - rec.total_security ### AGREGAMOS EL COSTO DE SEGURO VERIFICAR
			summary_margin_monthly = summary_margin_travel_days / rec.days
			summary_margin_percent = (summary_margin_travel_days / summary_income_travel_days ) * 100

			rec.write({
						'summary_income_monthly': summary_income_monthly,
						'summary_income_travel_days': summary_income_travel_days,
						'summary_income_percent': summary_income_percent,

						'summary_expenditures_travel_days': summary_expenditures_travel_days,
						'summary_expenditures_monthly': summary_expenditures_monthly,
						'summary_expenditures_percent': summary_expenditures_percent ,

						'summary_utility_monthly': summary_utility_monthly,
						'summary_utility_travel_days': summary_utility_travel_days,
						'summary_utility_percent': summary_utility_percent,

						'summary_km_productive_monthly': summary_km_productive_monthly,
						'summary_km_productive_travel_days': summary_km_productive_travel_days,
						'summary_km_productive_percent': summary_km_productive_percent,

						'summary_mk_shot_monthly': summary_mk_shot_monthly,
						'summary_mk_shot_travel_days': summary_mk_shot_travel_days,
						'summary_mk_shot_percent': summary_mk_shot_percent,

						'summary_cost_km_monthly': summary_cost_km_monthly,
						'summary_cost_km_travel_days': summary_cost_km_travel_days,
						'summary_cost_km_percent': summary_cost_km_percent,

						'summary_utility_km_monthly': summary_utility_km_monthly,
						'summary_utility_km_travel_days': summary_utility_km_travel_days,
						'summary_utility_km_percent': summary_utility_km_percent,

						'summary_margin_monthly': summary_margin_monthly,
						'summary_margin_travel_days': summary_margin_travel_days,
						'summary_margin_percent': summary_margin_percent,
				})

			######## ------------- CALCULAS LOS PORCENTAJES CORRESPONDIENTES DE GASTOS SE HACEN AL FINAL AL OBTENER EL MONTO TOTAL DE GASTOS SE PUEDE DIVIDIR CADA CANTIDAD INDIVIDUAL ENTRE ESTE MONTO * 100 ---- ######


		return True


	def onchange_operating_cost_products(self, cr, uid, ids, load_operating_cost):
		if load_operating_cost == False:
			return {}

		################### ------ COSTOS FIJOS OPERATIVOS ---------- ################
		### Creando los Costos Fijos Operativos
		product_obj = self.pool.get('product.product')
		product_fixes_ids = product_obj.search(cr, uid, [('tms_category', '=', 'indirect_expense'), ('active', '=', True), ('operating_fixed_cost', '=', True)])
		fixes_list = []

		date_start = ''
		date_end = ''
		number_months = 0
		fiscalyear_id = 0
		fiscalyear_obj = self.pool.get('account.fiscalyear')
			
		if product_fixes_ids:
			read = product_obj.read(cr, uid, product_fixes_ids[0])
			read_name = product_obj.read(cr, uid, product_fixes_ids[0])['name']

			date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
			year = date_strp.year
			month = date_strp.month
			day = date_strp.day

			#date_revision = date_strp - timedelta(days=30)

			if day == 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0101'+str(year-1)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day < 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0111'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0112'+str(year_asign)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 11

			elif day < 15 and month == 02:
				year_asign = year - 1
				cadena_date = '0112'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day ==15 and month == 02:
				cadena_date = '0101'+str(year)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0102'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 1


			else:
				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				if day < 15:
					ms = month - 2
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month -1 
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 2 

				elif day == 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1

				elif day > 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '15'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1


			for product in product_obj.browse(cr, uid, product_fixes_ids):
				account_list = []
				for ac in product.tms_account_ids:
					account_list.append(ac.id)


				# account_period_obj = self.pool.get('account.period')
				# account_period_ids = account_period_obj.search(cr, uid, [('fiscalyear_id','=',fiscalyear_id),('date_stop','<',date_end)])
				# number_periods = len(account_period_ids)
				############ HACER EL QUERY PARA EL RESULTADO DE TODOS LOS ACCOUNT MOVE LINE QUE RESULTEN COMPARAR Y DE AHI TOMAR LA INFORMACION PARA LO QUE SE NECESITE
				############ NO HACER POR PYTHON SI NO POR SQL DEBIT - CREDIT

				############# EMPEZAMOS EL QUERY PARA TRAER TODOS LOS MOVIEMIENTOS DE ACCOUNT_MOVE_LINE DE LAS CUENTAS DE LOS PRODUCTOS #############

				cumulative_sum = 0.0

				for account in account_list:
					cr.execute("""
						select sum(coalesce(debit) - coalesce(credit)) from account_move_line
						where
						period_id in (select id from account_period where fiscalyear_id = %s and date_stop < %s)
						and account_id = %s""", (fiscalyear_id, date_end, account))
					suma = cr.fetchall()
					suma01 = suma[0][0]
					if suma01:
						cumulative_sum += suma01
					# else:
					# 	suma01 = 0.0
					# 	cumulative_sum += cumulative_sum
				average_moth = cumulative_sum / number_months
				daily_average = average_moth / 30

				### Aqui buscamos dentro de las cuentas que tenga cada producto el debit - credit para al final crear un diccionario para crear las lineas
				# Debemos buscar los montos de acuerdo a la fecha actual de la fecha inicio del periodo contable
				xline = (0 ,0,{
								'product_id': product.id,
								'name': product.name,
								'acumulated_moth': cumulative_sum, # Calculados en base a los resultados de la busqueda
								'average_moth': average_moth if cumulative_sum else 0.00, # Calculados en base a los resultados de la busqueda
								'daily_average': daily_average if average_moth else 0.00, # Calculados en base a los resultados de la busqueda
								'travel_days': 0.0, # Calculados en base a los resultados de la busqueda
								#'percent': 0.0, # Calculados en base a los resultados de la busqueda
						})
				fixes_list.append(xline)
			return {'value' : {'operating_cost_ids' : [x for x in fixes_list]}}
		else:
			warning = {}
			title =  _("Error de Configuracion!")
			message = "No se Encontraron productos definidos como Gastos Fijos de Operacion"
			warning = {
					'title': title,
					'message': message,
			}
			
			warning['message'] = message 
			return {'warning':warning}


	def onchange_administrative_expenses(self, cr, uid, ids, load_administrative_expenses):

		if load_administrative_expenses == False:
			return {}

		################### ------ GASTOS ADMINISTRATIVOS ---------- ################
		### CREANDO LOS GASTOS ADMINISTRATIVOS
		product_obj = self.pool.get('product.product')
		product_administrative_ids = product_obj.search(cr, uid, [('tms_category', '=', 'indirect_expense'), ('active', '=', True), ('administrative_expense', '=', True)])
		administrative_list = []
		date_start = ''
		date_end = ''
		number_months = 0
		fiscalyear_id = 0
		fiscalyear_obj = self.pool.get('account.fiscalyear')

		if product_administrative_ids:
			read = product_obj.read(cr, uid, product_administrative_ids[0])
			read_name = product_obj.read(cr, uid, product_administrative_ids[0])['name']
			date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
			year = date_strp.year
			month = date_strp.month
			day = date_strp.day

			#date_revision = date_strp - timedelta(days=30)

			if day == 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0101'+str(year-1)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day < 15 and month == 01:
				year_asign = year - 1
				cadena_date = '0111'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0112'+str(year_asign)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 11

			elif day < 15 and month == 02:
				year_asign = year - 1
				cadena_date = '0112'+str(year_asign)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") 
				cadena_date_02 = '0101'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year-1)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 12

			elif day ==15 and month == 02:
				cadena_date = '0101'+str(year)
				date_start = datetime.strptime(cadena_date, "%d%m%Y") # Al realizar o crear mi propia fecha ya es del tipo strp para realizar calculos con fechas timedelta
				cadena_date_02 = '0102'+str(year)
				date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				number_months = 1


			else:
				cadena_closed = '3112'+str(year)
				date_closed = datetime.strptime(cadena_closed, "%d%m%Y")
				fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('date_stop','=',date_closed)])
				for fy in fiscalyear_obj.browse(cr, uid, fiscalyear_ids):
					if fy.period_ids:
						fiscalyear_id = fy.id
				if day < 15:
					ms = month - 2
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month -1 
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")

					number_months = month - 2 

				elif day == 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '01'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1

				elif day > 15:
					ms = month - 1
					if ms < 10:
						month_asign ='0' + str(ms)
					else:
						month_asign = str(ms)
					cadena_date = '01'+month_asign+str(year)
					date_start = datetime.strptime(cadena_date, "%d%m%Y")
					ms_02 = month
					if ms_02 < 10:
						month_asign_02 ='0' + str(ms_02)
					else:
						month_asign_02 = str(ms_02)
					cadena_date_02 = '15'+month_asign_02+str(year)
					date_end = datetime.strptime(cadena_date_02, "%d%m%Y")
					number_months = month - 1


			for product in product_obj.browse(cr, uid, product_administrative_ids):
				account_ids = product.tms_account_ids
				account_list = []
				for ac in product.tms_account_ids:
					account_list.append(ac.id)
				############# EMPEZAMOS EL QUERY PARA TRAER TODOS LOS MOVIEMIENTOS DE ACCOUNT_MOVE_LINE DE LAS CUENTAS DE LOS PRODUCTOS #############

				cumulative_sum = 0.0

				for account in account_list:
					cr.execute("""
						select sum(coalesce(debit) - coalesce(credit)) from account_move_line
						where
						period_id in (select id from account_period where fiscalyear_id = %s and date_stop < %s)
						and account_id = %s""", (fiscalyear_id, date_end, account))
					suma = cr.fetchall()
					suma01 = suma[0][0]
					if suma01:
						cumulative_sum += suma01
					# else:
					# 	suma01 = 0.0
					# 	cumulative_sum += cumulative_sum
				average_moth = cumulative_sum / number_months
				daily_average = average_moth / 30

				### Aqui buscamos dentro de las cuentas que tenga cada producto el debit - credit para al final crear un diccionario para crear las lineas
				# Debemos buscar los montos de acuerdo a la fecha actual de la fecha inicio del periodo contable
				xline = (0 ,0,{
								'product_id': product.id,
								'name': product.name,
								'acumulated_moth': cumulative_sum,  # Calculados en base a los resultados de la busqueda
								'average_moth':  average_moth if cumulative_sum else 0.00, # Calculados en base a los resultados de la busqueda
								'daily_average': daily_average if average_moth else 0.00, # Calculados en base a los resultados de la busqueda
								'travel_days': 0.0, # Calculados en base a los resultados de la busqueda
								#'percent': 0.0, # Calculados en base a los resultados de la busqueda
						})
				administrative_list.append(xline)
			return {'value' : {'administrative_expenses_ids' : [x for x in administrative_list]}}
		else:
			warning = {}
			title =  _("Error de Configuracion!")
			message = "No se Encontraron productos definidos como Gastos Administrativos"
			warning = {
					'title': title,
					'message': message,
			}
			
			warning['message'] = message 
			return {'warning':warning}


	def onchange_quotation(self, cr, uid, ids, parameter_id, days):
#		if not parameter_id:
#			return {'value': {
#							  #'pricelist_id': False,
#							  #'currency_id': False,}
#					}
		parameter_obj = self.pool.get('tms.quotation.config')
		parameter_browse = parameter_obj.browse(cr, uid, [parameter_id], context=None)[0]
		print "####################################### MONTH DAYS", parameter_browse
		print "####################################### MONTH DAYS", parameter_browse.month_days
		val = {
				'month_travel': parameter_browse.month_days / days,
				'diesel_cost' : parameter_browse.diesel_cost,
				'performance_loaded' : parameter_browse.charged_performance,
				'uncharged_performance' : parameter_browse.uncharged_performance,
				'factor_mtto' : parameter_browse.factor_mtto,
				'factor_tires' :parameter_browse.factor_tires, 
		#'pricelist_id': pricelist,
		#'currency_id': currency,
		}
		return {'value': val}

#	_order = "id desc"


	def copy(self, cr, uid, id, default=None, context=None):
		quotation = self.browse(cr, uid, id, context=context)
		if not default:
			default = {}
		default.update({
						
						#'unit_ids'	  : False, 
						'state'		 : 'draft',
						'agreement_id'	: False, 
						
						})
		return super(tms_quotation, self).copy(cr, uid, id, default, context=context)

	def action_confirmed(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids,{'state':'confirmed'})
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Quotation %s <em>%s</em> <b>confirmed</b>.") % (obj.sequence,obj.name),  context=context)
		return True


	def action_draft(self, cr,uid,ids,context={}):
		self.write(cr, uid, ids, {'state':'draft'})
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Quotation %s <em>%s</em> <b>drafted </b>.") % (obj.sequence,obj.name) ,context=context)
		return True


	def action_done(self,cr,uid,ids,context={}): 
		for rec in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [rec.id], body=_("Quotation %s <em>%s</em> <b>done</b>.") % (rec.sequence,rec.name),  context=context)
		self.write(cr, uid, ids, {'state':'done'})		
		return True	


	def action_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state':'cancel'})
		tms_agreement_obj = self.pool.get('tms.agreement')
		for obj in self.browse(cr, uid, ids, context=context):
			self.message_post(cr, uid, [obj.id], body=_("Quotation %s <em>%s</em> <b>cancelled</b>.") % (obj.sequence,obj.name),  context=context)
		for quotation in self.browse(cr, uid, ids, context=context):
			if quotation.agreement_id:
				self.message_post(cr, uid, [quotation.id], body=_("Agreement <em>%s</em> <b>has been Eliminated</b>.") % (quotation.agreement_id.name),  context=context)
				#tms_agreement_obj.unlink(cr, uid, [quotation.agreement_id.id], context=None)
				tms_agreement_obj.write(cr, uid, [quotation.agreement_id.id], {'state':'cancel'})
				quotation.write({'agreement_id':False})
		return True

	def _check_mark(self, cr, uid, ids, context=None):
		for rec in self.browse(cr,uid,ids):
			i=0
			for route in rec.route_ids:
				if route.mark == True:
					i += 1
			if i <= 1:
				return True
		return False

	# def _check_factor(self, cr, uid, ids, context=None):
	# 	for rec in self.browse(cr,uid,ids):
	# 		i=0
	# 		for factor in rec.factor_ids:
	# 			if factor:
	# 				i += 1
	# 		if i <= 1:
	# 			return True
	# 	return False

	# _constraints = [
	# 	(_check_mark, 'Error ! No se pueden tener 2 Rutas Marcadas ', ['Rutas']), (_check_factor, 'Error ! No se puede calcular mas de 1 factor por Cotizacion ', ['Factores'])
	# ]
	_constraints = [
		(_check_mark, 'Error ! No se pueden tener 2 Rutas Marcadas ', ['Rutas'])]
tms_quotation()


class tms_quotation_route(osv.Model):
	_name = 'tms.quotation.route'
	_description = 'Quotations Routes for TMS QUOTATION'

	def _get_total(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		total = 0.0
		for factor in self.browse(cr, uid, ids, context=context):
			if factor.factor_type != 'special':
				res[factor.id] = factor.factor * factor.variable_amount + (factor.fixed_amount if factor.mixed else 0.0)
			else: 
				res[factor.id] = 0.0 # Pendiente generar cálculo especial
		return res

	_columns = {
		'name': fields.char('Description of the Route', size=128, required=False),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID', ondelete='cascade'),			  
		'route_id': fields.many2one('tms.route', 'Route', required=True),
		'kms': fields.float('Kms', digits=(4,2), required=True),
		'product_id': fields.many2one('product.product', 'Product', domain=['|','|','|','|',
									('tms_category', '=','transportable'), 
									('tms_category', '=','move'), 
									('tms_category', '=','insurance'), 
									('tms_category', '=','highway_tolls'), 
									('tms_category', '=','other'),
									], change_default=True),
		'product_weight': fields.float('Weight', digits=(16, 2)),
		'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
		'rate': fields.float('Rate', digits=(16, 2)),
		'insurance': fields.float('Insurance', digits=(16, 2), required=True),
		'income': fields.float('Income', digits=(16, 2), required=True),
		'uncharged': fields.boolean('Uncharged'),
		'mark': fields.boolean('Mark'),
		'notes': fields.text('Notes'),

		########### --- CAMPOS NECESARIOS PARA EL FACTOR --- #############
		# 'category'	  : fields.selection([

		# 								('driver', 'Driver'),
		# 								('customer', 'Customer'),
		# 								('supplier', 'Supplier'),
		# 								], 'Type', required=True),
		'factor_type'   : fields.selection([
										('default','Default'),
										('distance', 'Distance Route (Km/Mi)'),
										('weight', 'Weight'),
										('travel', 'Travel'),
										('qty', 'Quantity'),
										], 'Factor Type', required=False, help="""
For next options you have to type Ranges or Fixed Amount
 - Distance Route (Km/mi)
 - Weight
 - Quantity
 - Volume
For next option you only have to type Fixed Amount:
 - Travel
For next option you only have to type Factor like 10.5 for 10.50%:

						"""),
		
		'framework'	 : fields.selection([
								('Any', 'Any'),
								('Unit', 'Unit'),
								('Single', 'Single'),
								('Double', 'Double'),
								], 'Framework', required=True),
		# 'factor'		: fields.float('Factor',		digits=(16, 4)),
		#### EL FACTOR ES EL RATE ####
		'fixed_amount'  : fields.float('Fixed Amount', digits=(16, 4)),
		'mixed'		 : fields.boolean('Mixed'),
		'total_amount'  : fields.function(_get_total, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total', type='float', store=True),
		'variable_amount' : fields.float('Variable',  digits=(16, 4)),
		'sequence'	  : fields.integer('Sequence', help="Gives the sequence calculation for these factors."),											
	}

	_defaults = {
		'mixed'			 : False,
		'sequence'	 	 : 10,
		'framework'		 : 'Any',
		'factor_type'    : 'default',
		
	}

	def calculate(self, cr, uid, ids, factor_type, total_kms, total_weight, factor, mixed, fixed_amount, context=None):
		result = 0.0
		x = 0.0
		if factor_type == 'distance': 
			print "Tipo Distancia"

			x = (float(total_kms))

		elif factor_type == 'weight':
			print "####### TIPO PESO"

			x = float(total_weight)

		elif factor_type == 'qty':
			print "####### TIPO CANTIDAD"
			x = float(total_weight)

		elif factor_type == 'travel':
			print "####### TIPO VIAJE"
			x = 0.0
		
		result += ((fixed_amount if (mixed or factor_type=='travel') else 0.0)+ (factor * x ))
		print "fixed_amount : ", fixed_amount
		print "mixed : ", mixed
		print "factor_type : ", factor_type
		print "factor : ", factor
		print "x : ", x
		print "################################################# RESULTADO =================", result
		print "################################################# RESULTADO =================", result
		return result
		

	def onchange_route(self, cr, uid, ids, route_id, context=None):
		if not route_id:
			return {'value': {} }
		route_obj = self.pool.get('tms.route')
		kms = 0.0
		for r in route_obj.browse(cr, uid, [route_id]):
			kms = r.distance
		val = {
			'kms': kms,
		}
		return {'value': val}

	def onchange_quotation(self, cr, uid, ids, factor_type, kms, product_weight, rate, insurance, mixed, fixed_amount, context=None):
		print "##################################### KMS", kms
		print "##################################### PRODUCT WEIGHT", product_weight
		print "##################################### RATE", rate
		print "##################################### INSURANCE", insurance
		print "##################################### FACTOR TYPE", factor_type
		print "##################################### MIXED", mixed
		print "##################################### FIXED AMOUNT", fixed_amount
		total = 0.0
		if factor_type == 'default':
			total = (product_weight * rate)+insurance
		if not factor_type:
			total = 0.0 + insurance
		else:
			calculate = self.calculate(cr, uid, ids, factor_type, kms, product_weight, rate, mixed, fixed_amount)
			print "############################################################ CALCULATE", calculate
			print "############################################################ CALCULATE", calculate
			print "############################################################ CALCULATE", calculate
			total = calculate + insurance
		print "################################################################ AL FINAL EL TOTAL ES", total
		val = {
			'income': total,
		}
		return {'value': val}

	def onchange_unchanged(self, cr, uid, ids, uncharged, context=None):
		if uncharged == True:
			val = {
				"product_id": False,
				"product_weight" : 0.0,
				"product_uom": 0.0,
				"rate" : 0.0,
				"factor_type": False,
				"mixed": False,
				"fixed_amount": 0.0,
				#"income": 0.0
			}
		return {'value': val}

	_order = "name"

	def onchange_product_id(self, cr, uid, ids, product_id, context=None):
		product_obj = self.pool.get('product.product')
		if product_id:
			for product in product_obj.browse(cr, uid, [product_id], context=context):

				val = {
						'product_uom': product.uom_id.id,
					}
		else:
			val = {}
		return {'value':val}

tms_quotation_route()

class tms_quotation_config(osv.Model):
	_name = 'tms.quotation.config'
	_description = 'Parameters for TMS QUOTATION'

	_columns = {
		'name': fields.char('Description', size=128, required=False),
		'month_days': fields.float('Days of the Month', digits=(9,2), required=True),
		'diesel_cost': fields.float('Cost of Diesel', digits=(9,2), required=True),
		'units_number': fields.float('Units Number', digits=(9,0), required=True),
		'number_trailers': fields.float('Number of Trailers', digits=(4,0), required=True),
		'operators': fields.float('Operators', digits=(4,0), required=True),
		'movers': fields.float('Movers', digits=(4,0), required=True),
		'tires': fields.float('Number of Tires', digits=(4,0), required=True),
		'charged_performance': fields.float('Charged Performance', digits=(9,2), required=True),
		'uncharged_performance': fields.float('Uncharged Performance', digits=(9,2), required=True),
		'salary_diary_movers': fields.float('Salary Movers Journal', digits=(9,2), required=True),
		'integrated_wage_factor': fields.float('Integrated Wage Factor', digits=(9,2), required=True),
		'insurance_satellite_equipment': fields.float('Insurance Satellite Equipment', digits=(9,2), required=True),
		'tractor_insurance': fields.float('Tractor Insurance', digits=(9,2), required=True),
		'trailer_insurance': fields.float('Trailer Insurance', digits=(9,2), required=True),
		'dolly_insurance': fields.float('Dolly Insurance', digits=(9,2), required=True),
		'ambiental_insurance': fields.float('Ambiental Insurance', digits=(9,2), required=True),
		'factor_administrative_expenses': fields.float('Factor Administrative Expenses', digits=(9,2), required=True),
		'factor_mtto': fields.float('Maintenance Factor', digits=(9,2), required=True),
		'factor_tires': fields.float('Tires Factor', digits=(9,2), required=True),

	}
	_defaults = {
	'month_days': 30,
	'name': 'Parameters',
	}

	def _check_unique(self, cr, uid, ids, context=None):
		if not ids:
			return True
		tms_quotation_config_obj = self.pool.get('tms.quotation.config')
		tms_quotation_config_ids = tms_quotation_config_obj.search(cr, uid, [('id','!=',ids[0])])
		if tms_quotation_config_ids:
			return False		   
		return True


	_constraints = [
		(_check_unique, 'Error ! Should only be kept of parameters', ['id'])
	]
tms_quotation_config()


class tms_operating_cost(osv.Model):
	_name = 'tms.operating.cost'
	_description = 'Fixed Operating Costs'

	_columns = {
		'product_id': fields.many2one('product.product','Product'),
		'name': fields.char('Concept', size=128, required=False),
		'acumulated_moth': fields.float('Accumulated C. Month', digits=(12,4), help="Accumulated Current Month"),
		'average_moth': fields.float('Average Month', digits=(12,4)),
		'daily_average': fields.float('Daily Average', digits=(12,4)),
		'travel_days': fields.float('Travel Days', digits=(12,4)),
		'percent': fields.float('%', digits=(2, 2), required=False),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID', ondelete='cascade'),			  

	}
	_defaults = {

	}
	_order = "acumulated_moth desc"

tms_operating_cost()


class tms_administrative_cost(osv.Model):
	_name = 'tms.administrative.cost'
	_description = 'Fixed Operating Costs'

	_columns = {
		'product_id': fields.many2one('product.product','Product'),
		'name': fields.char('Concept', size=128, required=False),
		'product_id': fields.char('Concep', size=128, required=False),
		'acumulated_moth': fields.float('Accumulated current month', digits=(12,4)),
		'average_moth': fields.float('Average Month', digits=(12,4)),
		'daily_average': fields.float('Daily Average', digits=(12,4)),
		'travel_days': fields.float('Travel Days', digits=(12,4)),
		'percent': fields.float('%', digits=(2, 2), required=False),
		'quotation_id': fields.many2one('tms.quotation', 'Quotation ID', ondelete='cascade'),			  

	}
	_defaults = {

	}
	_order = "acumulated_moth desc"
tms_administrative_cost()


#################### WIZARD PARA GENERAR EL AGREEMENT

class tms_quotation_agreement_wizard(osv.osv_memory):
	_name = 'tms.quotation.agreement.wizard'
	_description = 'Make Travel from Agreement'

	def _get_selection(self, cr, uid, context=None):
		active_id = context and context.get('active_id', False)
		print "######################### ACTIVE IDDDDDDDDDDD", active_id
		tms_quotation_obj = self.pool.get('tms.quotation')
		route_list = []
		for quotation in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
			if not quotation.route_ids:
				return ()
			for route in quotation.route_ids:
				route_list.append((route.route_id.id,route.route_id.name))
		return (tuple(route_list))

	def _get_selection_2(self, cr, uid, context=None):
		active_id = context and context.get('active_id', False)
		print "######################### ACTIVE IDDDDDDDDDDD", active_id
		tms_quotation_obj = self.pool.get('tms.quotation')
		route_list = []
		for quotation in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
			if not quotation.route_ids:
				return ()
			for route in quotation.route_ids:
				route_list.append((route.route_id.id,route.route_id.name))
		return (tuple(route_list))

	_columns = {

		'shop_id': fields.many2one('sale.shop', 'Shop', required=True, readonly=False),
		'date': fields.date('Date Start', required=True),
		'partner_id': fields.many2one('res.partner', 'Customer', required=False, select=True, readonly=False),
		'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', required=True),
		'partner_order_id': fields.many2one('res.partner', 'Ordering Contact', required=True),
		'departure_address_id': fields.many2one('res.partner', 'Departure Address', required=True),
		'arrival_address_id': fields.many2one('res.partner', 'Arrival Address', required=True),
		'upload_point': fields.char('Upload Point', size=128, readonly=False, required=True),
		'download_point': fields.char('Download Point', size=128, required=True, ),
		'date_start': openerp.osv.fields.date('Date Star', required=True),
		'date_end': openerp.osv.fields.date('Date End', required=True),
		'currency_id': fields.many2one('res.currency','Currency'),
		'quotation_id': fields.many2one('tms.quotation', 'Active ID'),
		'route_seleccion': fields.selection(_get_selection, 'Selecciona la Ruta de Partida'),
		'route_seleccion_return': fields.selection(_get_selection_2, 'Selecciona la Ruta de Partida'),

	}

	def _get_active_shop(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		res_obj = self.pool.get('res.users')
		res = res_obj.browse(cr, uid, uid, context=context)
		print "################################################# RES USERS", res.company_id.name
		shop_obj = self.pool.get('sale.shop')
		shop = shop_obj.search(cr, uid, [('company_id','=',res.company_id.id)], limit=1)
		# shop_id = shop[0]
		# print "#######################################################  SHOP [0]", shop_id
		if not shop:
			return None
		# return shop_id
		return shop[0]

	def _get_active_customer(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		active_id = context and context.get('active_id', False)
		print "######################### ACTIVE IDDDDDDDDDDD", active_id
		tms_quotation_obj = self.pool.get('tms.quotation')
		partner_id = []
		for customer in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
			if customer.partner_id:
				partner_id.append(customer.partner_id.id)

		return partner_id[0]

	def _get_active_id(self,cr,uid,context=None): # esta funcion en el wizard le va agregar por defecto la session en la que estamos
		active_id = context and context.get('active_id', False)
		if not active_id:
			return []

		return active_id

	_defaults = {
		'shop_id': _get_active_shop,
		'partner_id': _get_active_customer,
		'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'date_start': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
		'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,
		'quotation_id': _get_active_id,

	}

	def onchange_partner_id(self, cr, uid, ids, partner_id):
		if not partner_id:
			return {'value': {'partner_invoice_id': False, 
							'partner_order_id': False, 
							'payment_term': False, 
							#'pricelist_id': False,
							#'currency_id': False, 
							'user_id': False}
					}
		addr = self.pool.get('res.partner').address_get(cr, uid, [partner_id], ['invoice', 'contact', 'default', 'delivery'])
		part = self.pool.get('res.partner').browse(cr, uid, partner_id)
		pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
		payment_term = part.property_payment_term and part.property_payment_term.id or False
		dedicated_salesman = part.user_id and part.user_id.id or uid
		val = {
				'partner_invoice_id': addr['invoice'] if addr['invoice'] else addr['default'],
				'partner_order_id': addr['contact'] if addr['contact'] else addr['default'],
				'payment_term': payment_term,
				'user_id': dedicated_salesman,
				#'pricelist_id': pricelist,
				#'currency_id': currency,
		}
		return {'value': val}

	def button_generate_agreement(self, cr, uid, ids, context=None):
		active_id = context and context.get('active_id', False)
		tms_quotation_obj = self.pool.get('tms.quotation')
		tms_agreement_obj = self.pool.get('tms.agreement')
		product_obj = self.pool.get('product.product')
		fpos_obj = self.pool.get('account.fiscal.position')
		product_id = product_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_freight','=',True),('active','=', 1)], limit=1)

		product_browse = product_obj.browse(cr, uid, product_id, context=context)[0]
		for wizard in self.browse(cr, uid, ids, context=context):
			route_mark_id = []
			route_uncharged_id = []
			product_shipped_list = []
			agreement_line_list = []
			factor_list = []
			tms_agreement_id = 0
			expenses_list = []
			factor_driver_list = []

			if wizard.route_seleccion == wizard.route_seleccion_return:
				raise osv.except_osv(
					_('Error!'),
					_('La Ruta de Partida y Retorno no puede ser la misma seleccione una Distinta ...'))
			for quotation in tms_quotation_obj.browse(cr, uid, [active_id], context=context):
				
				for route in quotation.route_ids:
					if route.mark:
						if route.route_id.expense_driver_factor:
							product_obj = self.pool.get('product.product')
							product_id = product_obj.search(cr, uid, [('tms_category', '=', 'freight'),('tms_default_freight','=',True),('active','=', 1)], limit=1)
							if not product_id:
								raise osv.except_osv(
									_('Error, No se puede generar el Acuerdo!'),
									_('No se tiene Configurado un producto con las caracteristicas (tms_category, =, freight),(tms_default_freight,=,True),(active,=, 1)'))
							product_browse = product_obj.browse(cr, uid, product_id, context=context)[0]
							for factor in route.route_id.expense_driver_factor:
								print "########################################## FACTOR TYPE", factor.factor_type
								print "########################################## FACTOR TYPE", factor.range_start
								xline_factor = (0,0,{
										    		'name'          : product_browse.name,
											        'category'      : factor.category,
											        'factor_type'   : factor.factor_type,
											        'framework'     : factor.framework if factor.framework else False,
											        'range_start'   : factor.range_start if factor.range_start else 0.0,
											        'range_end'     : factor.range_end if factor.range_end else 0.0,
											        'factor'        : factor.factor if factor.factor else False,
											        'fixed_amount'  : factor.fixed_amount if factor.fixed_amount else 0.0,
											        'mixed'         : factor.mixed if factor.mixed else False,
											        'factor_special_id': factor.factor_special_id.id if factor.factor_special_id.id else False,
											        'variable_amount' : factor.variable_amount if factor.variable_amount else False,
											        'total_amount'  : factor.total_amount if factor.total_amount else 0.0,
											        'sequence'      : 0,
											        'notes'         : "Factor cargado de la ruta "+route.route_id.name,
											        'control'       : factor.control if factor.control == True else False,### Revisar si es necesario eliminarlo
											        'driver_helper' : factor.driver_helper if factor.driver_helper else False,

										})
								print "######################################## XLINE FACTOR", xline_factor
								print "######################################## XLINE FACTOR", xline_factor
								print "######################################## XLINE FACTOR", xline_factor
								factor_driver_list.append(xline_factor)

				control = False
				if quotation.agreement_id:
					raise osv.except_osv(
								_('Error, No se puede generar el Acuerdo!'),
								_('La Cotizacion Tiene el Acuerdo %s asignado, duplica el registro o crea uno Nuevamente ...') % (quotation.agreement_id.name))
				elif quotation.state != 'confirmed':
					raise osv.except_osv(
								_('Error, No se puede generar el Acuerdo!'),
								_('La Cotizacion %s se encuentra en el Estado Borrador, Confirmelo antes de crear el Acuerdo ...') % (quotation.sequence))
				else:
					i = 0
					for route in quotation.route_ids:
						if route.mark == True:
							route_mark_id.append(route.route_id.id)
						if route.uncharged:
							route_uncharged_id.append(route.route_id.id)
						if route.product_id:
							xline = (0 ,0,{
											'name': route.product_id.name,
											'product_id': route.product_id.id,
											'product_uom': route.product_uom.id,
											'product_uom_qty': route.product_weight,
											'notes': False,
											'sequence': i,
											})
							product_shipped_list.append(xline)
							i+=1
					######### CREANDO LOS FACTORES DESDE LAS RUTAS DE LA COTIZACION
					for factor in quotation.route_ids:
						xline_factor = (0,0,{
								    		'name'          : product_browse.name,
									        'category'      : 'customer',
									        'factor_type'   : factor.factor_type,
									        'framework'     : factor.framework if factor.framework else False,
									        'range_start'   : factor.range_start if factor.range_start else 0.0,
									        'range_end'     : factor.range_end if factor.range_end else 0.0,
									        'factor'        : factor.factor if factor.factor else False,
									        'fixed_amount'  : factor.fixed_amount if factor.fixed_amount else 0.0,
									        'mixed'         : factor.mixed if factor.mixed else False,
									        'factor_special_id': factor.factor_special_id.id if factor.factor_special_id.id else False,
									        'variable_amount' : factor.variable_amount if factor.variable_amount else False,
									        'total_amount'  : factor.total_amount if factor.total_amount else 0.0,
									        'sequence'      : 0,
									        'notes'         : quotation.name+" "+quotation.partner_id.name,
									        'control'       : control,
									        'driver_helper' : False,
 
								})
						factor_list.append(xline_factor)

					xline_agreement = (0,0,{
								'line_type': 'product',
								'name': product_browse.name,
								'sequence': 0,
								'product_id': product_browse.id,
								'price_unit': quotation.total_ingr,
								'tax_id': [(6, 0, [x.id for x in product_browse.taxes_id])],
								'product_uom_qty': 1,
								'product_uom': product_browse.uom_id.id,
								'control': control,
								})
					agreement_line_list.append(xline_agreement)
					print "#################### AGREEMENTS LINEASSSSSSSSSSSSS", agreement_line_list
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					print "############################## RUTAAAAAAAAAAAAAAAAAAAASSSSSSSSSSSSSS", route_mark_id
					########--- CREANDO LOS GASTOS DESDE LA COTIZACION ---########
					sq = 0
					if quotation.total_security > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'insurance'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado como Seguro'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.total_security,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Insurance expense Units',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.factor_mtto_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'maintenance'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Mantenimiento'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.factor_mtto_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expenditures for maintenance of the units',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.factor_tires_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'tires'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Llantas o Tires'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.factor_tires_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expense using by Tires',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.diesel_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'fuel'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Combustible'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'fuel',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.diesel_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expenses for fuel consumption during the Trip',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.toll_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'highway_tolls'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Caseta'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.toll_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Expenses during the trip by highway tolls',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.salary_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'salary'),('tms_default_salary','=',True),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Salario y Default por Defecto'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'salary',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.salary_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Salary expenses Operator',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.move_travel_days > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'move'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Move o Maniobra'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'real_expense',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.move_travel_days,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Moves Expenses',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.operating_amount_all > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'fixed_operating'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Gastos Fijos Operativos'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'indirect',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.operating_amount_all,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Fixed Operating Costs',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					if quotation.administrative_amount_all > 0.0:
						product_income_id = product_obj.search(cr, uid, [('tms_category', '=', 'administrative_expense'),('active','=', 1)], limit=1)
						product_browse = product_obj.browse(cr, uid, product_income_id, context)
						fpos = quotation.partner_id.property_account_position.id or False
						if not product_income_id:
							raise osv.except_osv(
                                _('Error al Crear el Acuerdo !'),
                                _('No se tiene un producto configurado de tipo Gastos Administrativos'))
						else:
							sq += 1
							xline_expense = (0,0,{
									'automatic_advance': False,
									'line_type': 'indirect',
									'name': product_browse[0].name,
									'sequence': sq,
									'price_unit': quotation.administrative_amount_all,
									'product_uom_qty': 1,
									'discount': 0.00,
									'notes': 'Administrative Expenses',
									'control': False,
									'product_id' : product_income_id[0],
									'product_uom': product_browse[0].uom_id.id,
									'tax_id' : [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_browse[0].taxes_id)])],
									})
							expenses_list.append(xline_expense)

					# if factor_mtto_travel_days:
					# 	xline_expense = (0,0,{
					# 			'line_type': 'product',
					# 			'name': product_browse.name,
					# 			'sequence': 0,
					# 			'product_id': product_browse.id,
					# 			'price_unit': quotation.total_ingr,
					# 			'tax_id': [(6, 0, [x.id for x in product_browse.taxes_id])],
					# 			'product_uom_qty': 1,
					# 			'product_uom': product_browse.uom_id.id,
					# 			'control': control,
					# 			})
						# expenses_list.append(xline_expense)

					vals = {
							'shop_id': wizard.shop_id.id,
							'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
							'partner_id': wizard.partner_id.id,
							'partner_invoice_id': wizard.partner_invoice_id.id,
							'partner_order_id': wizard.partner_order_id.id,
							'departure_address_id': wizard.departure_address_id.id,
							'arrival_address_id': wizard.arrival_address_id.id,
							'upload_point': wizard.upload_point,
							'download_point': wizard.download_point,
							'date_start': wizard.date_start,
							'date_end': wizard.date_end,
							'quotation_id': active_id,
							'unit_ids': quotation.unit_ids.id,
							'unit_a': quotation.parameter_id.units_number,
							'route_id': route_mark_id[0] if route_mark_id else False,
							'route_return_id': route_uncharged_id[0] if route_uncharged_id else False,
							'agreement_shipped_product': [x for x in product_shipped_list],
							'agreement_line': [x for x in agreement_line_list] if product_id else [],
							'units_a': quotation.parameter_id.units_number,
							'agreement_customer_factor': [x for x in factor_list] if factor_list else [],
							'agreement_driver_factor': [x for x in factor_driver_list] if factor_driver_list else [],
							'agreement_direct_expense_line': [x for x in expenses_list] if expenses_list else False,
							'state': 'confirmed',
							'departure': True if int(wizard.route_seleccion) == route_mark_id[0] else False,
							'departure_2': True if int(wizard.route_seleccion) == route_uncharged_id[0] else False,
							'arrival': True if int(wizard.route_seleccion_return) == route_mark_id[0] else False,
							'arrival_2': True if int(wizard.route_seleccion_return) == route_uncharged_id[0] else False,

							}
	
					print "################################################### VALORES PARA CREAR EL ACUERDOOOOOOOOOOOO", vals
					tms_agreement_id = tms_agreement_obj.create(cr, uid, vals, context)
					if tms_agreement_id:
						quotation.write({'agreement_id': tms_agreement_id})
					for agr in tms_agreement_obj.browse(cr, uid, [tms_agreement_id], context=context):
						agr.action_mount_write()

		return {
			'type': 'ir.actions.act_window',
			'name': _('TMS AGREEMENTS'),
			'res_model': 'tms.agreement',
			'res_id': tms_agreement_id,
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': False,
			'target': 'current',
			'nodestroy': True,
		}
tms_quotation_agreement_wizard()

# Products 
class product_product(osv.osv):
	_name = 'product.product'
	_inherit ='product.product'

	_columns = {
		}


	def onchange_tms_category(self, cr, uid, ids, tms_category):
		print "################################### CATEGORIA DEL PRODUCTO", tms_category
		print "################################### CATEGORIA DEL PRODUCTO", tms_category
		val = {}
		if not tms_category or tms_category=='standard':
			return val
		result = super(product_product, self).onchange_tms_category(cr, uid, ids, tms_category)
		vals= result.get('value',{})
		print "########################################## VALORES", vals
		print "########################################## VALORES", vals
		if tms_category in ['move', 'real_expense', 'salary']:
			vals.update({
				'type': 'service',
				'procure_method':'make_to_stock',
				'supply_method': 'buy',
				'purchase': False,
				'sale': False,
				})
		print "################################### VALORES AL FINAL DE LAS COMPARACIONES", vals
		print "################################### VALORES AL FINAL DE LAS COMPARACIONES", vals
		return {'value': vals}
	_default = {
			}
product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
