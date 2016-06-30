# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):
    _inherit = "sale.report"
#    _columns = {
#
#        'shipped_qty_1': fields.integer('Shipped', readonly=True),
#    }
#
#
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report')
        sale_obj=self.pool.get('sale.order')
        sale_line_obj=self.pool.get('sale.order.line')
        sale_ids=sale_obj.search(cr,1,[])
#        for sale_data in sale_obj.browse(cr,1,sale_ids):
#            for sale_line_data in sale_data.order_line:
#                if sale_line_data.id != '' and sale_line_data.product_id != '' and sale_line_data.product_uom_qty != '':
        cr.execute("""
            create or replace view sale_report as (
                select
                    min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0) as price_total,
                    count(*) as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    to_char(s.date_order, 'YYYY') as year,
                    to_char(s.date_order, 'MM') as month,
                    to_char(s.date_order, 'YYYY-MM-DD') as day,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.shop_id as shop_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.state,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    1 as  shipped_qty_1
                from
                    sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                where
                    l.id is not null and l.product_uom_qty <> 0.0 and
                    u.factor <> 0.0 and u2.factor <> 0.0
                group by
                    l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.shop_id,
                    s.company_id,
                    s.state,
                    s.pricelist_id,
                    s.project_id
            )
        """)
sale_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

#class report_stock_inventory(osv.osv):
#    _inherit = "report.stock.inventory"
#
#    def init(self, cr):
#        print"inventaryyyyyy"
#        tools.drop_view_if_exists(cr, 'report_stock_inventory')
#        cr.execute("""
#    CREATE OR REPLACE view report_stock_inventory AS (
#    (SELECT
#        -m.id as id, m.date as date,
#        to_char(m.date, 'YYYY') as year,
#        to_char(m.date, 'MM') as month,
#        m.partner_id as partner_id, m.location_dest_id as location_id,
#        m.product_id as product_id, pt.categ_id as product_categ_id, l.usage as location_type, l.scrap_location as scrap_location,
#        m.company_id,
#        m.state as state, m.prodlot_id as prodlot_id,
#        coalesce(sum(m.consignment_price * m.rem_product_qty * pu.factor / pu2.factor)::decimal, 0.0) as value,
#        coalesce(sum(m.rem_product_qty * pu.factor / pu2.factor)::decimal, 0.0) as product_qty
#    FROM
#        stock_move m
#            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
#            LEFT JOIN product_product pp ON (m.product_id=pp.id)
#                LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
#                LEFT JOIN product_uom pu ON (pt.uom_id=pu.id)
#                LEFT JOIN product_uom pu2 ON (m.product_uom=pu2.id)
#            LEFT JOIN product_uom u ON (m.product_uom=u.id)
#            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)
#            WHERE m.state = 'done' and p.type='internal' and m.rem_product_qty>0
#    GROUP BY
#        m.id, m.product_id, m.product_uom, pt.categ_id, m.partner_id, m.location_id, m.location_dest_id,
#        m.prodlot_id, m.date, m.state, l.usage, l.scrap_location, m.company_id, pt.uom_id, to_char(m.date, 'YYYY'), to_char(m.date, 'MM')
#
#)
#);
#        """)
#report_stock_inventory()
