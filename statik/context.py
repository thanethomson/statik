# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from copy import deepcopy, copy

from future.utils import iteritems
from statik.utils import underscore_var_names

import logging
logger = logging.getLogger(__name__)

__all__ = [
    "StatikContext"
]


class StatikContext(object):
    """For representing context in projects and views."""

    def __init__(
            self,
            initial=None,
            static=None,
            dynamic=None,
            for_each=None
        ):
        self.initial = initial or dict()
        self.static = underscore_var_names(
            deepcopy(static or dict())
        )
        self.dynamic = underscore_var_names(
            deepcopy(dynamic or dict())
        )
        self.for_each = underscore_var_names(
            deepcopy(for_each or dict())
        )
        logger.debug("Created Statik context instance: %s", self)

    def __repr__(self):
        return "StatikContext(initial=%s, static=%s, dynamic=%s, for_each=%s)" % (
            self.initial, self.static, self.dynamic, self.for_each
        )

    def __str__(self):
        return repr(self)

    def build_dynamic(self, db, safe_mode=False):
        """Builds the dynamic context based on our current dynamic context entity and the given
        database."""
        result = dict()
        for var, query in iteritems(self.dynamic):
            result[var] = db.query(query, safe_mode=safe_mode)
        return result

    def build_for_each(self, db, safe_mode=False, extra=None):
        """Builds the for-each context."""
        result = dict()
        for var, query in iteritems(self.for_each):
            result[var] = db.query(
                query,
                additional_locals=extra,
                safe_mode=safe_mode
            )
        return result

    def build(self, db=None, safe_mode=False, for_each_inst=None, extra=None):
        """Builds a dictionary that can be used as context for template rendering."""
        result = copy(self.initial)
        result.update(self.static)
        if self.dynamic:
            result.update(self.build_dynamic(db, safe_mode=safe_mode))
        if self.for_each and for_each_inst:
            result.update(self.build_for_each(db, safe_mode=safe_mode, extra=extra))
        if isinstance(extra, dict):
            result.update(extra)
        return result
