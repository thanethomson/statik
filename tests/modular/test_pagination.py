# -*- coding: utf-8 -*-

import unittest

from statik.pagination import *


class MockDBQuery(object):

    def __init__(self, items):
        self._items = items
        self._offset = 0
        self._limit = None

    def count(self):
        return len(self._items)

    def offset(self, offset):
        self._offset = offset
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def all(self):
        limit = (len(self._items) - self._offset) if self._limit is None else self._limit
        return self._items[self._offset:(self._offset + limit)]


class TestStatikPagination(unittest.TestCase):

    def test_simple_multi_page_pagination(self):
        db_query = MockDBQuery([i for i in range(100)])
        paginator = paginate(db_query, 10)
        self.assertEqual(10, len(paginator))
        self.assertEqual(10, paginator.items_per_page)
        self.assertEqual(0, paginator.offset)
        self.assertEqual(100, paginator.total_items)
        self.assertEqual(10, paginator.last_page)
        self.assertEqual(1, paginator.start_page)
        self.assertFalse(paginator.empty())

        page_no = 1
        for page in paginator:
            self.assertTrue(isinstance(page.has_next, bool))
            self.assertTrue(isinstance(page.has_previous, bool))

            if page_no == 1:
                self.assertTrue(page.has_next)
                self.assertFalse(page.has_previous)
            elif page_no == 10:
                self.assertFalse(page.has_next)
                self.assertTrue(page.has_previous)
            else:
                self.assertTrue(page.has_next)
                self.assertTrue(page.has_previous)

            # test for page conversion to string -> page number
            self.assertEqual(page_no, int("%s" % page))

            self.assertEqual(page_no, page.number)
            self.assertEqual(page_no-1, page.number0)
            self.assertEqual(10, page.count)
            self.assertEqual(10, len(page.items))
            # test the page iterator
            self.assertEqual(10, len(page))
            self.assertEqual([i for i in range((page_no-1) * 10, page_no * 10)], page.items)

            self.assertEqual(100, page.total_items)
            self.assertEqual(10, page.total_pages)

            page_no += 1

        self.assertEqual(11, page_no)

    def test_empty_pagination(self):
        db_query = MockDBQuery([])
        paginator = paginate(db_query, 10)
        self.assertTrue(paginator.empty())
        self.assertEqual(0, paginator.total_items)
        self.assertEqual(0, paginator.total_pages)

        for page in paginator:
            self.fail("No pages should be iterated")

    def test_single_item_pagination(self):
        db_query = MockDBQuery([1])
        paginator = paginate(db_query, 10)
        self.assertFalse(paginator.empty())
        self.assertEqual(1, paginator.total_items)
        self.assertEqual(1, len(paginator))
        self.assertEqual(10, paginator.items_per_page)
        self.assertEqual(0, paginator.offset)

        page = paginator[1]
        self.assertEqual(1, page.number)
        self.assertEqual(0, page.number0)
        self.assertEqual([1], page.items)
        self.assertEqual(1, len(page))

    def test_complex_multi_page_pagination(self):
        db_query = MockDBQuery([i for i in range(100)])
        paginator = paginate(db_query, 10, offset=5)
        self.assertEqual(10, len(paginator))
        self.assertEqual(5, paginator.offset)
        self.assertEqual(95, paginator.total_items)

        # first page should start with item 5
        page = paginator[1]
        self.assertEqual(10, len(page))
        self.assertEqual([i for i in range(5, 15)], page.items)

        # last page should only have 5 items
        page = paginator[10]
        self.assertEqual(5, len(page))
        self.assertEqual([i for i in range(95, 100)], page.items)

    def test_non_standard_starting_page_number(self):
        db_query = MockDBQuery([i for i in range(100)])
        paginator = paginate(db_query, 10, start_page=2)
        self.assertEqual(10, len(paginator))
        self.assertEqual(range(2, 12), paginator.page_range)
        self.assertEqual(2, paginator.start_page)
        self.assertEqual(11, paginator.last_page)

        page_number = 2
        for page in paginator:
            self.assertEqual(page_number, page.number)
            self.assertEqual([i for i in range((page_number - 2) * 10, (page_number - 1) * 10)], page.items)

            if page_number == 2:
                self.assertFalse(page.has_previous)
                self.assertTrue(page.has_next)
            elif page_number == 11:
                self.assertTrue(page.has_previous)
                self.assertFalse(page.has_next)
            else:
                self.assertTrue(page.has_previous)
                self.assertTrue(page.has_next)

            page_number += 1

        self.assertEqual(12, page_number)

    def test_non_standard_starting_page_with_offset(self):
        db_query = MockDBQuery([i for i in range(100)])
        paginator = paginate(db_query, 10, offset=5, start_page=2)
        self.assertEqual(10, len(paginator))
        self.assertEqual(range(2, 12), paginator.page_range)
        self.assertEqual(11, paginator.last_page)


if __name__ == "__main__":
    unittest.main()
