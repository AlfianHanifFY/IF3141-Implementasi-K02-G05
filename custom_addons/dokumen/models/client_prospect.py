from odoo import models, fields

class ClientProspect(models.Model):
    _inherit = 'client.prospect'

    document_ids = fields.One2many(
        'dokumen.dokumen', 
        'client_id', 
        string='Dokumen'
    )
