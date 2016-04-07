# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@argil.mx)
############################################################################
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


class ifrs_lines(osv.osv):
    _inherit = 'ifrs.lines'


    def _get_amount_with_operands(self, cr, uid, ids, ifrs_line, period_info=None, fiscalyear=None, exchange_date=None, currency_wizard=None, number_month=None, target_move=None, pd=None, undefined=None, two=None, is_compute=None, context=None):
        if context is None:
            context = {}
        """ Integrate operand_ids field in the calculation of the amounts for each line
        @param ifrs_line: linea a calcular monto
        @param period_info: informacion de los periodos del fiscal year
        @param fiscalyear: selected fiscal year
        @param exchange_date: date of change currency
        @param currency_wizard: currency in the report
        @param number_month: period number
        @param target_move: target move to consider
        @param is_compute: si el metodo actualizara el campo amount para la vista
        """
        ifrs_line = self.browse(cr, uid, ifrs_line.id)
        if not number_month:
            context.update({'whole_fy': 'True'})
        if is_compute:
            field_name = 'amount'
        else:
            if context.get('whole_fy', False):
                field_name = 'ytd'
            else:
                field_name = 'period_%s' % str(number_month)

        res = self._get_amount_value(
            cr, uid, ids, ifrs_line, period_info, fiscalyear, exchange_date,
            currency_wizard, number_month, target_move, pd, undefined, two, is_compute, context=context)

        res = ifrs_line.inv_sign and (-1.0 * res) or res
        self.write(cr, uid, ifrs_line.id, {field_name: res})

        return res
    
    
    def _get_amount_value(self, cr, uid, ids, ifrs_line=None, period_info=None, fiscalyear=None, exchange_date=None, currency_wizard=None, number_month=None, target_move=None, pd=None, undefined=None, two=None, is_compute=None, context=None):
        if context is None:
            context = {}
        """ Returns the amount corresponding to the period of fiscal year
        @param ifrs_line: linea a calcular monto
        @param period_info: informacion de los periodos del fiscal year
        @param fiscalyear: selected fiscal year
        @param exchange_date: date of change currency
        @param currency_wizard: currency in the report
        @param number_month: period number
        @param target_move: target move to consider
        @param is_compute: si el metodo actualizara el campo amount para la vista
        """

        from_currency_id = ifrs_line.ifrs_id.company_id.currency_id.id
        to_currency_id = currency_wizard

        ifrs_line = self.browse(cr, uid, ifrs_line.id)
        if number_month:
            if two:
                context.update({'period_from': number_month, 'period_to': number_month})
            else:
                period_id = period_info[number_month][1]
                context.update({'period_from': period_id, 'period_to': period_id})
        else:
            context.update({'whole_fy': 'True'})

        context['partner_detail'] = pd
        context['fiscalyear'] = fiscalyear
        context['state'] = target_move
        if ifrs_line.type == 'detail':
            res = self._get_sum_detail(cr, uid, ifrs_line.id, number_month,
                    is_compute, context=context)
        elif ifrs_line.type == 'total':
            res = self._get_grand_total(cr, uid, ifrs_line.id, number_month,
                    is_compute, context=context)
        elif ifrs_line.type == 'constant':
            res = self._get_constant(cr, uid, ifrs_line.id, number_month,
                    is_compute, context=context)
        else:
            res = 0.0

        if ifrs_line.type == 'detail':
            res = self.exchange(
                cr, uid, ids, res, to_currency_id, from_currency_id, exchange_date, context=context)
        # Total amounts come from details so if the details are already
        # converted into the regarding currency then it is not useful to do at
        # total level
        # elif ifrs_line.type == 'total':
        #    if ifrs_line.operator not in ('percent', 'ratio'):
        #        if ifrs_line.comparison not in ('percent', 'ratio', 'product'):
        #            res = self.exchange(
        #                cr, uid, ids, res, to_currency_id, from_currency_id, exchange_date, context=context)
        return res    

class ifrs_report_wizard(osv.osv_memory):
    _inherit = "ifrs.report.wizard"

    _columns = {
        #'employee_ids': fields.many2many('hr.employee', 'account_mx_reports_employee_rel', 'account_id', 'employee_id', 'Operadores', required=False),
        'vehicle_ids' : fields.many2many('fleet.vehicle', 'account_mx_ifrs_vehicle_rel', 'account_id', 'vehicle_id', 'Vehicles', required=False),
        }


    def init(self, cr,):
        report_obj = self.pool.get('ir.actions.report.xml')        
        report_ids = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','ifrs_report/report/report_webkit_html.mako')])
        if report_ids:
            report_obj.write(cr, SUPERUSER_ID, report_ids, {'report_file':'tms_ifrs_vehicle_filter/report/report_webkit_html.mako'})
        report_ids = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','ifrs_report/report/report_webkit_html_12.mako')])
        if report_ids:
            report_obj.write(cr, SUPERUSER_ID, report_ids, {'report_file':'tms_ifrs_vehicle_filter/report/report_webkit_html_12.mako'})
        report_ids = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','ifrs_report/report/report_webkit_html.mako')])
        if report_ids:
            report_obj.write(cr, SUPERUSER_ID, report_ids, {'report_file':'tms_ifrs_vehicle_filter/report/report_webkit_html.mako'})
        report_ids = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','ifrs_report/report/report_webkit_html_12.mako')])
        if report_ids:
            report_obj.write(cr, SUPERUSER_ID, report_ids, {'report_file':'tms_ifrs_vehicle_filter/report/report_webkit_html_12.mako'})
        return True    
    
    def print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        result =  super(ifrs_report_wizard, self).print_report(cr, uid, ids, context=context)
        wizard_ifrs = self.browse(cr, uid, ids, context=context)[0]
        vehicle_ids = []
        vehicle_names = ""
        for x in wizard_ifrs.vehicle_ids:
            vehicle_ids.append(x.id)
            vehicle_names += x.name + ","
        result['datas']['vehicle_names'] = vehicle_names and vehicle_names[:len(vehicle_names)-1] or ""
        result['datas']['vehicle_ids'] = vehicle_ids
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
