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

class tms_time(osv.Model):
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'tms.time'
    _description = 'Activity Control Time'
    _rec_name='event'

########################### Columnas : Atributos #######################################################################
    _columns = {
        'date_event': fields.datetime('Date Event'),
        'event': fields.selection([('process','Process'), ('pause','Pause'), ('end','End')],'Event'),

        ########Many2One###########
        'control_time_id': fields.many2one('tms.activity.control.time','Control Time'),
    }
    
########################### Metodos ####################################################################################

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj 

########################### Valores por Defecto ########################################################################
    #_defaults = {
        #'state'                 : lambda *a: 'draft',
    #}

########################### Criterio de ordenamiento ###################################################################
    #_order = 'name'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
