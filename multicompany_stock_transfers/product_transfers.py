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
import netsvc
from tools.translate import _
class stock_invoice_onshipping(osv.osv_memory):
    _inherit = 'stock.invoice.onshipping'
    def _get_journal_id(self, cr, uid, context=None):
        print "GET JOURNAL"
        if context is None:
            context = {}

        model = context.get('active_model')
        print model 
        if not model or 'stock.picking' not in model:
            return []
        
        model_pool = self.pool.get(model)
        journal_obj = self.pool.get('account.journal')
        res_ids = context and context.get('active_ids', [])
        vals = []
        browse_picking = model_pool.browse(cr, uid, res_ids, context=context)
        print browse_picking
        for pick in browse_picking:
            if not pick.move_lines:
                continue
            
            src_usage = pick.move_lines[0].location_id.usage
            dest_usage = pick.move_lines[0].location_dest_id.usage
            type = pick.type
            if type == 'out' and dest_usage == 'supplier':
                journal_type = 'purchase_refund'
            elif type == 'out' and dest_usage == 'customer':
                journal_type = 'sale'
            elif type == 'in' and src_usage == 'supplier':
                journal_type = 'purchase'
            elif type == 'in' and src_usage == 'customer':
                journal_type = 'sale_refund'
            elif type == 'in' and src_usage == 'transit':
                journal_type = 'purchase'
            else:
                journal_type = 'sale'
            print type
            print dest_usage
            print src_usage
            print journal_type
            value = journal_obj.search(cr, uid, [('type', '=',journal_type )])
            for jr_type in journal_obj.browse(cr, uid, value, context=context):
                t1 = jr_type.id,jr_type.name
                if t1 not in vals:
                    vals.append(t1)
        return vals
    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal',required=True),
    }

stock_invoice_onshipping()
class wzd_transfer_product_rel(osv.osv):
    _name = 'wzd.transfers.product.rel'
    _description = "one2many betweetn product.product and product.transfer"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'product_uom_qty': fields.float('Quantity (UoM)', digits_compute= dp.get_precision('Product UoS'), required=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
        'product_uos_qty': fields.float('Quantity (UoS)' ,digits_compute= dp.get_precision('Product UoS')),
        'product_uos': fields.many2one('product.uom', 'Product UoS'),
        'product_tranfer_id': fields.many2one('product.transfers', 'Transfer ')
    }
    def product_id_change(self, cr, uid, ids, product, qty=0, uom=False, qty_uos=0, uos=False, context=None):
        context = context or {}
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        res = {}
        if not product:
            return {'value': {'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}

        result = res.get('value', {})
        warning_msgs = res.get('warning') and res['warning']['message'] or ''
        product_obj = product_obj.browse(cr, uid, product, context=context)

        uom2 = False
        if uom:
           
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}

        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff

        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty

        return {'value': result, 'domain': domain, 'warning': warning}
    def product_uos_change(self, cr, uid, ids, product, qty=0,
            uom=False, qty_uos=0, uos=False):
        res = {}
        if product:
            product_obj = self.pool.get('product.product').browse(cr, uid, product)
            if uos:
                if self.pool.get('product.uom').browse(cr,uid, uos).category_id.id == product_obj.uos_id.category_id.id:
                    if qty_uos:
                        qty_uom = qty_uos / product_obj.uos_coeff
                        uom = product_obj.uom_id.id


                        res = self.product_id_change(cr, uid, ids, product,
                            qty=qty_uom, uom=False, qty_uos=qty_uos, uos=uos)
                        if 'product_uom' in res['value']:
                            del res['value']['product_uom']
        return res

wzd_transfer_product_rel()


class product_transfer(osv.osv):
    _name = 'product.transfers'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'product_ids': fields.one2many('wzd.transfers.product.rel', 'product_tranfer_id','Products to tranfer', required=True),
        'orig_location_id': fields.many2one('stock.location', 'Source location', required=True),
        'dest_location_id': fields.many2one('stock.location', 'Dest. location', required=True),
        'transfer_location_id': fields.many2one('stock.location', 'Tranfer location', required=True),
        'journal_id': fields.many2one('stock.journal', 'Journal', required=True),
        'bill_output': fields.boolean('Bill output'),
        'bill_entry': fields.boolean('Bill entry'),
        'automatic_execution': fields.boolean('Automatic execution'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'date_planned': fields.datetime('Date Planned'),
        'state': fields.selection([
            ('draft','Draft'),
            ('transferred', 'Transferred')], 'State', readonly=True)
    }

    _defaults = {
        'transfer_location_id': lambda self, cr, uid, c: self.pool.get('stock.location').browse(cr, uid, (self.pool.get('stock.location').search(cr, uid, [('usage','=','transit')])[0]), context=c).id,
        'journal_id': lambda self, cr, uid, c: self.pool.get('stock.journal').browse(cr, uid, (self.pool.get('stock.journal').search(cr, uid, [('name','=','TRASPASOS')])[0]),context=c).id,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.transfer', context=c),
        'date_planned': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft'
    }
    def execute_transfer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        picking_obj=self.pool.get('stock.picking')
        wf_service = netsvc.LocalService("workflow")
        proc_obj = self.pool.get('procurement.order')
               
        for line in self.browse(cr, uid, ids, context=context):
            for product in line.product_ids:
                
                first = 0
                  
                transfer1 = "Entrada en " + line.dest_location_id.company_id.name
                transfer2 = "Salida de " + line.orig_location_id.company_id.name
                picking_type = ''
                notep = ''
                notem = ''
                noteproc = ''
                bill = ''
                address = False

                while first < 2:
                    if first == 0:
                        origin = (line.name) + ':' + transfer1
                        company = line.dest_location_id.company_id.id
                        addr = self.pool.get('res.partner').address_get(cr, uid, [line.orig_location_id.company_id.partner_id.id], ['delivery', 'invoice', 'contact', 'default', 'other'])
                        if addr['invoice']: address = addr['invoice']
                        elif addr['default']: address = addr['default']
                        elif addr['delivery']: address = addr['delivery']
                        elif addr['contact']: address = addr['contact']
                        elif addr['other']:  address = addr['other']
                        picking_type = 'in'
                        notep = _('Picking for pulled procurement coming from original location %s, pull rule %s, via original Procurement %s') % (line.orig_location_id.name, transfer1, line.name),
                        notem = _('Move for pulled procurement coming from original location %s, pull rule %s, via original Procurement %s') % (line.orig_location_id.name, transfer1, line.name),
                        noteproc = _('Pulled procurement coming from original location %s, pull rule %s, via original Procurement %s') % (line.orig_location_id.name, transfer1, line.name),
                        if line.bill_entry:
                            bill = '2binvoiced'
                        else:
                            bill = 'none'
                        location_orig = line.transfer_location_id.id
                        location_dest = line.dest_location_id.id
                    elif first == 1:
                        origin = (line.name) + ':' + transfer2
                        company = line.orig_location_id.company_id.id
                        addr = self.pool.get('res.partner').address_get(cr, uid, [line.dest_location_id.company_id.partner_id.id], ['delivery', 'invoice', 'contact', 'default', 'other'])
                        if addr['invoice']: address = addr['invoice']
                        elif addr['default']: address = addr['default']
                        elif addr['delivery']: address = addr['delivery']
                        elif addr['contact']: address = addr['contact']
                        elif addr['other']:  address = addr['other']
                        picking_type = 'out'
                        notep = _('Picking for pulled procurement coming from original location %s, pull rule %s, via original Procurement %s') % (line.orig_location_id.name, transfer2, line.name),
                        notem = _('Move for pulled procurement coming from original location %s, pull rule %s, via original Procurement %s') % (line.orig_location_id.name, transfer2, line.name),
                        noteproc = _('Pulled procurement coming from original location %s, pull rule %s, via original Procurement %s') % (line.orig_location_id.name, transfer2, line.name),
                        if line.bill_output:
                            bill = '2binvoiced'
                        else:
                            bill = 'none'
                        location_orig = line.orig_location_id.id
                        location_dest = line.transfer_location_id.id

                    picking_id = picking_obj.create(cr, uid, {
                        'origin': origin,
                        'company_id': company or False,
                        'type': picking_type,
                        'stock_journal_id': line.journal_id and line.journal_id.id or False,
                        'move_type': 'one',
                        'address_id': False,
                        'note': notep,
                        'invoice_state': bill,
                        'address_id': address
                    })

                    move_id = move_obj.create(cr, uid, {
                        'name': origin,
                        'picking_id': picking_id,
                        'company_id':  company or False,
                        'product_id': product.product_id.id,
                        'date': line.date_planned,
                        'product_qty': product.product_uom_qty,
                        'product_uom': product.product_uom.id,
                        'product_uos_qty': (product.product_uos and product.product_uos_qty)\
                                or product.product_uom_qty,
                        'product_uos': (product.product_uos and product.product_uos.id)\
                                or product.product_uom.id,
                        'address_id': False,
                        'location_id': location_orig,
                        'location_dest_id': location_dest,
                            
                        'tracking_id': False,
                        'cancel_cascade': False,
                        'state': 'confirmed',
                        'note': notem
                    })
                       

                    proc_id = proc_obj.create(cr, uid, {
                        'name': line.name,
                        'origin': origin,
                        'note': noteproc,
                        'company_id':  company or False,
                        'date_planned': line.date_planned,
                        'product_id': product.product_id.id,
                        'product_qty': product.product_uom_qty,
                        'product_uom': product.product_uom.id,
                        'product_uos_qty': (product.product_uos and product.product_uos_qty)\
                                or product.product_uom_qty,
                        'product_uos': (product.product_uos and product.product_uos.id)\
                                or product.product_uom.id,
                        'location_id': location_orig,
                        'procure_method': 'make_to_stock',
                        'move_id': move_id,
                    })

                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                   
                    wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
                      
                    proc_obj.write(cr, uid, [proc_id], {'state':'running', 'message':_('Pulled from another location via procurement %d')%proc_id})

                    # trigger direct processing (the new procurement shares the same planned date as the original one, which is already being processed)
                    wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_check', cr)
                    first += 1
                    if line.automatic_execution:
                        picking_obj.force_assign(cr, uid, [picking_id])
                        wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_done', cr)
                    
        self.write(cr, uid, ids, {'state': 'transferred'})

        return True

product_transfer()
