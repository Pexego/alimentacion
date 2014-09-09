# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Marta Vázquez Rodríguez$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields
import decimal_precision as dp

class stock_picking(osv.osv):

    _inherit = "stock.picking"

    def _amount_all(self, cr, uid, ids, field_name, arg, context):
        """compute amopunt for out picking orders"""
        res = {}
        cur_obj = self.pool.get('res.currency')

        for picking in self.browse(cr, uid, ids):
            res[picking.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'amount_gross':0.0,
                'amount_discounted': 0.0
            }

            val = val1 = val2 = val3 = 0.0
            cur = (picking.address_id and picking.address_id.partner_id.property_product_pricelist) and picking.address_id.partner_id.property_product_pricelist.currency_id or False

            for line in picking.move_lines:
                price_unit = 0.0
                if line.sale_line_id and line.state != 'cancel':
                    val1 += line.sale_line_id.price_subtotal
                    price_unit = line.sale_line_id.price_unit * (1-(line.sale_line_id.discount or 0.0)/100.0)
                    for c in self.pool.get('account.tax').compute_all(cr, uid, line.sale_line_id.tax_id, price_unit, line.product_qty, line.sale_line_id.order_id.partner_order_id.id, line.sale_line_id.product_id.id, line.sale_line_id.order_partner_id)['taxes']:
                        val += c.get('amount', 0.0)
                    val2 += (line.sale_line_id.price_unit * line.product_qty)
                    val3 += price_unit * line.product_qty

                elif line.purchase_line_id and line.state != 'cancel':
                    val1 += line.purchase_line_id.price_subtotal
                    price_unit = line.purchase_line_id.price_unit * (1-(line.purchase_line_id.discount or 0.0)/100.0)
                    for c in self.pool.get('account.tax').compute_all(cr, uid, line.purchase_line_id.taxes_id, price_unit, line.product_qty, False, line.purchase_line_id.product_id.id, False)['taxes']:
                        val += c.get('amount', 0.0)
                    val2 += (line.purchase_line_id.price_unit * line.product_qty)
                    val3 += price_unit * line.product_qty

            if cur:
                res[picking.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
                res[picking.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val3)
                res[picking.id]['amount_gross'] = cur_obj.round(cr,uid,cur,val2)
            else:
                res[picking.id]['amount_tax'] = round(val, 2)
                res[picking.id]['amount_untaxed'] = round(val3, 2)
                res[picking.id]['amount_gross'] = round(val2, 2)

            res[picking.id]['amount_total'] = res[picking.id]['amount_untaxed'] + res[picking.id]['amount_tax']
            res[picking.id]['amount_discounted'] = res[picking.id]['amount_gross'] - res[picking.id]['amount_untaxed']
        return res

    _columns = {
        'amount_untaxed': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Untaxed Amount', multi='vp', readonly=True),
        'amount_tax': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Taxes', multi='vp', readonly=True),
        'amount_total': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Total', multi='vp', readonly=True),
        'amount_gross': fields.function(_amount_all, method=True,digits_compute=dp.get_precision('Sale Price'), string='Amount gross', multi='vp', readonly=True),
        'amount_discounted': fields.function(_amount_all, method=True, digits_compute=dp.get_precision('Sale Price'), string='Discounted', multi='vp', readonly=True),
        'valued_picking': fields.boolean('Valued picking', help="If it sets to True, customer wants valued picking", readonly=True),
    }

    def onchange_partner_in(self, cr, uid, context=None, partner_id=None):
        """extend this method to fill valued_picking field"""
        res = super(stock_picking, self).onchange_partner_in(cr, uid, context=context, partner_id=partner_id)
        if not 'value' in res:
            res['value'] = {}
        if partner_id:
            address_obj = self.pool.get('res.partner.address').browse(cr, uid, partner_id)
            if address_obj.partner_id:
                res['value']['valued_picking'] = address_obj.partner_id.valued_picking
        return res

    
stock_picking()

class stock_move(osv.osv):
    
    _inherit = "stock.move"
    
    def _get_subtotal(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = {
                'price_subtotal': 0.0,
                'order_price_unit': 0.0
            }
            if move.sale_line_id:
                price_unit = (move.sale_line_id.price_unit * (1-(move.sale_line_id.discount or 0.0)/100.0))
                res[move.id]['price_subtotal'] = price_unit * move.product_qty
                res[move.id]['order_price_unit'] = price_unit
            elif move.purchase_line_id:
                price_unit = (move.purchase_line_id.price_unit * (1-(move.purchase_line_id.discount or 0.0)/100.0))
                res[move.id]['price_subtotal'] = price_unit * move.product_qty
                res[move.id]['order_price_unit'] = price_unit
        
        return res
    
    _columns = {
        'price_subtotal': fields.function(_get_subtotal, method=True, string="Subtotal", type="float", digits_compute=dp.get_precision('Sale Price'), readonly=True, multi="order_price"),
        'order_price_unit': fields.function(_get_subtotal, method=True, string="Price unit", type="float", digits_compute=dp.get_precision('Sale Price'), readonly=True, multi="order_price")
    }
    
stock_move()
