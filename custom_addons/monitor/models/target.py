from odoo import models, fields, api

class Target(models.Model):
    _name = 'monitor.target'
    _description = 'Target Monitoring'

    name = fields.Char(string='Nama Target', required=True)
    year = fields.Selection(
        selection=[(str(y), str(y)) for y in range(2020, 2050)],
        string='Tahun',
        required=True,
        default=str(fields.Date.today().year)
    )   
    
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
    
    line_ids = fields.One2many(
        'monitor.target.line',
        'target_id',
        string='Target Bulanan'
    )

    total_target = fields.Float(string='Total Target', compute='_compute_totals', store=True)
    total_realized = fields.Float(string='Total Realisasi', compute='_compute_totals', store=True)
    total_miss = fields.Float(string='Total Miss', compute='_compute_totals', store=True)

    @api.depends('line_ids.amount_target', 'line_ids.amount_realized', 'line_ids.amount_miss')
    def _compute_totals(self):
        for rec in self:
            rec.total_target = sum(rec.line_ids.mapped('amount_target'))
            rec.total_realized = sum(rec.line_ids.mapped('amount_realized'))
            rec.total_miss = sum(rec.line_ids.mapped('amount_miss'))

    # Otomatis buat 12 bulan saat record dibuat
    @api.model_create_multi
    def create(self, vals_list):
        records = super(Target, self).create(vals_list)
        for record in records:
            if not record.line_ids:
                record._generate_target_lines()
        return records

    def action_generate_lines(self):
        for rec in self:
            if not rec.line_ids:
                rec._generate_target_lines()
        return True

    def _generate_target_lines(self):
        self.ensure_one()
        lines = []
        for month in range(1, 13):
            lines.append({
                'target_id': self.id,
                'month': str(month).zfill(2),
                'amount_target': 0.0,
                'amount_realized': 0.0,
            })
        self.env['monitor.target.line'].create(lines)
