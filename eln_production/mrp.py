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
import time
from datetime import datetime, timedelta
import tools
from tools.translate import _

class change_production_qty(osv.osv_memory):
    _inherit = 'change.production.qty'

    def change_prod_qty(self, cr, uid, ids, context=None):
        res = super(change_production_qty, self).change_prod_qty(cr, uid, ids, context=context)
        prod_obj = self.pool.get('mrp.production')
        record_id = context and context.get('active_id',False)
        assert record_id, _('Active Id is not found')
        for wiz_qty in self.browse(cr, uid, ids, context=context):
            prod = prod_obj.browse(cr, uid, record_id, context=context)
            if prod.product_uom and prod.product_uos and prod.product_uos.id == prod.product_id.uos_id.id:
                prod_obj.write(cr, uid, prod.id, {'product_uos_qty': wiz_qty.product_qty * (prod.product_id.uos_coeff or 1.0)})

        return res

change_production_qty()

class mrp_workcenter(osv.osv):
    _inherit = 'mrp.workcenter'
    _columns = {
        'operators_ids': fields.many2many('hr.employee', 'hr_employee_mrp_workcenter_rel', 'workcenter_id', 'employee_id', string='Operators'),
    }
mrp_workcenter()
def rounding(f, r):
    import math
    if not r:
        return f
    return math.ceil(f / r) * r
class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'
    _columns = {
        'alternatives_routing_ids': fields.many2many('mrp.routing', 'mrp_bom_routing_rel', 'bom_id', 'routing_id', string="Alternatives routings")
    }
    def _check_product(self, cr, uid, ids, context=None):
        return True
    _constraints = [
        (_check_product, 'BoM line product should not be same as BoM product.', ['product_id']),
    ]
    
    def _bom_explode(self, cr, uid, bom, factor, properties=[], addthis=False, level=0, routing_id=False):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product.
        @param factor: Factor of product UoM.
        @param properties: A List of properties Ids.
        @param addthis: If BoM found then True else False.
        @param level: Depth level to find BoM lines starts from 10.
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        def _get_vals(wc_use, operators, operators_n, factor, bom, wc, routing):
                qty_per_cycle = self.pool.get('product.uom')._compute_qty(cr, uid, wc_use.uom_id.id, wc_use.qty_per_cycle, bom.product_uom.id)
                oper = []
                for op in range(0, (operators_n)):
                    oper.append(operators[op])
                return{
                    'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
                    'routing_id': routing.id,
                    'workcenter_id': wc.id,
                    'sequence': level+(wc_use.sequence or 0),
                    'operators_ids': [(6,0,oper)],
                    'cycle': wc_use.cycle_nbr * (factor * bom.product_qty),
                    'time_start': wc_use.time_start,
                    'time_stop': wc_use.time_stop,
                    'hour': float((wc_use.operators_number * ((factor * bom.product_qty)/(qty_per_cycle or 1.0)))/(operators_n or 1.0)),
                    'real_time': float((wc_use.operators_number * ((factor * bom.product_qty)/(qty_per_cycle or 1.0)))/(operators_n or 1.0))

                        }
        routing_obj = self.pool.get('mrp.routing')
        factor = factor / (bom.product_efficiency or 1.0)
        factor = rounding(factor, bom.product_rounding)
        if factor < bom.product_rounding:
            factor = bom.product_rounding
        result = []
        result2 = []
        phantom = False
        if bom.type == 'phantom' and not bom.bom_lines:
            newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)

            if newbom:
                res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
                phantom = True
            else:
                phantom = False
        if not phantom:
            if addthis and not bom.bom_lines:
                result.append(
                {
                    'name': bom.product_id.name,
                    'product_id': bom.product_id.id,
                    'product_qty': bom.product_qty * factor,
                    'product_uom': bom.product_uom.id,
                    'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
                    'product_uos': bom.product_uos and bom.product_uos.id or False,
                })
            routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
            if routing:
                for wc_use in routing.workcenter_lines:
                    wc = wc_use.workcenter_id
                    operators = []
                    if wc_use.operators_ids:
                        for oper in wc_use.operators_ids:
                            operators.append(oper.id)
                    result2.append(_get_vals(wc_use, operators, wc_use.operators_number, factor, bom, wc, routing))

            for bom2 in bom.bom_lines:
                res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
                result = result + res[0]
                result2 = result2 + res[1]
        return result, result2
mrp_bom()

class mrp_routing_workcenter(osv.osv):
    _inherit = 'mrp.routing.workcenter'
    _columns = {
        'operators_ids': fields.many2many('hr.employee', 'hr_employee_mrp_routing_workcenter_rel', 'routing_workcenter_id', 'employee_id', string='Operators'),
        'capacity_per_cycle': fields.float('Capacity per Cycle', help="Number of operations this Work Center can do in parallel. If this Work Center represents a team of 5 workers, the capacity per cycle is 5."),
        'time_start': fields.float('Time before prod.', help="Time in hours for the setup."),
        'time_stop': fields.float('Time after prod.', help="Time in hours for the cleaning."),
        'qty_per_cycle': fields.float('Qty x cycle'),
        'uom_id': fields.many2one('product.uom', 'UoM'),
        'operators_number': fields.integer('Operators Nº')
    }
    def onchange_workcenter_id(self, cr, uid, ids, workcenter_id, context=None):
        """ Changes Operators if workcenter changes.
        @param workcenter_id: Changed workcenter_id
        @return:  Dictionary of changed values
        """
        if workcenter_id:
            operators = []
            workcenter = self.pool.get('mrp.workcenter').browse(cr, uid, workcenter_id, context=context)
            if workcenter.operators_ids:
                for oper in workcenter.operators_ids:
                    operators.append(oper.id)
                return {'value': {'operators_ids': operators}}
        return {}
mrp_routing_workcenter()

class production_stops(osv.osv):
    _name = 'production.stops'
    _columns = {
        'name': fields.char('Name',size=32, required=True),
        'reason': fields.char('Reason', size=255, required=True),
        'time': fields.float('Time', required=True),
        'production_workcenter_line_id': fields.many2one('mrp.production.workcenter.line', 'Production workcenter line')
    }
production_stops()

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'
    def _get_color_stock(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        mvs = []
        moves = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.product:
                moves = self.pool.get('stock.move').search(cr, uid, [('product_id','=',line.product.id),('picking_id.type','=','out'),('state','not in',('done','cancel'))])
                if moves:
                    for move in moves:
                        obj = self.pool.get('stock.move').browse(cr,uid, move)
                        if obj.date_expected[:10] == time.strftime('%Y-%m-%d'):
                            mvs.append(obj.id)
                if mvs and line.stock < 0:
                    res[line.id] = 2
                elif not mvs and line.stock < 0:
                    res[line.id] = 3
                elif line.stock > 0:
                    res[line.id] = 4
        return res
    def _get_date_stop(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.date_expected and line.hour:
                start = datetime.strptime(line.date_expected, "%Y-%m-%d %H:%M:%S")
                stop = start + timedelta(hours=line.hour)
                res[line.id] = stop.strftime("%Y-%m-%d %H:%M:%S")

        return res
    _columns = {
        'operators_ids': fields.many2many('hr.employee', 'hr_employee_mrp_prod_workc_line_rel', 'workcenter_line_id', 'employee_id', string='Operators'),
        'production_stops_ids': fields.one2many('production.stops', 'production_workcenter_line_id', 'Production Stops'),
        'time_start': fields.float('Time before prod.', help="Time in hours for the setup."),
        'time_stop': fields.float('Time after prod.', help="Time in hours for the cleaning."),
        'gasoleo_start': fields.float('Gasoleo start'),
        'gasoleo_stop': fields.float('Gasoleo stop'),
        'color': fields.integer('Color Index'),
        'move_id': fields.related('production_id', 'move_prod_id', type='many2one',relation='stock.move', string='Move', readonly=True),
        'address': fields.related('move_id', 'address_id', type='many2one', string='address', relation='res.partner.address', readonly=True),
        'partnerid': fields.related('address', 'partner_id', type='many2one', string='Parnter', relation='res.partner',readonly=True),
        'partner_name': fields.related('partnerid', 'name', type='char', string='Parntername', readonly=True),
        'date_expected': fields.related('move_id', 'date_expected', type='datetime', string='date', readonly=True),
        'date_stop': fields.function(_get_date_stop, type="datetime", string="Date stop", readonly=True),
        'stock': fields.related('product', 'real_virtual_available', type='float', string='Stock', readonly=True),
        'color_stock': fields.function(_get_color_stock, type="integer", string="Color stock", readonly=True),
        'routing_id': fields.many2one('mrp.routing', 'Routing', readonly=True),
        'real_time': fields.float('Real time')

    }

mrp_production_workcenter_line()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def _get_ids_str(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        res = {}
        
        for cur_obj in self.browse(cr, uid, ids):
            stream = []
            res[cur_obj.id] = "[]"
            if cur_obj.bom_id:
                bom_point = self.pool.get('mrp.bom').browse(cr, uid, cur_obj.bom_id.id, context=context)
                if bom_point.routing_id or bom_point.alternatives_routing_ids:
                    if bom_point.routing_id:
                        stream.append(str(bom_point.routing_id.id))
                    if bom_point.alternatives_routing_ids:
                        for line in bom_point.alternatives_routing_ids:
                            stream.append(str(line.id))
                    res[cur_obj.id] = "[" + u", ".join(stream) + "]"
        
        return res

    def _get_operator_ids_str(self, cr, uid, ids, field_name, args, context=None):
        if context is None:
            context = {}
        res = {}

        for cur_obj in self.browse(cr, uid, ids):
            stream = []
            res[cur_obj.id] = "[]"
            if cur_obj.routing_id:
                if cur_obj.routing_id.workcenter_lines:
                    for line in cur_obj.routing_id.workcenter_lines:
                        if line.operators_ids:
                            for op in line.operators_ids:
                                stream.append(str(op.id))

                    res[cur_obj.id] = "[" + u", ".join(stream) + "]"

        return res

    _columns = {
        'ids_str2': fields.function(_get_ids_str, method=True, string='ids_str', type='char', size=255),
        'operator_ids_str': fields.function(_get_operator_ids_str, method=True, string="Operators_ids_str", type="char", size="255"),
        'routing_id': fields.many2one('mrp.routing', string='Routing', on_delete='set null', readonly=True, states={'draft':[('readonly',False)],'confirmed':[('readonly',False)],'ready':[('readonly',False)]}, help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production plannification."),
        'date_end_planned': fields.datetime('Date end Planned'),

    }
    def _costs_generate(self, cr, uid, production):
        """ Calculates total costs at the end of the production.
        @param production: Id of production order.
        @return: Calculated amount.
        """
        amount = 0.0
        analytic_line_obj = self.pool.get('account.analytic.line')
        for wc_line in production.workcenter_lines:
            wc = wc_line.workcenter_id
            if wc.costs_journal_id and wc.costs_general_account_id:
                # Cost per hour
                value = wc_line.hour * wc.costs_hour
                account = wc.costs_hour_account_id.id
                if value and account:
                    amount += value
                    analytic_line_obj.create(cr, uid, {
                        'name': wc_line.name + ' (H)',
                        'amount': value,
                        'account_id': account,
                        'general_account_id': wc.costs_general_account_id.id,
                        'journal_id': wc.costs_journal_id.id,
                        'ref': wc.code,
                        'product_id': wc.product_id.id,
                        'unit_amount': wc_line.hour,
                        'product_uom_id': wc.product_id and wc.product_id.uom_id.id or False
                    } )

        return amount

    

    def product_qty_change(self, cr, uid, ids, product_id, product_qty, product_uom, product_uos, context=None):


        result = {'value': {}}
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
            if product_uos:
                if self.pool.get('product.uom').browse(cr, uid, product_uos).category_id.id == product_obj.uos_id.category_id.id:
                    if product_qty:
                        if product_obj.uos_coeff:
                            qty_uos = float(product_qty * product_obj.uos_coeff)
                            result['value']['product_uos_qty'] = qty_uos
        return result

    def product_uos_qty_change(self, cr, uid, ids, product_id, product_uos_qty, product_uos, product_uom, context=None):

        result = {'value': {}}
        if product_id:
            product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
            if product_uom:
                if self.pool.get('product.uom').browse(cr, uid, product_uom).category_id.id == product_obj.uom_id.category_id.id:
                    if product_uos_qty:
                        if product_obj.uos_coeff:
                            qty_uom = float(product_uos_qty / product_obj.uos_coeff)
                            result['value']['product_qty'] = qty_uom
        return result

    def bom_id_change(self, cr, uid, ids, bom_id, context=None):
        """ Finds routing for changed BoM.
        @param product: Id of product.
        @return: Dictionary of values.
        """
       
        result = super(mrp_production,self).bom_id_change(cr, uid, ids, bom_id, context=context)
        if not bom_id:
            return {'value': {
                'ids_str': "[]"
            }}
        bom_point = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context=context)
        stream = []
        result['value']['ids_str'] = "[]"
        if bom_point.routing_id:
            stream.append(str(bom_point.routing_id.id))
        if bom_point.alternatives_routing_ids:
            for line in bom_point.alternatives_routing_ids:
                stream.append(str(line.id))
        if stream:
            result['value']['ids_str2'] =  "[" + u", ".join(stream) + "]"

        return result

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        """ Finds UoM of changed product.
        @param product_id: Id of changed product.
        @return: Dictionary of values.
        """
        
        result = super(mrp_production,self).product_id_change(cr, uid, ids, product_id, context=context)
        if not product_id:
            return {'value': {
                'ids_str': "[]",
                'product_uos': False
            }}
        product = self.pool.get('product.product'). browse(cr, uid, product_id, context=context)
        result['value']['product_uos'] = product.uos_id and product.uos_id.id or False

        if result['value'].get('bom_id', False):
            stream = []
            result['value']['ids_str2'] = "[]"

            bom_point = self.pool.get('mrp.bom').browse(cr, uid, result['value']['bom_id'])
            if bom_point.routing_id:
                stream.append(str(bom_point.routing_id.id))
            if bom_point.alternatives_routing_ids:
                for line in bom_point.alternatives_routing_ids:
                    stream.append(str(line.id))
            if stream:
                result['value']['ids_str2'] =  "[" + u", ".join(stream) + "]"

        return result
    
    def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
        production = self.browse(cr, uid, production_id, context=context)

        raw_product = [move for move in production.move_lines]

        if raw_product:
            for consume_line in raw_product:
                consume_line.action_consume(consume_line.product_qty, consume_line.location_id.id, context=context)
       
        return super(mrp_production, self).action_produce(cr, uid, production_id, production_qty, production_mode, context=context)

    def action_recalculate_time(self, cr, uid, ids, properties=[],context=None):

        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            time = 0.00

            if production.workcenter_lines:
                for line in production.workcenter_lines:
                    if line.operators_ids:
                        real_operators = len([x.id for x in line.operators_ids])
                        real_qty = line.qty
                        wc = self.pool.get('mrp.routing.workcenter').search(cr, uid, [('routing_id','=',production.routing_id.id), ('workcenter_id','=',line.workcenter_id.id),('sequence','=',line.sequence)])
                        
                        if wc:
                            wco = self.pool.get('mrp.routing.workcenter').browse(cr, uid, wc[0])
                            obj_operators = wco.operators_number
                            obj_qty = wco.qty_per_cycle
                            time = float((obj_operators * (real_qty/obj_qty or 1.0))/(real_operators or 1.0))
                            workcenter_line_obj.write(cr, uid, line.id, {'real_time': time})
                        else:
                            raise osv.except_osv(_('Error!'),  _('Can not recalculate time because not exists objectives datas in the lines of the routing'))
                        

        return True

mrp_production()


