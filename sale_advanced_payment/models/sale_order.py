from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_payment = fields.Monetary(string='Advance Payment', currency_field='currency_id')

    # advance_entry_ids = fields.One2many(
    #     'account.move',
    #     'sale_order_id', # This is the corresponding Many2one field on account.move
    #     string='Advance Journal Entries',
    #     readonly=True,
    # )
    # @api.depends('advance_entry_ids')
    # def _compute_advance_entry_count(self):
    #     for order in self:
    #         order.advance_entry_count = len(order.advance_entry_ids)

    def action_create_advance_entry(self):
        self.ensure_one()
        if not self.advance_payment or self.advance_payment <= 0.0:
            raise UserError(_('Advance payment amount must be set and greater than 0.'))
        
        partner = self.partner_id
        if not partner:
            raise UserError(_('Sale order must have a customer (partner) to create accounting entries.'))

        # Find the advance account and journal
        advance_account = self.env.ref('sale_advanced_payment.account_advance_received', raise_if_not_found=False)
        advance_journal = self.env.ref('sale_advanced_payment.journal_advance_payment', raise_if_not_found=False)
        if not advance_account or not advance_journal:
            raise UserError(_('Advance account or journal not found. Make sure the module data is installed.'))

        # Use partner receivable account
        receivable_account = partner.property_account_receivable_id
        if not receivable_account:
            raise UserError(_('The partner does not have a receivable account set.'))

        # Convert amount to company currency
        amount = self.advance_payment
        if self.currency_id != self.company_id.currency_id:
            amount = self.currency_id._convert(
                self.advance_payment, self.company_id.currency_id, self.company_id, self.date_order or fields.Date.context_today(self)
            )

        # Build Debit Line
        debit_vals = {
            'name': _('Advance payment for %s') % self.name,
            'partner_id': partner.id,
            'account_id': receivable_account.id,
            'debit': amount,
            'credit': 0.0,
        }
        if self.currency_id != self.company_id.currency_id:
            debit_vals.update({
                'currency_id': self.currency_id.id,
                'amount_currency': self.advance_payment,
            })
            
        # Build Credit Line
        credit_vals = {
            'name': _('Advance payment for %s') % self.name,
            'partner_id': partner.id,
            'account_id': advance_account.id,
            'debit': 0.0,
            'credit': amount,
        }
        if self.currency_id != self.company_id.currency_id:
            credit_vals.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.advance_payment,
            })

        move_vals = {
            'journal_id': advance_journal.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
            'company_id': self.company_id.id,
            'sale_order_id': self.id, # Custom field link
        }

        move = self.env['account.move'].with_context(default_move_type='entry').create(move_vals)
        
        # CORRECTED chatter message
        url_fragment = f"#id={move.id}&model=account.move&view_type=form"
        move_link = f'<a href="/web{url_fragment}">{move.display_name or _("Draft Entry")}</a>'
        message = _(
            "Created draft journal entry %s for advance payment of %s %s."
        ) % (move_link, self.advance_payment, self.currency_id.symbol)
        self.message_post(body=message)
        
        return move