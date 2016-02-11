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

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,domain = [('supplier','=',True)],states={'draft': [('readonly', False)]}, select=True),
        'order_policy': fields.selection([
            ('prepaid', 'Pay before delivery'),
            ('manual', 'Deliver & invoice on demand'),
            ('picking', 'Invoice based on deliveries'),
            ('postpaid', 'Invoice on order after delivery'),
            ('no_bill', 'No bill')
        ], 'Invoice Policy', required=True, readonly=True, states={'draft': [('readonly', False)]}, change_default=True),
        
    }

    def action_ship_create(self, cr, uid, ids, context=None):
        super(sale_order, self).action_ship_create(cr, uid, ids, context=context)

        
        for order in self.browse(cr, uid, ids):
            if order.picking_ids and order.supplier_id:
                for picking in order.picking_ids:
                    if picking.state != 'cancel' and not picking.supplier_id:
                        self.pool.get('stock.picking').write(cr, uid, picking.id, {'supplier_id': order.supplier_id.id})
        return True

sale_order()

class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def product_uos_change(self, cursor, user, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        res = {}
        if product:
            product_obj = self.pool.get('product.product').browse(cursor, user, product)
            if uos:
                qty_uom = 0.0
                if self.pool.get('product.uom').browse(cursor, user, uos).category_id.id == product_obj.uos_id.category_id.id:
                    if qty_uos:
                        if product_obj.uos_coeff:
                            qty_uom = qty_uos / product_obj.uos_coeff
                            uom = product_obj.uom_id.id


                        res = self.product_id_change(cursor, user, ids, pricelist, product,
                            qty=qty_uom, uom=False, qty_uos=qty_uos, uos=uos, name=name,
                            partner_id=partner_id, lang=lang, update_tax=update_tax,
                            date_order=date_order)
                        if 'product_uom' in res['value']:
                            del res['value']['product_uom']
        return res

sale_order_line()
