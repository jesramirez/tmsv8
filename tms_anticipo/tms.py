# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from datetime import datetime, timedelta

class tms_advance(osv.osv):
    _name = 'tms.advance'
    _inherit ='tms.advance'

    def _get_orden(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        no_orden = ""
        no_orden_list = []
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.travel_id:
                if rec.travel_id.waybill_ids:
                    for waybill in  rec.travel_id.waybill_ids:
                        if not waybill.name in no_orden_list:
                            no_orden_list.append(str(waybill.name))
            res[rec.id] = str(no_orden_list).replace('[','').replace(']','').replace("'",'') if no_orden_list else ''
        #### RESULTADO SIEMPRE RETORNAMOS {id:valor}
        return res

    _columns = {
    ##### CAMPOS FUNCIONALES #######
    'no_orden': fields.function(_get_orden, string="No. Orden",
                            type="char", size=128),

        }

    _defaults = {
        }


tms_advance()

