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

class stock_move(osv.osv):
    _inherit = 'stock.move'
    
    # def write(self, cr, uid, ids, vals, context=None):
    #     if context is None:
    #         context = {}
    #
    #     if isinstance(ids,(int,long)):
    #         ids = [ids]
    #     res = super(stock_move, self).write(cr, uid, ids, vals, context=context)
    #     if vals.get('prodlot_id', False):
    #         for move in self.browse(cr, uid, ids):
    #             if move.production_ids and move.production_ids[0].picking_id and move.production_ids[0].picking_id.move_lines:
    #                 for line in move.production_ids[0].picking_id.move_lines:
    #                     if line.product_id and line.product_id.id == move.product_id.id \
    #                             and (line.prodlot_id and line.prodlot_id.id != vals['prodlot_id'] or not line.prodlot_id):
    #                         self.pool.get('stock.move').write(cr, uid, line.id, {'prodlot_id': vals['prodlot_id']})
    #     return res

stock_move()
