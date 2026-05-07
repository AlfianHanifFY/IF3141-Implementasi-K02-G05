from odoo import models, fields

class PKS(models.Model):
    _inherit = 'dokumen.dokumen'

    pks_id = fields.Many2one(
        'client.prospect', 
        string='PKS',
        ondelete='cascade'
    )
    no_pks = fields.Char(string='No PKS')
    begin_date_pks = fields.Date(string='Tgl Mulai PKS')
    end_date_pks = fields.Date(string='Tgl Berakhir PKS')
    value_pks = fields.Float(string='Nilai PKS')
    

    