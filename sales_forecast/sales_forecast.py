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

class sales_forecast(osv.osv):

    _name = 'sales.forecast'
    _description = 'Sales forecast'
    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'analytic_id': fields.many2one('account.analytic.account', 'Account',
                                        required=True),
        'commercial_id': fields.many2one('res.users', 'Commercial'),
        'date': fields.date('Date'),
        'sales_forecast_lines': fields.one2many('sales.forecast.line',
                                                'sales_forecast_id', 'Lines'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([
                                ('draft','Draft'),
                                ('done', 'Done'),
                                ('approve', 'Approved'),
                                ('cancel', 'Cancel')], string="State",
                                required=True, readonly=True)
    }
    _defaults = {
        'state': 'draft',
        'commercial_id': lambda obj, cr, uid, context: uid,
    }

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def action_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        return True

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

sales_forecast()

class sales_forecast_line(osv.osv):

    _name = 'sales.forecast.line'
    _description = 'Sales forecast lines'

    def _get_total_amount(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.jan_amount + line.feb_amount + line.mar_amount + \
                           line.apr_amount + line.may_amount + line.jun_amount + \
                           line.jul_amount + line.aug_amount + line.sep_amount + \
                           line.oct_amount + line.nov_amount + line.dec_amount
        return res

    def _get_total_qty(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.jan_qty + line.feb_qty + line.mar_qty + \
                           line.apr_qty + line.may_qty + line.jun_qty + \
                           line.jul_qty + line.aug_qty + line.sep_qty + \
                           line.oct_qty + line.nov_qty + line.dec_qty
        return res

    _columns = {
        'name': fields.char('Name', size=255, required=True),
        'sales_forecast_id': fields.many2one('sales.forecast', 'Sales forecast',
                                                required=True, ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product',
                                        required=True),
        'jan_qty': fields.float('Qty', digits=(16,2)),
        'jan_amount': fields.float('€', digits=(16,2)),
        'feb_qty': fields.float('Qty', digits=(16,2)),
        'feb_amount': fields.float('€', digits=(16,2)),
        'mar_qty': fields.float('Qty', digits=(16,2)),
        'mar_amount': fields.float('€', digits=(16,2)),
        'apr_qty': fields.float('Qty', digits=(16,2)),
        'apr_amount': fields.float('€', digits=(16,2)),
        'may_qty': fields.float('Qty', digits=(16,2)),
        'may_amount': fields.float('€', digits=(16,2)),
        'jun_qty': fields.float('Qty', digits=(16,2)),
        'jun_amount': fields.float('€', digits=(16,2)),
        'jul_qty': fields.float('Qty', digits=(16,2)),
        'jul_amount': fields.float('€', digits=(16,2)),
        'aug_qty': fields.float('Qty', digits=(16,2)),
        'aug_amount': fields.float('€', digits=(16,2)),
        'sep_qty': fields.float('Qty', digits=(16,2)),
        'sep_amount': fields.float('€', digits=(16,2)),
        'oct_qty': fields.float('Qty', digits=(16,2)),
        'oct_amount': fields.float('€', digits=(16,2)),
        'nov_qty': fields.float('Qty', digits=(16,2)),
        'nov_amount': fields.float('€', digits=(16,2)),
        'dec_qty': fields.float('Qty', digits=(16,2)),
        'dec_amount': fields.float('€', digits=(16,2)),
        'total_qty': fields.function(_get_total_qty, type="float", 
                                    digits=(16,2), string="Total Qty.", readonly=True),
        'total_amount': fields.function(_get_total_amount, type="float", 
                                    digits=(16,2), string="Total €", readonly=True),
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'sales.forecast.line') or '/'
    }

    def on_change_amount(self, cr, uid, ids, amount=0.0, field='', product_id=False, context=None):
        if context is None:
            context = {}

        res = {}

#        if amount and field != '' and product_id:
#            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
#            #TODO al cambiar los € rellenar la cantidad según tarifa
#            res[field + '_qty'] = 0.0

        return {'value': res}

    def on_change_qty(self, cr, uid, ids, qty=0.0, field='', product_id=False, context=None):
        if context is None:
            context = {}

        res = {}

#        if amount and field != '' and product_id:
#            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
#            #TODO al cambiar la cantidad rellenar los € según tarifa
#            res[field + '_amount'] = 0.0

        return {'value': res}


sales_forecast_line()