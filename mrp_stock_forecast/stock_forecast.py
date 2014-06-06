# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos All Rights Reserved
#    $Marta Vázquez Rodríguez$ <marta@pexego.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from osv import osv, fields

class forecast_kg_sold(osv.osv):
    _name = 'forecast.kg.sold'
    _description = 'Forecast of kg moved'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Account',
                                        required=True),
        'commercial_id': fields.many2one('res.users', 'Commercial'),
        'date': fields.date('Date'),
        'kgsold_forecast_lines': fields.one2many('forecast.kg.sold.line',
                                                'kgsold_forecast_id', 'Lines'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([
                                ('draft','Draft'),
                                ('approve', 'Approved'),
                                ('cancel', 'Cancel')], string="State",
                                required=True, readonly=True)
    }

    _defaults = {
        'state': 'draft',
        'commercial_id': lambda obj, cr, uid, context: uid,
    }

    def action_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        return True

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
forecast_kg_sold()

class forecast_kg_sold_line(osv.osv):
    _name = 'forecast.kg.sold.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'kgsold_forecast_id': fields.many2one('forecast.kg.sold', 'Forecast kg sold',
                                                required=True, ondelete='cascade'),
        'format_id': fields.many2one('product.format',
                                        'Product Format'),
        'notes': fields.char('Notes', size=32),
        'jan_kg': fields.float('Jan Kg'),
        'feb_kg': fields.float('Feb Kg'),
        'mar_kg': fields.float('Mar Kg'),
        'apr_kg': fields.float('Apr Kg'),
        'may_kg': fields.float('May Kg'),
        'jun_kg': fields.float('Jun Kg'),
        'jul_kg': fields.float('Jul Kg'),
        'aug_kg': fields.float('Aug Kg'),
        'sep_kg': fields.float('Sep Kg'),
        'oct_kg': fields.float('Oct Kg'),
        'nov_kg': fields.float('Nov Kg'),
        'dec_kg': fields.float('Dec Kg'),

    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'forecast.kg.sold.line') or '/'
    }
forecast_kg_sold_line()