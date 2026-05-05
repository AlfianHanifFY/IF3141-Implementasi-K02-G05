from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ClientProspect(models.Model):
    _name = 'client.prospect'
    _description = 'Prospek Klien'
    _rec_name = 'display_name'
    _order = 'create_date desc, id desc'

    company_name = fields.Char(string='Nama Klien', required=True)
    project_name = fields.Char(string='Proyek', required=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    company_address = fields.Char(string='Alamat Perusahaan')
    pic_email = fields.Char(string='Email PIC')
    am_id = fields.Many2one(
        'res.users',
        string='Account Manager',
        required=True,
        default=lambda self: self.env.user,
    )
    classification = fields.Selection(
        [
            ('kecil', 'Kecil'),
            ('sedang', 'Sedang'),
            ('besar', 'Besar'),
        ],
        string='Klasifikasi Proyek',
        required=True,
        default='kecil',
    )
    probability = fields.Integer(string='Probabilitas (%)', required=True, default=0)
    priority = fields.Selection(
        [
            ('LOW', 'LOW'),
            ('MEDIUM', 'MEDIUM'),
            ('HIGH', 'HIGH'),
        ],
        string='Prioritas',
        required=True,
        default='MEDIUM',
    )
    status = fields.Selection(
        [
            ('new', 'NEW'),
            ('progress', 'PROGRESS'),
            ('won', 'WON'),
            ('loss', 'LOSS'),
        ],
        string='Status',
        required=True,
        default='new',
    )
    description = fields.Text(string='Deskripsi')
    currency_id = fields.Many2one('res.currency', string='Mata Uang', default=lambda self: self.env.ref('base.IDR'))
    contract_value = fields.Monetary(string='Nilai Kontrak (Estimasi)', currency_field='currency_id')
    start_date = fields.Date(string='Tanggal Mulai')
    expected_end_date = fields.Date(string='Estimasi Selesai')
    log_activity_ids = fields.One2many('log.am', 'client_id', string='Log Aktivitas')
    
    @api.depends('company_name', 'project_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.project_name} - {record.company_name}"

    @api.constrains('probability')
    def _check_probability(self):
        for record in self:
            if not (0 <= record.probability <= 100):
                raise ValidationError('Probabilitas harus antara 0 dan 100.')

    @api.constrains('expected_end_date', 'start_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.expected_end_date:
                if record.expected_end_date < record.start_date:
                    raise ValidationError('Estimasi Selesai harus setelah Tanggal Mulai.')
    