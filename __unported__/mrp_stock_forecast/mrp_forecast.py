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
############################################################################
from osv import osv, fields

class mrp_forecast(osv.osv):
    _name = 'mrp.forecast'
    _description = 'Forecast of producion hours'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'date': fields.date('Date'),
        'mrp_forecast_lines': fields.one2many('mrp.forecast.line',
                                                'mrp_forecast_id', 'Lines'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([
                                ('draft','Draft'),
                                ('approve', 'Approved'),
                                ('cancel', 'Cancel')], string="State",
                                required=True, readonly=True)
    }
    _defaults = {
        'state': 'draft',
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
mrp_forecast()

class mrp_forecast_line(osv.osv):
    _name = 'mrp.forecast.line'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'mrp_forecast_id': fields.many2one('mrp.forecast', 'MRP Forecast',
                                                required=True, ondelete='cascade'),
        'workcenter_id': fields.many2one('mrp.workcenter', 'Workcenter',
                                                required=True),
        'jan_hours': fields.float('Jan Hrs'),
        'feb_hours': fields.float('Feb Hrs'),
        'mar_hours': fields.float('Mar Hrs'),
        'apr_hours': fields.float('Apr Hrs'),
        'may_hours': fields.float('May Hrs'),
        'jun_hours': fields.float('Jun Hrs'),
        'jul_hours': fields.float('Jul Hrs'),
        'aug_hours': fields.float('Aug Hrs'),
        'sep_hours': fields.float('Sep Hrs'),
        'oct_hours': fields.float('Oct Hrs'),
        'nov_hours': fields.float('Nov Hrs'),
        'dec_hours': fields.float('Dec Hrs'),

        'jan_real_time': fields.float('Jan Real Time'),
        'feb_real_time': fields.float('Feb Real Time'),
        'mar_real_time': fields.float('Mar Real Time'),
        'apr_real_time': fields.float('Apr Real Time'),
        'may_real_time': fields.float('May Real Time'),
        'jun_real_time': fields.float('Jun Real Time'),
        'jul_real_time': fields.float('Jul Real Time'),
        'aug_real_time': fields.float('Aug Real Time'),
        'sep_real_time': fields.float('Sep Real Time'),
        'oct_real_time': fields.float('Oct Real Time'),
        'nov_real_time': fields.float('Nov Real Time'),
        'dec_real_time': fields.float('Dec Real Time'),

    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'mrp.forecast.line') or '/'
    }
mrp_forecast_line()