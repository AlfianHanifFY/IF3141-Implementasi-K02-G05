import base64
from datetime import datetime
import logging
from odoo import models, fields
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    _inherit = 'dokumen.dokumen'

    invoice_id = fields.Many2one(
        'client.prospect',
        string='Prospek Invoice',
        ondelete='cascade'
    )
    no_invoice = fields.Char(string='No Invoice')
    due_date_invoice = fields.Date(string='Tgl Jatuh Tempo Invoice')
    value_invoice = fields.Float(string='Nominal Invoice')
    description_invoice = fields.Text(string='Deskripsi Invoice')
    is_invoice_draft = fields.Boolean(string='Draft Invoice', default=False)

    def _escape_pdf_text(self, value):
        text = (value or '').replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')
        return text

    def _format_currency(self, value):
        amount = value or 0.0
        formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        return f"Rp {formatted}"

    def _split_text_lines(self, text, max_len=85):
        clean = (text or '').strip()
        if not clean:
            return ['-']

        lines = []
        for paragraph in clean.splitlines():
            words = paragraph.split()
            if not words:
                lines.append('')
                continue

            current = words[0]
            for word in words[1:]:
                candidate = f"{current} {word}"
                if len(candidate) <= max_len:
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            lines.append(current)

        return lines or ['-']

    def _generate_minimal_pdf(self):
        """Create a readable and dependency-free invoice-like 1-page PDF fallback."""
        self.ensure_one()

        invoice_title = self._escape_pdf_text('DRAFT INVOICE')
        invoice_no = self._escape_pdf_text(self.no_invoice or self.name or str(self.id))
        client_name = self._escape_pdf_text(self.client_id.company_name if self.client_id else '-')
        client_email = self._escape_pdf_text(self.client_id.pic_email if self.client_id else '-')
        nominal = self._escape_pdf_text(self._format_currency(self.value_invoice))
        due_date = self.due_date_invoice.strftime('%d-%m-%Y') if self.due_date_invoice else '-'
        issue_date = datetime.now().strftime('%d-%m-%Y')
        description_lines = [self._escape_pdf_text(line) for line in self._split_text_lines(
            self.description_invoice or self.description,
            max_len=45,
        )]

        commands = [
            'BT',
            '/F1 20 Tf',
            '50 805 Td',
            f'({invoice_title}) Tj',
            '/F1 10 Tf',
            '0 -18 Td',
            '(Perusahaan Anda) Tj',
            '0 -14 Td',
            '(Alamat Perusahaan Anda) Tj',
            '0 -22 Td',
            '(--------------------------------------------------------------------------------) Tj',
            '/F1 11 Tf',
            '0 -20 Td',
            f'(Bill To: {client_name}) Tj',
            '0 -16 Td',
            f'(Email PIC: {client_email}) Tj',
            '0 -20 Td',
            f'(Invoice No: {invoice_no}) Tj',
            '0 -16 Td',
            f'(Issue Date: {self._escape_pdf_text(issue_date)}) Tj',
            '0 -16 Td',
            f'(Due Date  : {self._escape_pdf_text(due_date)}) Tj',
            '0 -22 Td',
            '(--------------------------------------------------------------------------------) Tj',
            '/F1 10 Tf',
            '0 -18 Td',
            '(Item                                    Qty           Harga                 Jumlah) Tj',
            '0 -14 Td',
            '(--------------------------------------------------------------------------------) Tj',
            '0 -16 Td',
            '(Layanan/Proyek                           1) Tj',
            '220 0 Td',
            f'({nominal}) Tj',
            '110 0 Td',
            f'({nominal}) Tj',
            '-330 -18 Td',
        ]

        commands.append('(Deskripsi:) Tj')
        for idx, line in enumerate(description_lines[:6]):
            if idx == 0:
                commands.append('0 -14 Td')
            else:
                commands.append('0 -13 Td')
            commands.append(f'(- {line}) Tj')

        commands.extend([
            '0 -20 Td',
            '(--------------------------------------------------------------------------------) Tj',
            '/F1 11 Tf',
            '0 -18 Td',
            '(Subtotal) Tj',
            '360 0 Td',
            f'({nominal}) Tj',
            '-360 -16 Td',
            '(PPN 11%) Tj',
            '360 0 Td',
            '(Rp 0,00) Tj',
            '-360 -18 Td',
            '/F1 13 Tf',
            '(TOTAL) Tj',
            '360 0 Td',
            f'({nominal}) Tj',
            '-360 -26 Td',
            '/F1 10 Tf',
            '(Catatan:) Tj',
            '0 -14 Td',
            '(1. Mohon lakukan pembayaran sebelum tanggal jatuh tempo.) Tj',
            '0 -13 Td',
            '(2. Simpan invoice ini sebagai bukti penagihan.) Tj',
            '0 -28 Td',
            '(Hormat kami,) Tj',
            '0 -40 Td',
            '(__________________________) Tj',
            'ET',
        ])

        content = '\n'.join(commands) + '\n'

        objects = []
        objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
        objects.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
        objects.append(
            "3 0 obj\n"
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>\n"
            "endobj\n"
        )
        objects.append(
            "4 0 obj\n"
            f"<< /Length {len(content.encode('latin-1'))} >>\n"
            "stream\n"
            f"{content}"
            "endstream\n"
            "endobj\n"
        )
        objects.append("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

        pdf = "%PDF-1.4\n"
        offsets = [0]
        for obj in objects:
            offsets.append(len(pdf.encode('latin-1')))
            pdf += obj

        xref_pos = len(pdf.encode('latin-1'))
        pdf += f"xref\n0 {len(objects) + 1}\n"
        pdf += "0000000000 65535 f \n"
        for off in offsets[1:]:
            pdf += f"{off:010d} 00000 n \n"

        pdf += (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_pos}\n"
            "%%EOF"
        )

        return pdf.encode('latin-1')

    def action_create_draft_invoice(self):
        self.ensure_one()
        if self.type != 'invoice':
            raise UserError('Tombol ini hanya untuk dokumen bertipe Invoice.')

        pdf_content = self._generate_minimal_pdf()

        filename = f"Draft_Invoice_{self.no_invoice or self.name or self.id}.pdf"

        # 2. Opsional: Buat Draft di account.move jika modul account terpasang
        if 'account.move' in self.env:
            partner_obj = self.env['res.partner']
            partner = partner_obj.search([('name', '=', self.client_id.company_name)], limit=1)
            if not partner:
                partner = partner_obj.create({
                    'name': self.client_id.company_name,
                    'is_company': True,
                    'email': self.client_id.pic_email or False,
                })

            vals = {
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.context_today(self),
                'invoice_date_due': self.due_date_invoice or False,
                'ref': self.no_invoice or self.name,
                'invoice_origin': self.name or False,
                'narration': self.description_invoice or self.description or False,
            }
            self.env['account.move'].create(vals)

        # 3. Simpan file PDF ke record
        self.write({
            'is_invoice_draft': True,
            'file': base64.b64encode(pdf_content),
            'filename': filename,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Draft Invoice',
            'res_model': 'dokumen.dokumen',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
