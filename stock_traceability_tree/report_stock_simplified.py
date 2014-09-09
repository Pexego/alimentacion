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

"""Creates function for show the traceability simplified"""

from openerp import models

class report_stock_simplified(models.AbstractModel):
    """Creates function for show the traceability simplified"""
    _name = "report.stock.simplified"
    _description = "Creates function for show the traceability simplified"

    def init(self, cr):
        """creates function when install"""
        #check if exists the language plpgsql in bbdd, if not, is created for can create functions in this language
        cr.execute("select * from pg_language where lanname = 'plpgsql'")
        if not cr.rowcount:
            cr.execute("create language 'plpgsql'")

        #creates a function. From int parameter return the stock_move top parents for this paramenter
        cr.execute("""create or replace function stock_move_parents (integer)
            returns setof stock_move as '
            declare results record;
                child record;
                temp record;
                temp2 record;
                BEGIN
                  select into results stock_move.* from stock_move inner join stock_move_trace_rel on stock_move.id = stock_move_trace_rel.parent_id where stock_move_trace_rel.child_id = $1;
                  IF found then
                    FOR child IN select stock_move.id from stock_move inner join stock_move_trace_rel on stock_move.id = stock_move_trace_rel.parent_id where stock_move_trace_rel.child_id = $1
                    LOOP
                        FOR temp IN select distinct * from stock_move_parents(child.id)
                        LOOP
                      select into temp2 stock_move.* from stock_move inner join stock_move_trace_rel on stock_move.id = stock_move_trace_rel.parent_id where stock_move_trace_rel.child_id = temp.id;
                      IF not found then
                        return next temp;
                      END IF;
                      CONTINUE;
                        END LOOP;
                    END LOOP;
                  ELSE
                    select into results * from stock_move where id = $1;
                    return next results;
                  END IF;
                END; '
                language 'plpgsql';""")

        #creates a function. From int parameter return the stock_move last childs for this paramenter
        cr.execute("""create or replace function stock_move_childs (integer)
            returns setof stock_move as
            $BODY$
            declare results record;
                    parent record;
                    temp record;
                    temp2 record;
                    temp3 record;
            BEGIN
              select into results stock_move.* from stock_move inner join stock_move_trace_rel on stock_move.id = stock_move_trace_rel.child_id
              where stock_move_trace_rel.parent_id = $1;
              IF found then
                FOR parent IN select stock_move.id from stock_move inner join stock_move_trace_rel on stock_move.id = stock_move_trace_rel.child_id where stock_move_trace_rel.parent_id = $1
                LOOP
            select into temp3 stock_move.* from stock_move inner join stock_location on stock_move.location_dest_id = stock_location.id where stock_move.id = parent.id and stock_location.usage = 'customer';
            If found then
            return next temp3;
            END IF;
                    FOR temp IN select distinct * from stock_move_childs(parent.id)
                    LOOP
            select into temp2 stock_move.* from stock_move inner join stock_move_trace_rel on stock_move.id = stock_move_trace_rel.child_id where stock_move_trace_rel.parent_id = temp.id;
            IF not found then
                return next temp;
            END IF;
                  CONTINUE;
                    END LOOP;
                END LOOP;
              ELSE
                select into results * from stock_move where id = $1;
                return next results;
              END IF;
            END; $BODY$
            language 'plpgsql';""")

