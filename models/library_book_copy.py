from odoo import models, fields, api


class LibraryBookCopy(models.Model):
    _name = "library.book.copy"
    _inherit = "library.book"
    _description = "Library Book's Copy"

    def name_get(self):
        result = []
        print("library book copy ", self._name)
        for record in self:
            name = '%s,%s Copy' % (record.name, record.date_release)
            result.append((record.id, name))

        return result
