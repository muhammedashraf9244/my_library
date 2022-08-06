from datetime import timedelta
from odoo import models, fields, api
from odoo.tools.date_utils import end_of, start_of, add, get_month

""""
get_month(date or datetime) return start in index[0] and end in index [1] of month in date or datetime
start_of(date or datetime, granularity="year,month,week,day") return start of any granularity(year,month,week,day)
end_of(date or datetime, granularity="year,month,week,day") return end of any granularity(year,month,week,day)
add(date or datetime, years=n,months=m,week=e,days=d,hours=h,minutes=m,seconds=s) add date or datetime
"""


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = """ Library Book model"""
    _order = 'date_release desc, name'
    _rec_name = 'short_name'

    short_name = fields.Char("Short Name", required=True, translate=True, index=True)
    name = fields.Char('Title', required=True, copy=False)

    date_release = fields.Date('Release Date', default=add(fields.Date.today(), months=-1))
    date_end = fields.Date('Start Date', default=add(start_of(fields.Date.today(), 'month'), months=1))
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
    pages = fields.Integer('Number of Pages', groups='base.group_user',
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

    publisher_id = fields.Many2one('res.partner', string='Publisher', ondelete='set null', context={},
                                   domain=[])
    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True)

    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([
            ('field_id.name', '=', 'code')])

        return [(x.model, x.name) for x in models]

    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,  # optional
        compute_sudo=True  # optional
    )

    @api.depends('date_release')
    def _compute_age(self):
        for book in self:
            if book.date_release:
                delta = fields.Date.today() - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        print("Inverse ", self.filtered('date_release'))
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    def name_get(self):
        result = []
        print("library book ", self._name)
        if self._name == 'library.book':
            for record in self:
                rec_name = f"{record.name}, {record.date_release}"
                result.append((record.id, rec_name))
            return result
        else:
            return super().name_get()

    category_id = fields.Many2one('library.book.category', ondelete='restrict')

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)',
         'Book title must be unique.'),
        ('positive_page', 'CHECK(pages>0)',
         'No of pages must be positive')
    ]

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    def write(self, vals):
        if "ref_doc_id" in vals:
            print("ref_doc_id ", vals['ref_doc_id'])

        res = super().write(vals)
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    publisher_books_ids = fields.One2many("library.book", "publisher_id", string="Publish Books")

    _order = 'name'
    authored_book_ids = fields.Many2many('library.book', string='Authored Books')
    count_books = fields.Integer('Number of Authored Books ', compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for partner in self:
            partner.count_books = len(partner.authored_book_ids)
