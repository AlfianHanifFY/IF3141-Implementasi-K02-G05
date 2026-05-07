from odoo import models, fields, api

class LogProgressProyek(models.Model):
    _name = 'monitor.log_progress_proyek'
    _description = 'Log Progress Proyek Monitoring'

    name = fields.Char(string='Judul Log', required=True)
    date = fields.Date(string='Tanggal', default=fields.Date.today, required=True)
    description = fields.Text(string='Deskripsi')
    
    progress_id = fields.Many2one(
        'monitor.progress_proyek',
        string='Progress Proyek',
        ondelete='cascade'
    )