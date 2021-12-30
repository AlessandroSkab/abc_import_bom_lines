# -*- coding: utf-8 -*-
from odoo import api, models, fields,_
from odoo.exceptions import UserError
import csv
import io
import base64
import tempfile
from io import StringIO



class EplanBomLine(models.TransientModel):
    _name = 'eplan.bom.line'
    _description = "Eplan BOM Line"

    csv_file = fields.Binary(string="Import csv")
    missing_product_ids = fields.One2many('eplan.missing.product', 'eplan_bom_id')
    is_product_missing = fields.Boolean(string="Product Missing?")
    bom_id = fields.Many2one('mrp.bom', string="BOM")

    def action_create_missing_product(self):
        for each in self.missing_product_ids:
            if not each.description or not each.type or not each.product_code or not each.categ_id:
                raise UserError(_('Enter missing product details.'))
            self.env['product.product'].create({
                'name': each.description,
                'type' : each.type,
                'default_code' : each.product_code,
                'categ_id' : each.categ_id.id,
                'sale_ok': each.can_be_sold,
            })
        self.is_product_missing = False
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Eplan'),
            'res_model': 'eplan.bom.line',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }

    def import_bom_line(self):
        if not self.csv_file:
            raise UserError(_('Please upload csv file.'))
        csv_data = base64.b64decode(self.csv_file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_reader = csv.reader(data_file, delimiter='/')
        file_reader.extend(csv_reader)
        missing_product_lst = []
        missing = []
        product_lst = []
        for each in file_reader:
            split_lst = each[0].split(';')
            product_id = self.env['product.product'].search([('default_code', '=', split_lst[0])], limit=1)
            product_lst.append((0,0, {
                'product_id': product_id.id,
                'product_qty' : int(split_lst[1])
            }))
            if not product_id and split_lst[0] not in missing:
                missing.append(split_lst[0])
                missing_product_lst.append((0, 0, {
                    'product_code' : split_lst[0]
                }))
        if missing_product_lst:
            self.missing_product_ids = missing_product_lst
            self.is_product_missing = True
            return {
                'type': 'ir.actions.act_window',
                'name': _('Import Eplan'),
                'res_model': 'eplan.bom.line',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Eplan'),
            'res_model': 'wiz.eplan.confirm',
            'view_mode': 'form',
            'target': 'new',
            'context' : {'bom_id' : self.bom_id.id, 'product_lst' : product_lst}
        }
        print ("\n\n split lt----",missing_product_lst)


class EplanMissingProduct(models.TransientModel):
    _name = 'eplan.missing.product'
    _description = 'Eplan Missing Product'

    eplan_bom_id = fields.Many2one('eplan.bom.line', string="Eplan")
    product_code = fields.Char(string='Product Code', required=True)
    description = fields.Char(string="Description")
    categ_id = fields.Many2one('product.category', string="Product category")
    can_be_sold = fields.Boolean(string="Can be Sold")
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')
    ], string='Product Type', default='product', required=True)


class WizardEplanConfirm(models.TransientModel):
    _name = 'wiz.eplan.confirm'
    _description = 'Eplan Confirmation'

    def action_create_bom_line_with_mo(self):
        if self._context.get('bom_id'):
            bom_id = self.env['mrp.bom'].browse(self._context.get('bom_id'))
            bom_id.bom_line_ids = self._context.get('product_lst')
            product_id = bom_id.product_id or bom_id.product_tmpl_id.product_variant_ids[0]
            product_uom_id = bom_id and bom_id.product_uom_id.id or product_id.uom_id.id
            mrp_prod_id = self.env['mrp.production'].with_context(default_bom_id=bom_id.id,import_file=True).create({
                'product_id' : product_id.id,
                'product_qty': bom_id.product_qty,
                'product_uom_id' : product_uom_id,
            })

    def action_create_bom(self):
        if self._context.get('bom_id'):
            bom_id = self.env['mrp.bom'].browse(self._context.get('bom_id'))
            bom_id.bom_line_ids = self._context.get('product_lst')

