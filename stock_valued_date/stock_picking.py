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
import netsvc
import time

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    _columns = {
        'real_date':fields.datetime('Real Date', help="Real Date of Completion"),
    }

    _defaults = {
        'real_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
mrp_production()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    _columns = {
        'real_date':fields.datetime('Real Date', help="Real Date of Completion"),
    }

    _defaults = {
        'real_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        
        if isinstance(ids,(int,long)):
            ids = [ids]
        res = super(stock_picking, self).write(cr, uid, ids, vals, context=context)
        if vals.get('real_date', False):
            for picking in self.browse(cr, uid, ids):
                self.pool.get('stock.move').write(cr, uid, [x.id for x in picking.move_lines], {'date': vals['real_date']})
                     
        return res
    
    def _calculate_pmp(self, cr, uid, old_move, product_currency, stock_cur, pmp_cur, stock_new, pmp_new, product_uom,context=None):
        
        move = self.pool.get('stock.move').browse(cr, uid, old_move[0])
        product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context={'to_date': move.date})
        move_currency_id = move.company_id.currency_id.id

        qty = self.pool.get('product.uom')._compute_qty(cr, uid, product_uom, stock_new, product.uom_id.id)
        if qty >= 0:
            new_price = self.pool.get('res.currency').compute(cr, uid, product_currency,
                    move_currency_id, pmp_new)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, product_uom, new_price,
                    product.uom_id.id)
            if stock_cur <= 0:
                pmp = new_price
            else:
                
                pmp = (( stock_cur* pmp_cur)+(stock_new * new_price))/(stock_cur + stock_new)

        return pmp

    def _create_line_pmp(self, cr, uid, ids, product_currency, product_price, product_qty, product_uom,context=None):

        if context is None:
            context = {}
        
        register_obj = self.pool.get('weighted.average.price')
        move_obj = self.pool.get('stock.move').browse(cr, uid, ids[0], context=context)
        product_id = move_obj.product_id.id
        date = move_obj.picking_id.real_date
        company_id = move_obj.company_id.id
        ids_registers = register_obj.search(cr, uid, [('product_id', '=', product_id),('company_id','=', company_id),('date','<',date)],order='date desc')
        new_register = False
        
        ids_registers_pos = register_obj.search(cr, uid, [('product_id', '=', product_id),('company_id','=', company_id),('date','>',date)],order='date asc')
        if ids_registers:
            obj = register_obj.browse(cr, uid, ids_registers[0], context=context)
            stock_cur = obj.stock_qty
            pmp_cur = obj.pmp
        else:
            context.update({'to_date': move_obj.picking_id.real_date})
            product = self.pool.get('product.product').browse(cr, uid, move_obj.product_id.id, context=context)
            stock_cur = product.qty_available
            if ids_registers_pos:
                obj_pos = register_obj.browse(cr, uid, ids_registers_pos[0],context=context)
                if obj_pos.pmp_old:
                    pmp_cur = obj_pos.pmp_old
                    new_register = True
            else:
                pmp_cur = product.standard_price
                new_register = True

        
        pmp = self._calculate_pmp(cr, uid, [move_obj.id], product_currency,stock_cur, pmp_cur, product_qty, product_price,product_uom,context=context)
        id_new = register_obj.create(cr, uid, {'product_id': product_id,
                                                                'date': date,
                                                                'pmp': pmp,
                                                                'move_id': move_obj.id,
                                                                'company_id': move_obj.company_id.id,

                                                                })
        if new_register:
            register_obj.write(cr, uid, id_new, {'pmp_old': pmp_cur})
            new_register = False

        
        if ids_registers_pos:
            obj_cur = register_obj.browse(cr, uid, id_new,context=context)
            
            qty = obj_cur.move_id.product_qty
            for reg in ids_registers_pos:
                if obj_cur:
                    obj = register_obj.browse(cr, uid, reg, context=context)
                    pmp = self._calculate_pmp(cr, uid, [obj.move_id.id], obj.move_id.price_currency_id.id,obj_cur.stock_qty, obj_cur.pmp, obj.move_id.product_qty, obj.move_id.price_unit,obj.move_id.product_uom.id,context=context)
                    register_obj.write(cr, uid, reg, {'pmp':pmp})
                    obj_cur = False
                    new = reg
                else:
                    obj_cur = register_obj.browse(cr, uid, new,context=context)
                    obj = register_obj.browse(cr, uid, reg, context=context)
                    pmp = self._calculate_pmp(cr, uid, [obj.move_id.id], obj.move_id.price_currency_id.id, obj_cur.stock_qty, obj_cur.pmp, obj.move_id.product_qty, obj.move_id.price_unit,obj.move_id.product_uom.id,context=context)
                    register_obj.write(cr, uid, reg, {'pmp':pmp})
                    obj_cur = False
                    new = reg
            # CHECK If final stock qty in weighted.average.price is equal toqty_avaible at the product
            # If no we'll force it
                 
            last_reg = register_obj.browse (cr, uid, reg)
            if (last_reg.stock_qty != last_reg.product_id.qty_available):
                register_obj.write(cr, uid, reg, {'stock_qty':last_reg.product_id.qty_available})
                
        return True

    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, address_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom',False)
                product_price = partial_data.get('product_price',0.0)
                product_currency = partial_data.get('product_currency',False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                    ###############################################################
                    pmp = self._create_line_pmp(cr, uid, [move.id],product_currency, product_price, product_qty, product_uom, context=context)
                    ###############################################################
                    product = product_obj.browse(cr, uid, move.product_id.id)
#                    move_currency_id = move.company_id.currency_id.id
#                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
#
#                    if product.id in product_avail:
#                        product_avail[product.id] += qty
#                    else:
#                        product_avail[product.id] = product.qty_available
#
                    if qty > 0:
#                        new_price = currency_obj.compute(cr, uid, product_currency,
#                                move_currency_id, product_price)
#                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
#                                product.uom_id.id)
#                        if product.qty_available <= 0:
#                            new_std_price = new_price
#                        else:
#                            # Get the standard price
#                            amount_unit = product.price_get('standard_price', context=context)[product.id]
#                            new_std_price = ((amount_unit * product_avail[product.id])\
#                                + (new_price * qty))/(product_avail[product.id] + qty)
#                        # Write the field according to price type field
                        id_pmp = self.pool.get('weighted.average.price').search(cr, uid, [('product_id', '=', product.id),('company_id','=', move.company_id.id)],order='date desc')
                        obj = self.pool.get('weighted.average.price').browse(cr, uid, id_pmp[0])
                        
                        #TODO No creo que se deba reescribir el qty_available en ningún caso ya que es el que el sistema debe calcular
                        #product_obj.write(cr, uid, [product.id], {'standard_price': obj.pmp, 'qty_available': obj.stock_qty})
                        product_obj.write(cr, uid, [product.id], {'standard_price': obj.pmp})
                           
                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})


            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking:
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': sequence_obj.get(cr, uid, 'stock.picking.%s'%(pick.type)),
                                'move_lines' : [],
                                'state':'draft',
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty, #TODO: put correct uos_qty
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty' : move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_qty - partial_qty[move.id], #TODO: put correct uos_qty

                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': product_qty, #TODO: put correct uos_qty
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking])
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
            else:
                self.action_move(cr, uid, [pick.id])
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}

        return res

stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'

    _columns = {
        'inventory_ids':fields.many2many('stock.inventory', 'stock_inventory_move_rel','move_id', 'inventory_id', 'Inventories'),
        'production_ids': fields.many2many('mrp.production', 'mrp_production_move_ids', 'move_id', 'production_id', 'Consumed Products'),
    }
#~ 
    #~ 
    
    def recalculate_pmp (self, cr, uid, ids, new_price, uom, qty, context=None):
        if context is None:
            context = {}
        
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        
        move = move_obj.browse(cr, uid, ids[0], context=context)
        picking = picking_obj.browse (cr, uid, move.picking_id.id)
        product_id = move.product_id.id
        date = move.picking_id.real_date
        company_id = move.company_id.id
        register_obj  = self.pool.get('weighted.average.price')
        uom_obj = self.pool.get('product.uom')
        
        ids_registers = register_obj.search(cr, uid, [('product_id', '=', product_id),('company_id','=', company_id),('date','<',date)],order='date desc')
        id_register = register_obj.search(cr, uid, [('id', '=', move.id)])
        new_register = False
        ids_registers_pos = register_obj.search(cr, uid, [('product_id', '=', product_id),('company_id','=', company_id),('date','>',date)],order='date asc')
        
        if ids_registers:
            obj = register_obj.browse(cr, uid, ids_registers[0], context=context)
            stock_cur = obj.stock_qty
            pmp_cur = obj.pmp
        else:
            context.update({'to_date': move.picking_id.real_date})
            product = self.pool.get('product.product').browse(cr, uid, move.product_id.id, context=context)
            stock_cur = product.qty_available
            if ids_registers_pos:
                obj_pos = register_obj.browse(cr, uid, ids_registers_pos[0],context=context)
                if obj_pos.pmp_old:
                    pmp_cur = obj_pos.pmp_old
            else:
                pmp_cur = product.standard_price

        
        if id_register:
            obj = register_obj.browse(cr, uid, id_register[0], context=context)
            uom_qty = uom_obj._compute_qty(cr, uid, uom, qty, move.product_uom.id)
            pmp = picking._calculate_pmp(cr, uid, [move.id], move.currency.id, stock_cur, pmp_cur, uom_qty, new_price, move.product_uom.id ,context=context)
            register_obj.write(cr, uid, [move.id], {'pmp': pmp,})
        #=======================================================================
        # if new_register:
        #    self.pool.get('weighted.average.price').write(cr, uid, id_new, {'pmp_old': pmp_cur})
        #    new_register = False
        #=======================================================================

        
        if ids_registers_pos:
            obj_cur = register_obj.browse(cr, uid, id_register[0], context=context)
            
            qty = obj_cur.move_id.product_qty
            for reg in ids_registers_pos:
                if obj_cur:
                    obj = register_obj.browse(cr, uid, reg, context=context)
                    pmp = picking._calculate_pmp(cr, uid, [obj.move_id.id], obj.move_id.price_currency_id.id,obj_cur.stock_qty, obj_cur.pmp, obj.move_id.product_qty, obj.move_id.price_unit,obj.move_id.product_uom.id,context=context)
                    register_obj.write(cr, uid, reg, {'pmp':pmp})
                    obj_cur = False
                    new = reg
                else:
                    obj_cur = register_obj.browse(cr, uid, new,context=context)
                    obj = register_obj.browse(cr, uid, reg, context=context)
                    pmp = picking._calculate_pmp(cr, uid, [obj.move_id.id], obj.move_id.price_currency_id.id, obj_cur.stock_qty, obj_cur.pmp, obj.move_id.product_qty, obj.move_id.price_unit,obj.move_id.product_uom.id,context=context)
                    register_obj.write(cr, uid, reg, {'pmp':pmp})
                    obj_cur = False
                    new = reg
                    
        product_obj.write(cr, uid, product_id, {'standard_price': obj.pmp})
        return True
        
    
    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        partial_datas=''
        picking_ids = []
        move_ids = []
        partial_obj=self.pool.get('stock.partial.picking')
        wf_service = netsvc.LocalService("workflow")
        #partial_id=partial_obj.search(cr,uid,[])
#        if partial_id:
#            partial_datas = partial_obj.read(cr, uid, partial_id, context=context)[0]
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
     
            move_ids.append(move.id)
            date = time.strftime('%Y-%m-%d %H:%M:%S')
            if move.inventory_ids:
                for inventory in move.inventory_ids:
                    date = self.pool.get('stock.inventory').browse(cr, uid, inventory.id).date
            if move.production_id:
                date = self.pool.get('mrp.production').browse(cr, uid, move.production_id.id).real_date
            if move.production_ids:
                for production in move.production_ids:
                    date = self.pool.get('mrp.production').browse(cr, uid, production.id).real_date
            if move.picking_id:
                picking_ids.append(move.picking_id.id)
                date = self.pool.get('stock.picking').browse(cr, uid, move.picking_id.id).real_date
            if move.move_dest_id.id and (move.state != 'done'):
                self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                if move.move_dest_id.state in ('waiting', 'confirmed'):
                    if move.prodlot_id.id and move.product_id.id == move.move_dest_id.product_id.id:
                        self.write(cr, uid, [move.move_dest_id.id], {'prodlot_id':move.prodlot_id.id})
                    self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                    if move.move_dest_id.picking_id:
                        wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                    if move.move_dest_id.auto_validate:
                        self.action_done(cr, uid, [move.move_dest_id.id], context=context)
            
            self._create_product_valuation_moves(cr, uid, move, context=context)
#            prodlot_id = partial_datas and partial_datas.get('move%s_prodlot_id' % (move.id), False)
#            if prodlot_id:
#                self.write(cr, uid, [move.id], {'prodlot_id': prodlot_id}, context=context)
            if move.state not in ('confirmed','done','assigned'):
                self.action_confirm(cr, uid, [move.id], context=context)

            self.write(cr, uid, [move.id], {'state': 'done', 'date': date}, context=context)

        for id in move_ids:
             wf_service.trg_trigger(uid, 'stock.move', id, cr)
             
        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True
    #~ 
stock_move()
