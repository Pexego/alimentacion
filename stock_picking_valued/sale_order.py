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
from osv import osv

class sale_order(osv.osv):
    _inherit = "sale.order"

    def action_ship_create(self, cr, uid, ids, *args):
        """extend this method to add valued_picking field to picking"""
        res = super(sale_order, self).action_ship_create(cr, uid, ids, args)

        for order in self.browse(cr, uid, ids):
            pickings = [x.id for x in order.picking_ids]
            if pickings:
                self.pool.get('stock.picking').write(cr, uid, pickings, {'valued_picking': order.partner_id.valued_picking})

        return res
sale_order()