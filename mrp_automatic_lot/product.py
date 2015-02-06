# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
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

"""add functionally for differentiate miscible products and not"""

from osv import fields, osv
from tools.translate import _

class product_product(osv.osv):
    """add functionally for differentiate miscible product and not miscible product"""
    _inherit = "product.product"

    _columns = {
                'transfer_lot': fields.boolean('Transfer Lot', help="When confirm production order, will copy the lot of the first product to the one to be produced"),
                'transfer_lot_date': fields.boolean('Tranfiere fecha de lote',
                                                    help="Al confirmar una orden de producción de este producto se transferirá la fecha de caducidad del primer lote a consumir encontrado"),
                }
    _defaults = {
                 'transfer_lot': lambda *a: 0,
                 'transfer_lot_date': lambda *a: 0,
                 }
