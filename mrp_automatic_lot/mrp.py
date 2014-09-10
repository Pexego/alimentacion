# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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

from openerp import models, fields, api


class MrpProduction(models.Model):

    _inherit = "mrp.production"

    final_lot_id = fields.Many2one("stock.production.lot", 'Final Lot')

    def _make_production_produce_line(self, cr, uid, production, context=None):
        res = super(MrpProduction, self).\
            _make_production_produce_line(cr, uid, production, context=context)

        lot_obj = self.pool.get('stock.production.lot')
        product_id = production.product_id.id
        prodlot_id = lot_obj.create(cr, uid,
                                    {'product_id': product_id},
                                    context={'product_id': product_id})
        production.write({'final_lot_id': prodlot_id})

        return res
