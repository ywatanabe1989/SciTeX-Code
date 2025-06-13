#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-24 22:08:33 (ywatanabe)"
# File: ./scitex_repo/src/scitex/db/_Basemodules/_BaseTransactionMixin.py

THIS_FILE = (
    "/home/ywatanabe/proj/scitex_repo/src/scitex/db/_Basemodules/_BaseTransactionMixin.py"
)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import contextlib


class _BaseTransactionMixin:
    @contextlib.contextmanager
    def transaction(self):
        try:
            self.begin()
            yield
            self.commit()
        except Exception as e:
            self.rollback()
            raise e

    def begin(self):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def enable_foreign_keys(self):
        raise NotImplementedError

    def disable_foreign_keys(self):
        raise NotImplementedError

    @property
    def writable(self):
        raise NotImplementedError

    @writable.setter
    def writable(self, state: bool):
        raise NotImplementedError


# EOF
