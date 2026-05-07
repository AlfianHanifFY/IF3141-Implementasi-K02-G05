from odoo import models, fields

class Kwitansi(models.Model):
    _inherit = 'dokumen.dokumen'

    kwitansi_id = fields.Many2one(
        'dokumen.dokumen', 
        string='Invoice Terkait',
        domain=[('type', '=', 'invoice')],
        ondelete='cascade'
    )
    no_kwitansi = fields.Char(string='No Kwitansi')
    tgl_kwitansi = fields.Date(string='Tgl Kwitansi')
    value_kwitansi = fields.Float(string='Nominal Kwitansi')
    
