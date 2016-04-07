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


from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import calendar

class week_days(osv.osv):
    _name = 'week.days'

    _columns = {
        'name': fields.char('Name', size=256, required=True),
        # 'partner_p_id': fields.many2one('res.partner',' ID P' ),
        # 'partner_r_id': fields.many2one('res.partner',' ID R' ),
        # 'partner_id': fields.many2one('res.partner', 'ID partner'),

    }


week_days() 


# TMS - Special Category for TMS module
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        # 'mo_r': fields.boolean('Mon'),
        # 'tu_r': fields.boolean('Tue'),
        # 'we_r': fields.boolean('Wed'),
        # 'th_r': fields.boolean('Thu'),
        # 'fr_r': fields.boolean('Fri'),
        # 'sa_r': fields.boolean('Sat'),
        # 'su_r': fields.boolean('Sun'),

        # 'mo_p': fields.boolean('Mon'),
        # 'tu_p': fields.boolean('Tue'),
        # 'we_p': fields.boolean('Wed'),
        # 'th_p': fields.boolean('Thu'),
        # 'fr_p': fields.boolean('Fri'),
        # 'sa_p': fields.boolean('Sat'),
        # # 'su_p': fields.boolean('Sun'),
        # 'revision_week_r_ids': fields.one2many('week.days', 'partner_r_id', 'Revision Days Add'),
        # 'revision_week_p_ids': fields.one2many('week.days', 'partner_p_id', 'Paydays Add'),
        'revision_week_r_ids': fields.many2many('week.days', 'partner_week_period_rel_r', 'partner_id', 'week_id', 'Revision Days Add'),
        'revision_week_p_ids': fields.many2many('week.days', 'partner_week_period_rel_p', 'partner_id', 'week_id', 'Paydays Add'),
        'revision_schedule': fields.char('Revision schedule', size=512),
        'payment_schedule': fields.char('Payment schedule', size=512),
        'credit_days': fields.integer('Credit Days'),
        'notes_payment': fields.text('Notes'),

        'charging_equipment_ids': fields.one2many('charging.equipment', 'parent_r_id', 'Chargind and Equipment'),
        'path_flow': fields.selection([('fedetal','Federal'), ('expressway','Expressway'), ('both','Both')], 'Path to Flow'), 
        'kit_id': fields.many2one('tms.unit.kit','Configuration Kit' ),
        'banners_p':  fields.integer('Banners'),
        'bands_p':  fields.integer('Bands'),
        'chains': fields.integer('Chains'),
        'gatas':  fields.integer('Gatas'),
        'polines':  fields.integer('Polines'),
        'tables': fields.integer('Tables'),
        'other': fields.char('Other', size=512),
        'charge_insurance': fields.selection([('uninsured','Uninsured'), ('customer','Customer'), ('carrier','Carrier')], 'Charge Insurance'),
        'insurance': fields.many2one('res.partner', 'Insurance'),
        'observation': fields.text('Observations'),
        # 'child_payment_ids': fields.one2many('res.partner.category', 'parent_r_id', 'Child Categories Payment'),

    }

    _defaults = {

    }

res_partner()

class charging_equipment(osv.osv):
    _name = 'charging.equipment'
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one('product.product','Product' ),
        'measures': fields.char('Measures', size=512),
        'tons_month': fields.integer('Emb. Tons/Month'),
        'origin': fields.char('Origin', size=512),
        'destination': fields.char('Destination', size=512),
        'parent_r_id': fields.many2one('res.partner',' ID R' ),
        'note': fields.char('Description', size=512),
        # 'partner_id': fields.many2one('res.partner', 'ID partner'),

    }


charging_equipment() 




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: