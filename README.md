# Odoo_Advance_Payment_Entries

## Behavior summary

* Adds an advance_payment monetary field to sale.order.
* Adds a button Create Advance Entry that creates a draft account.move with: Debit = partner receivable, Credit = Advance Received (liability).
* The module creates an Advance Received account and an Advance Journal on install.
* account.move is extended with sale_order_id linking back to the sale order.
* A chatter message is posted on the sale order with a link to the created draft journal entry. [To be implemented]