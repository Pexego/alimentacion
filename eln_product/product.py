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
import decimal_precision as dp
import time
from datetime import datetime

class product_options_product(osv.osv):
    _name = 'product.options.product'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'option_id': fields.many2one('product.options', 'Option'),
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.options.product') or '/',
    }
product_options_product()
class product_verifications_product(osv.osv):
    _name = 'product.verifications.product'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_id': fields.many2one('product.product', 'Product'),
        'verification_id': fields.many2one('product.verifications', 'Verification'),
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.verifications.product') or '/',
    }
product_options_product()

class product_revisions(osv.osv):
    _name = 'product.revision'

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'user_id': fields.many2one('res.users', 'User'),
        'date': fields.date('Date'),
        'product_id': fields.many2one('product.product', 'Product'),
        'description': fields.text('Description')

    }
    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'date':lambda *a: time.strftime("%Y-%m-%d"),
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.revision') or '/',
    }
    
product_revisions

class product_sheet_shipments(osv.osv):
    _name = 'product.sheet.shipments'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'contact_id': fields.many2one('res.partner', 'Contact', required=True),
        'date': fields.date('Date', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'revision': fields.char('Rev.', size=255, readonly=True)
    }
    _defaults = {
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'product.sheet.shipments') or '/',
    }
product_sheet_shipments()

class product_product(osv.osv):
    _inherit = 'product.product'
    def _get_last_revision(self, cr, uid, ids, field_name, arg, context):

        res = {}
        revisions = []
        last_revision = ""
        for line in self.browse(cr, uid, ids, context=context):
            revisions = self.pool.get('product.revision').search(cr, uid, [('product_id','=',line.id)], order="date desc")
            if revisions:
                rev = self.pool.get('product.revision').browse(cr, uid, revisions[0])
                date = datetime.strptime(rev.date, "%Y-%m-%d")
                last_revision = rev.name + " (" + date.strftime("%d/%m/%Y") + ")"
            res[line.id] = last_revision

        return res
    def _get_name_packaging(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        packs = []
        name = ''
        for line in self.browse(cr, uid, ids, context=context):
            packs = self.pool.get('product.packaging').search(cr, uid, [('product_id','=', line.id),('sequence','=', 2)])
            if packs:
                pack_obj = self.pool.get('product.packaging').browse(cr, uid, packs[0])
                if pack_obj.ul and pack_obj.ul.name:
                    name = pack_obj.ul.name
            res[line.id] = name
        return res
    def _get_ldm_last_revision(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        revisions = []
        boms = []
        last_revision = ""
        for line in self.browse(cr, uid, ids, context=context):
            boms = self.pool.get('mrp.bom').search(cr, uid, [('product_id','=', line.id)])
            if boms:
                bom_id = self.pool.get('mrp.bom').browse(cr, uid, boms[0])
                if bom_id.revision_ids:
                    revisions = self.pool.get('mrp.bom.revision').search(cr, uid, [('bom_id','=',bom_id.id)], order='date desc')
                    if revisions:
                        rev = self.pool.get('mrp.bom.revision').browse(cr, uid, revisions[0])
                        date = datetime.strptime(rev.date, "%Y-%m-%d")
                        last_revision=rev.name + " (" + date.strftime("%d/%m/%Y") + ")"
            res[line.id] = last_revision

        return res

    def _get_heights(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        rows = 0
        for product in self.browse(cr, uid, ids, context=context):
            if product.packaging:
                for pack in product.packaging:
                    if pack.ul.type == 'pallet':
                        rows = pack.rows
                        break
            res[product.id] = rows
        print res
        return res
    def _get_boxes_base(self, cr, uid, ids, field_name, arg, context=None):
       
        res = {}
        ul_qty = 0
        for product in self.browse(cr, uid, ids, context=context):
            if product.packaging:
                for pack in product.packaging:
                    if pack.ul.type == 'pallet':
                        ul_qty = pack.ul_qty
                        break
            res[product.id] = ul_qty
        print res
        return res

    def _get_boxes_palet(self, cr, uid, ids, field_name, arg, context=None):
        
        res = {}
        qty = 0.0
        for product in self.browse(cr, uid, ids, context=context):
            if product.packaging:
                for pack in product.packaging:
                    if pack.ul.type == 'pallet':
                        qty  = pack.qty
                        break
            res[product.id] = qty

        print res
        return res
    _columns = {
        'product_ingredient_ids': fields.one2many('product.ingredient', 'product_parent_id', string="Ingredients"),
        'protective_atmosphere': fields.boolean('Protective atmosphere'),
        'perforated_bag': fields.boolean('Perforated bag'),
        'energy': fields.float('Energy', digits_compute=dp.get_precision('Product UoM')),
        'carbohydrates': fields.float('Carbohydrates', digits_compute=dp.get_precision('Product UoM')),
        'carbo_sugar': fields.float('of which sugars', digits_compute=dp.get_precision('Product UoM')),
        'fats': fields.float('Fats', digits_compute=dp.get_precision('Product UoM')),
        'fat_saturates': fields.float('of which saturates', digits_compute=dp.get_precision('Product UoM')),
        'proteins': fields.float('Proteins', digits_compute=dp.get_precision('Product UoM')),
        'salt': fields.float('Salt', digits_compute=dp.get_precision('Product UoM')),
        'storage_conditions': fields.text('Storage conditions'),
        'expected_use': fields.text('Expected use'),
        'allergen': fields.text('Allergen'),
        'ogms': fields.text('OGMs'),
        'comments_product_sheet': fields.char('Comments (product sheet)', size=255),
        'comments_sheet': fields.char('Comments (sheet)', size=255),
        'comments_product_logistics_sheet': fields.char('Comments (product logistics sheet)', size=255),
        'palletizing': fields.binary('Palletizing'),
        'provision_boxes_base': fields.binary('Provision of boxes base'),
        'format': fields.char('Format', size=64),
        'comercial_format': fields.char('Comercial format', size=255),
        'box': fields.many2one('product.product', 'Box'),
        'bag_length': fields.char('Bag length', size=64),
        'bobbin': fields.many2one('product.product', 'Bobbin'),
        'bag': fields.many2one('product.product', 'Bag'),
        'others': fields.many2one('product.product', 'Others'),
        'seal': fields.many2one('product.product', 'Seal'),
        'allergen_labeling': fields.boolean('Allergen labeling'),
        'gluten_free_labeling': fields.boolean('Gluten free labeling'),
        'parameter_ids': fields.one2many('product.parameter.product', 'product_id', 'Parameters'),
        'option_ids':fields.one2many('product.options.product', 'product_id', 'Options'),
        'verification_ids':fields.one2many('product.verifications.product', 'product_id', 'Verfications'),
        'revision_ids': fields.one2many('product.revision', 'product_id', 'Revisions'),
        'shipments_ids': fields.one2many('product.sheet.shipments', 'product_id', 'Shipments'),
        'partner_product_code': fields.char('Partner code', size=64),
        'dun14': fields.char('DUN14', size=64),
        'last_revision': fields.function(_get_last_revision,readonly=True,string='Last revision', type='char',size=255),
        'boxes_palet3': fields.function(_get_boxes_palet, digits_compute= dp.get_precision('Sale Price'), string='Boxes x palet'),
        'boxes_base3': fields.function(_get_boxes_base, type="integer", string='Boxes of base'),
        'heights3': fields.function(_get_heights, type="integer", string='Heights'),
        'last_revision_ldm': fields.function(_get_ldm_last_revision,readonly=True,string='Last revision LdM', type='char',size=255),
        'company_product_code': fields.char('Company code', size=64),
        'packaging_seq2': fields.function(_get_name_packaging,readonly=True,string='Name pack. box', type='char',size=255),
        'written_by': fields.many2one('hr.employee','Written by'),
        'written_signature': fields.binary('Signature'),
        'written_job': fields.many2one('hr.job', 'Job'),
        'reviewed_by': fields.many2one('hr.employee','Reviewed by'),
        'reviewed_signature': fields.binary('Signature'),
        'reviewed_job': fields.many2one('hr.job', 'Job'),
        'approved_by': fields.many2one('hr.employee','Approved by'),
        'approved_signature': fields.binary('Signature'),
        'approved_job': fields.many2one('hr.job', 'Job'),
        'recommended_ration': fields.integer('Recommended ration (gr)')
    }
    

product_product()

class product_template(osv.osv):
    _inherit = 'product.template'
    _columns = {
        'uos_coeff': fields.float('UOM -> UOS Coeff', digits=(16,8),
            help='Coefficient to convert UOM to UOS\n'
            ' uos = uom * coeff'),
    }
product_template()
