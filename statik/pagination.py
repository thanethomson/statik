# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import math

__all__ = [
    "paginate"
]


class PageIterator:
    def __init__(self, page):
        self.page = page
        self.cur_item = 0

    def __iter__(self):
        return self

    def next(self):
        if self.cur_item >= self.page.count:
            raise StopIteration()
        self.cur_item += 1
        return self.page.items[self.cur_item - 1]

    def __next__(self):
        return self.next()


class Page(object):
    """For representing a single page of items."""

    def __init__(self, paginator, number, items):
        """Constructor.

        Args:
            paginator: The parent paginator object.
            number: The number of this page (starting from 1).
            items: A list of items to belong to this page.
        """
        self.paginator = paginator
        self.number = number
        self.number0 = number - 1   # for zero-indexed pagination
        self.items = items
        self.count = len(items)

        # copy the paginator variables
        self.total_items = paginator.total_items
        self.items_per_page = paginator.items_per_page
        self.total_pages = paginator.total_pages
        self.page_range = paginator.page_range
        self.start_page = paginator.start_page
        self.last_page = paginator.last_page

    def __str__(self):
        return "%d" % self.number

    def __iter__(self):
        return PageIterator(self)

    def __len__(self):
        return self.count

    @property
    def has_next(self):
        return True if self.number < self.last_page else False

    @property
    def has_previous(self):
        return True if self.number > self.start_page else False


class PaginatorIterator:
    """A Python iterator for iterating through paginated items."""

    def __init__(self, paginator, start_page=1):
        self.paginator = paginator
        self.cur_page = start_page

    def __iter__(self):
        return self

    def next(self):
        if self.cur_page > self.paginator.last_page:
            raise StopIteration()
        self.cur_page += 1
        return self.paginator[self.cur_page - 1]

    def __next__(self):
        return self.next()


class Paginator(object):
    """Paginator class for encapsulating a collection of paged items."""

    def __init__(self, db_query, items_per_page, offset=0, start_page=1):
        """Constructor.

        Args:
            db_query: The database query to execute.
        """
        self.db_query = db_query
        self.items_per_page = items_per_page
        self.offset = offset
        self.start_page = start_page

        self.total_items = db_query.count() - offset
        self.total_pages = int(math.ceil(float(self.total_items) / float(items_per_page)))
        self.last_page = self.start_page + self.total_pages - 1
        self.page_range = range(self.start_page, self.last_page + 1)

    def empty(self):
        return self.total_pages == 0

    def __getitem__(self, page):
        if page < self.start_page or page > self.last_page:
            raise IndexError("Invalid page number: %d" % page)
        return Page(
            self,
            page,
            self.db_query.offset(
                self.offset + ((page-self.start_page) * self.items_per_page)
            ).limit(self.items_per_page).all()
        )

    def __len__(self):
        return self.total_pages

    def __iter__(self):
        return PaginatorIterator(self, start_page=self.start_page)


def paginate(db_query, items_per_page, offset=0, start_page=1):
    """Instantiates a Paginator instance for database queries.

    Args:
        db_query: The SQLAlchemy database query to paginate.
        items_per_page: The desired number of items per page.
        offset: The number of items to skip when paginating.
        start_page: The number of the first page when reporting on page numbers.
    """
    return Paginator(db_query, items_per_page, offset=offset, start_page=start_page)
