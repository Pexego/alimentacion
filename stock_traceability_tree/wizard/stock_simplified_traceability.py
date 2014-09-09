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

from openerp import models, _


class action_simplified_traceability(models.TransientModel):
    """
    This class defines a function action_traceability for wizard

    """
    _name = "action.simplified.traceability"
    _description = "Action simplified traceability "

    def action_traceability(self, cr, uid, ids, context=None):
        """ It traces the information of a product
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary of values
        """
        if context is None:
            context = {}
        type1 = context.get('type', 'simplified_parent_ids')
        quant_obj = self.pool.get("stock.quant")
        quants = quant_obj.search(cr, uid, [('lot_id', 'in', ids)],
                                  context=context)
        moves = set()
        for quant in quant_obj.browse(cr, uid, quants, context=context):
            moves |= {move.id for move in quant.history_ids
                      if not move.parent_ids or move.production_id}

        cr.execute("""select id from ir_ui_view where model=%s and
                   field_parent=%s and type=%s""", ('stock.move', type1,
                                                    'tree'))
        view_ids = cr.fetchone()
        view_id = view_ids and view_ids[0] or False
        value = {
            'domain': "[('id','in',["+','.join(map(str, moves))+"])]",
            'name': (((type1 == 'simplified_parent_ids') and
                      _('Simplified Upstream Traceability')) or
                     _('Simplified Downstream Traceability')),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'stock.move',
            'field_parent': type1,
            'view_id': (view_id, 'View'),
            'type': 'ir.actions.act_window',
            'nodestroy': True,
        }
        return value
