from odoo import models, fields, api, tools

class MonitorAMPerformanceReport(models.Model):
    _name = 'monitor.am.performance.report'
    _description = 'Laporan Kinerja AM'
    _auto = False

    am_id = fields.Many2one('res.users', string='Account Manager', readonly=True)
    
    # Prospect Metrics
    prospect_count = fields.Integer(string='Jumlah Prospek', readonly=True)
    won_count = fields.Integer(string='Prospek WON', readonly=True)
    total_contract_value = fields.Float(string='Total Estimasi Kontrak', readonly=True)
    
    # Activity Metrics
    activity_count = fields.Integer(string='Total Aktivitas', readonly=True)
    meeting_count = fields.Integer(string='Jumlah Meeting', readonly=True)
    phone_count = fields.Integer(string='Jumlah Telepon', readonly=True)
    email_count = fields.Integer(string='Jumlah Email', readonly=True)
    other_count = fields.Integer(string='Jumlah Lain-lain', readonly=True)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                WITH prospect_stats AS (
                    SELECT 
                        am_id,
                        count(id) as prospect_count,
                        count(id) FILTER (WHERE status = 'won') as won_count,
                        sum(contract_value) as total_contract_value
                    FROM client_prospect
                    GROUP BY am_id
                ),
                activity_stats AS (
                    SELECT 
                        am_id,
                        count(id) as activity_count,
                        count(id) FILTER (WHERE activity_type = 'meeting') as meeting_count,
                        count(id) FILTER (WHERE activity_type = 'phone') as phone_count,
                        count(id) FILTER (WHERE activity_type = 'email') as email_count,
                        count(id) FILTER (WHERE activity_type = 'other') as other_count
                    FROM log_am
                    GROUP BY am_id
                )
                SELECT 
                    row_number() OVER () as id,
                    u.id as am_id,
                    coalesce(ps.prospect_count, 0) as prospect_count,
                    coalesce(ps.won_count, 0) as won_count,
                    coalesce(ps.total_contract_value, 0) as total_contract_value,
                    coalesce(as_.activity_count, 0) as activity_count,
                    coalesce(as_.meeting_count, 0) as meeting_count,
                    coalesce(as_.phone_count, 0) as phone_count,
                    coalesce(as_.email_count, 0) as email_count,
                    coalesce(as_.other_count, 0) as other_count
                FROM res_users u
                LEFT JOIN prospect_stats ps ON u.id = ps.am_id
                LEFT JOIN activity_stats as_ ON u.id = as_.am_id
                WHERE ps.am_id IS NOT NULL OR as_.am_id IS NOT NULL
            )
        """ % self._table)
