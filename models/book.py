from odoo import models, fields
import datetime
from odoo.tools.date_utils import end_of, start_of, add, get_month


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = """ Library Book model"""
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    short_name = fields.Char("Short Name", required=True, translate=True, index=True)
    name = fields.Char('Title', required=True)

    date_release = fields.Date('Release Date', default=lambda self: get_month(add(end_of(fields.Date.today(), 'month'), months=1))[1])
    date_end = fields.Date('Start Date', default=lambda self: get_month(add(start_of(fields.Date.today(), 'month'), months=1))[0])
    author_ids = fields.Many2many('res.partner', string='Authors')
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('lost', 'Lost')],
        'State', default='draft')
    description = fields.Html('Description', sanitize=True, strip_style=False)
    notes = fields.Char()
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages',groups='base.group_user',
                           states={'lost': [('readonly', True)]},
                           help='Total book page count', company_dependent=False)
    reader_rating = fields.Float(
        'Reader Average Rating',
        digits=(14, 4),  # Optional precision decimals,
    )

    cost_price = fields.Float(
        'Book Cost', digits='Book Price')

    currency_id = fields.Many2one(
        'res.currency', string='Currency')
    retail_price = fields.Monetary(
        'Retail Price',
        # optional: currency_field='currency_id',
    )

    publisher_id = fields.Many2one('res.partner', string='Publisher',ondelete='set null',context={},domain=[])

    def name_get(self):
        result = []
        for record in self:
            rec_name = f"{record.name}, {record.date_release}"
        result.append((record.id, rec_name))
        return result

    category_id = fields.Many2one('library.book.category')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    publisher_books_ids = fields.One2many("library.book", "publisher_id", string="Publish Books")

