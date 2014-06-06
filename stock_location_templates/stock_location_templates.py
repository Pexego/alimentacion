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
from osv import osv,fields

class stock_location_templates(osv.osv):
    _name = 'stock.location.templates'
    _description = 'Templates logistics flows'
    _columns = {
        'name': fields.char('Name', size=64, required=True, select=True),
        'flow_pull_ids': fields.one2many('product.pulled.flow', 'template_id', 'Pulled Flows'),
        'path_ids': fields.one2many('stock.location.path', 'template_id',
            'Pushed Flow',
            help="These rules set the right path of the product in the "\
            "whole location tree."),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        
    }
    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.pulled.flow', context=c),
    }
stock_location_templates()

class stock_location_path(osv.osv):
    _inherit = "stock.location.path"
    _columns = {
        'template_id': fields.many2one('stock.location.templates', 'Template')
    }
stock_location_path()

class product_pulled_flow(osv.osv):
    _inherit = 'product.pulled.flow'
    _columns = {
        'template_id': fields.many2one('stock.location.templates', 'Template')
    }
product_pulled_flow()

