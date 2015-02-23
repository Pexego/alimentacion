# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, _, api, SUPERUSER_ID
from openerp.osv import fields


class StockMove(models.Model):

    _inherit = "stock.move"

    def _get_move_type(self, cr, uid, ids, field_name, arg, context=None):
        """return the type of moves"""
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.picking_id and move.picking_id.\
                    picking_type_code != "internal":
                if move.location_id.usage == 'customer':
                    res[move.id] = _('RETURN')
                elif move.location_dest_id.usage == 'supplier':
                    res[move.id] = _('RETURN')
                elif move.picking_id.picking_type_code == 'incoming':
                    res[move.id] = _('IN')
                elif move.picking_id.picking_type_code == 'outgoing':
                    res[move.id] = _('OUT')
                else:
                    res[move.id] = False
            else:
                if move.location_dest_id.usage == 'customer':
                    res[move.id] = _('OUT')
                elif move.scrapped:
                    res[move.id] = _('SCRAP')
                elif move.location_dest_id.usage == 'inventory':
                    res[move.id] = _('INVENTORY')
                elif move.location_id.usage == 'inventory':
                    res[move.id] = _('FROM INVENTORY')
                elif move.location_dest_id.usage == 'production':
                    res[move.id] = _('PRODUCTION')
                elif move.location_dest_id.usage == 'production':
                    res[move.id] = _('PRODUCTION FINAL MOVE')
                elif move.location_dest_id.usage == 'procurement':
                    res[move.id] = _('PROCUREMENT')
                elif move.location_dest_id.usage == 'transit':
                    res[move.id] = _('TRANSIT')
                else:
                    res[move.id] = _('INTERNAL')
        return res

    def _get_simplified_trace_up(self, cr, uid, ids, field_name, arg, context):
        """get the last childs moves for a specific move"""
        res = {}
        for move in self.browse(cr, uid, ids):
            cr.execute("select id from stock_move_parents(%s)", (move.id,))
            records = []
            for record in cr.fetchall():
                records.append(record[0])
            if records[0] in ids:
                res[move.id] = []
            else:
                res[move.id] = records
        return res

    def _get_simplified_trace_down(self, cr, uid, ids, field_name, arg,
                                   context):
        """get the top parents moves for a specific move"""
        res = {}
        for move in self.browse(cr, uid, ids):
            cr.execute("select id from stock_move_childs(%s)", (move.id,))
            records = []
            for record in cr.fetchall():
                records.append(record[0])
            if records[0] in ids:
                res[move.id] = []
            else:
                res[move.id] = records
        return res

    def _get_related_lots_str(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = u", ".join([x.name for x in move.lot_ids])

        return res


    _columns = {
        'child_ids': fields.many2many('stock.move', 'stock_move_trace_rel',
                                      'parent_id', 'child_id', 'Child moves'),
        'parent_ids': fields.many2many('stock.move', 'stock_move_trace_rel',
                                       'child_id', 'parent_id',
                                       'Parent moves'),
        'move_type': fields.function(_get_move_type, method=True,
                                     type="char", readonly=True,
                                     string="Move type"),
        'simplified_parent_ids': fields.function(_get_simplified_trace_up,
                                                 method=True,
                                                 relation='stock.move',
                                                 type="many2many",
                                                 string='First parents'),
        'simplified_child_ids': fields.function(_get_simplified_trace_down,
                                                method=True,
                                                relation='stock.move',
                                                type="many2many",
                                                string='Last childs'),
        'lot_str': fields.function(_get_related_lots_str, method=True,
                                   type="char", string="Lots",
                                   readonly=True)
    }


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def move_quants_write(self, cr, uid, quants, move, location_dest_id,
                          dest_package_id, context=None):
        for q in quants:
            last_move = self._get_latest_move(cr, uid, q, context=context)
            if last_move:
                last_move.write({'child_ids': [(4, move.id)]})
        super(StockQuant, self).move_quants_write(cr, uid, quants, move,
                                                  location_dest_id,
                                                  dest_package_id,
                                                  context=context)

    @api.cr_uid_ids_context
    def _quants_merge(self, cr, uid, solved_quant_ids, solving_quant,
                      context=None):
        solved_quant = self.browse(cr, SUPERUSER_ID, solved_quant_ids[0],
                                   context=context)
        last_move = self._get_latest_move(cr, uid, solved_quant,
                                          context=context)
        for move in solving_quant.history_ids:
            move.write({'child_ids': [(4, last_move.id)]})

        super(StockQuant, self)._quants_merge(cr, uid, solved_quant_ids,
                                              solving_quant, context=context)

    _columns = {
        'move_ids': fields.many2many('stock.move', 'stock_quant_move_rel',
                                     'quant_id', 'move_id', 'Moved Quants'),
    }


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    def action_tree_traceability(self, cr, uid, ids, context=None):
        """ It traces the information of a product
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary of values
        """
        value = self.pool.get('action.traceability').\
            action_traceability(cr, uid, ids, context)
        return value

    def action_simplified_tree_traceability(self, cr, uid, ids, context=None):
        """ It traces the information of a product
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary of values
        """
        value = self.pool.get('action.simplified.traceability').\
            action_traceability(cr, uid, ids, context)
        return value

    def _get_related_moves(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for lot in self.browse(cr, uid, ids):
            if lot.quant_ids:
                moves = []
                for quant in lot.quant_ids:
                    for move in quat.move_ids:
                        moves.append(move.id)

                res[lot.id] = list(set(moves))
            else:
                res[lot.id] = []
        return res

    def _search_moves(self, cr, uid, obj, name, args, context=None):
        if not len(args):
            return []
        move_pool = self.pool['stock.move']
        final_lots = set()
        for arg in args:
            moves = []
            lots = []
            if arg[2]:
                moves = move_pool.browse(cr, uid, arg[2])
            for move in moves:
                lots.extend([x.id for x in move.lot_ids])
            lots = set(lots)
            if lots and arg[1] in ["in", "="]:
                final_lots |= lots
            elif lots and arg[1] in ["not in", "!="]:
                final_lots -= lots

        if not final_lots:
            return [('id', '=', 0)]
        return [('id', 'in', list(final_lots))]

    _columns = {
        'move_related_ids': fields.function(_get_related_moves,
                                            method=True,
                                            relation='stock.move',
                                            type="many2many",
                                            string='Related moves',
                                            fnct_search=_search_moves)
    }
