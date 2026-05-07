from odoo import models, fields

class PO(models.Model):
    _inherit = 'dokumen.dokumen'

    po_id = fields.Many2one(
        'client.prospect', 
        string='PO',
        ondelete='cascade'
    )
    no_po = fields.Char(string='No PO')
    begin_date_po = fields.Date(string='Tgl Mulai PO')
    end_date_po = fields.Date(string='Tgl Berakhir PO')
    value_po = fields.Float(string='Nilai PO')
    description_po = fields.Text(string='Deskripsi PO')