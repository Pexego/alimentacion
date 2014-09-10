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

from openerp import models, api, fields


class MrpProductProduce(models.TransientModel):

    _inherit = "mrp.product.produce"

    def _get_limit_lot(self):
        if self.env.context.get('active_id', False):
            prod_obj = self.env["mrp.production"].\
                browse(self.env.context['active_id'])
            if prod_obj.final_lot_id:
                return True
        return False

    def _get_final_lot(self):
        if self.env.context.get('active_id', False):
            prod_obj = self.env["mrp.production"].\
                browse(self.env.context['active_id'])
            if prod_obj.final_lot_id:
                return prod_obj.final_lot_id.id
        return False

    with_final_lot = fields.Boolean("With final lot", default=_get_limit_lot)
    lot_id = fields.Many2one('stock.production.lot', 'Lot',
                             default=_get_final_lot)
