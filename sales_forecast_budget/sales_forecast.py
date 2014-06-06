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
from tools.translate import _

class sales_forecast(osv.osv):
    _inherit = 'sales.forecast'

    _columns = {
        'budget_version_id': fields.many2one('budget.version', 'Version'),
        'budget_item_id': fields.many2one('budget.item', 'Item')
    }

    def create_budget_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        budget_line = self.pool.get('budget.line')
        
        for cur in self.browse(cr, uid, ids):
            if cur.sales_forecast_lines:
                if not cur.budget_version_id and not cur.budget_item_id:
                    raise osv.except_osv(_('Error !'), _('For create a budget line is neccessary to have a budget version and budget item at sales forecast.'))
                for line in cur.sales_forecast_lines:
                    vals = {
                        'budget_version_id': cur.budget_version_id.id,
                        'budget_item_id': cur.budget_item_id.id,
                        'name': _('Sales forecast line of ') + cur.name,
                        'product_id': line.product_id.id,
                        'amount': line.total_amount,
                        'currency_id': cur.budget_version_id.currency_id.id
                    }
                    budget_line.create(cr, uid, vals)

        return True
            

    def action_validate(self, cr, uid, ids, context=None):
        
        self.create_budget_lines(cr, uid, ids, context)
        
        return super(sales_forecast, self).action_validate(cr, uid, ids, context=context)

sales_forecast()