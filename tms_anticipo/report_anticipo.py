# -*- coding: utf-8 -*-

from openerp.osv import fields, osv, orm
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID

class tms_advanced_report_e(osv.osv):
    _name = 'tms.advanced.report.e'
    _description = 'Reporte de Anticipos'
    _columns = {
        'name': fields.char('Herencia de Anticipos', size=4),
        }

    _defaults = {
        }

    def init(self, cr,):
        report_obj = self.pool.get('ir.actions.report.xml')
        report_id = report_obj.search(cr, SUPERUSER_ID, [('report_file','=','tms_reportess/Anticipos.rml')])
        if report_id:
            report_obj.write(cr, SUPERUSER_ID, report_id, {'report_file':'tms_anticipo/Anticipos.rml'})
        return True

tms_advanced_report_e()

