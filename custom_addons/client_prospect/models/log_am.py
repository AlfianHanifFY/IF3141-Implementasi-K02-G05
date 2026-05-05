from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LogAM(models.Model):
    _name = 'log.am'
    _description = 'Log AM'

    client_id = fields.Many2one('client.prospect', string='Client')
    am_id = fields.Many2one('res.users', string='Responsible',default=lambda self: self.env.user)
    activity_type = fields.Selection([
        ('meeting', 'Meeting'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('other', 'Other'),
    ], string='Activity Type')
    date = fields.Datetime(string='Date')
    notes = fields.Text(string='Notes')
    result = fields.Text(string='Result')
    status = fields.Selection([
        ('new', 'New'),
        ('progress', 'Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='Status', default='new')


    