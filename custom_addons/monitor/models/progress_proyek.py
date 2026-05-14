from odoo import models, fields, api

class ProgressProyek(models.Model):
    _name = 'monitor.progress_proyek'
    _description = 'Progress Proyek Monitoring'

    name = fields.Char(string='Nama Progress Proyek', required=True)

    dokumen_id = fields.Many2one(
        'dokumen.dokumen',
        string='PKS / Proyek',
        domain="[('type', '=', 'pks')]"
    )

    prospect_id = fields.Many2one(
        'client.prospect',
        string='Prospect Klien',
        related='dokumen_id.client_id',
        store=True,
        readonly=True
    )

    project_manager_id = fields.Many2one(
        "res.users", string="Project Manager"
    )

    percentage = fields.Float(string='Progress (%)', required=True)
    description = fields.Text(string='Deskripsi')
    status = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('on review', 'On Review'),
        ('done', 'Done'),
    ], string='Status', required=True, default='open')
    date_start = fields.Date(string='Tanggal Mulai')
    date_end = fields.Date(string='Tanggal Selesai')   
    
    log_ids = fields.One2many(
        'monitor.log_progress_proyek',
        'progress_id',
        string='Log Progress'
    )
