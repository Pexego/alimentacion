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

from openerp import models

class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _quant_create(self, cr, uid, qty, move, lot_id=False, owner_id=False,
                      src_package_id=False, dest_package_id=False,
                      force_location_from=False, force_location_to=False,
                      context=None):
        res = super(StockQuant, self)._quant_create(cr, uid, qty, move, lot_id,
                                                    owner_id, src_package_id,
                                                    dest_package_id,
                                                    force_location_from,
                                                    force_location_to,
                                                    context)
        if move.production_id:  # Is final production move
            for raw in move.production_id.move_lines:
                move.write({'parent_ids': [(4, raw.id)]})

        return res
