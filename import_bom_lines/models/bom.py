# -*- coding: utf-8 -*-

from odoo import api, models, fields,_
from odoo.exceptions import Warning


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def import_eplan_bom(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Eplan'),
            'res_model': 'eplan.bom.line',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_bom_id': self.id}
        }