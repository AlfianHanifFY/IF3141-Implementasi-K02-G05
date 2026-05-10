from odoo import models, fields, api

class TargetLine(models.Model):
    _name = 'monitor.target.line'
    _description = 'Target Monitoring Line'
    _order = 'month_int asc'

    _MONTH_SELECTION = [
        ('01', '01. Januari'),
        ('02', '02. Februari'),
        ('03', '03. Maret'),
        ('04', '04. April'),
        ('05', '05. Mei'),
        ('06', '06. Juni'),
        ('07', '07. Juli'),
        ('08', '08. Agustus'),
        ('09', '09. September'),
        ('10', '10. Oktober'),
        ('11', '11. November'),
        ('12', '12. Desember'),
    ]

    _MONTH_ALIASES = {
        '1': '01',
        '2': '02',
        '3': '03',
        '4': '04',
        '5': '05',
        '6': '06',
        '7': '07',
        '8': '08',
        '9': '09',
    }

    target_id = fields.Many2one('monitor.target', string='Target Parent', ondelete='cascade')
    
    month = fields.Selection(
        _MONTH_SELECTION,
        string='Bulan',
        required=True,
    )

    month_int = fields.Integer(compute='_compute_month_int', store=True)

    amount_target = fields.Float(string='Target')
    amount_realized = fields.Float(string='Realisasi')
    amount_miss = fields.Float(string='Miss', compute='_compute_miss', store=True)
    achievement_rate = fields.Float(string='Pencapaian (%)', compute='_compute_achievement_rate', store=True)

    @api.depends('month')
    def _compute_month_int(self):
        for rec in self:
            month = self._normalize_month_value(rec.month)
            if month and month.isdigit():
                rec.month_int = int(month)
            else:
                rec.month_int = 0

    @api.model
    def _normalize_month_value(self, month_value):
        if not month_value:
            return month_value
        return self._MONTH_ALIASES.get(month_value, month_value)

    @api.model_create_multi
    def create(self, vals_list):
        normalized_vals_list = []
        for vals in vals_list:
            updated_vals = dict(vals)
            if 'month' in updated_vals:
                updated_vals['month'] = self._normalize_month_value(updated_vals['month'])
            normalized_vals_list.append(updated_vals)
        return super().create(normalized_vals_list)

    def write(self, vals):
        updated_vals = dict(vals)
        if 'month' in updated_vals:
            updated_vals['month'] = self._normalize_month_value(updated_vals['month'])
        return super().write(updated_vals)

    @api.depends('amount_target', 'amount_realized')
    def _compute_miss(self):
        for rec in self:
            # Miss = Target - Realisasi
            # Jika Realisasi >= Target, Miss = 0
            miss = rec.amount_target - rec.amount_realized
            rec.amount_miss = miss if miss > 0 else 0.0

    @api.depends('amount_target', 'amount_realized')
    def _compute_achievement_rate(self):
        for rec in self:
            if rec.amount_target > 0:
                rec.achievement_rate = (rec.amount_realized / rec.amount_target) * 100
            else:
                rec.achievement_rate = 0.0
