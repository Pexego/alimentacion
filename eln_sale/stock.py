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

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,domain = [('supplier','=',True)],states={'draft': [('readonly', False)]}, select=True),
        'carrier_id': fields.many2one('res.partner', 'Carrier', readonly=True, states={'draft': [('readonly', False)]}, select=True)
    }
stock_picking()
class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True,domain = [('supplier','=',True)],states={'draft': [('readonly', False)]}, select=True)
    }
stock_move()