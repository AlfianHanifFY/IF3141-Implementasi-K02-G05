import base64

from odoo import models, fields, api
from odoo.exceptions import UserError

class Dokumen(models.Model):
    _name = 'dokumen.dokumen'
    _description = 'Dokumen Prospek'

    name = fields.Char(string='Nama Dokumen', required=True)
    file = fields.Binary(string='File')
    filename = fields.Char(string='Nama File')
    client_id = fields.Many2one(
        'client.prospect', 
        string='Prospek Klien',
        ondelete='cascade'
    )
    description = fields.Text(string='Deskripsi')

    type = fields.Selection([
        ('other', 'Other'),
        ('pks', 'PKS'),
        ('po', 'PO'),
        ('invoice', 'Invoice'),
        ('kwitansi', 'Kwitansi'),
    ], string='Type', default='other')

    deadline_date = fields.Date(string='Deadline', compute='_compute_deadline_date', store=True)

    @api.depends('type', 'end_date_pks', 'due_date_invoice', 'end_date_po')
    def _compute_deadline_date(self):
        for rec in self:
            if rec.type == 'pks':
                rec.deadline_date = getattr(rec, 'end_date_pks', False)
            elif rec.type == 'invoice':
                rec.deadline_date = getattr(rec, 'due_date_invoice', False)
            elif rec.type == 'po':
                rec.deadline_date = getattr(rec, 'end_date_po', False)
            else:
                rec.deadline_date = False
