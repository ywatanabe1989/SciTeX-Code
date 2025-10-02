#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 22:03:48 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/dict/_DotDict.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import json


class DotDict:
    """
    A dictionary-like object that allows attribute-like access (for valid identifier keys)
    and standard item access for all keys (including integers, etc.).
    """

    def __init__(self, dictionary=None):
        # Use a private attribute to store the actual data
        # Avoids conflicts with keys named like standard methods ('keys', 'items', etc.)
        super().__setattr__("_data", {})
        if dictionary is not None:
            if isinstance(dictionary, DotDict):
                dictionary = dictionary._data
            elif not isinstance(dictionary, dict):
                raise TypeError("Input must be a dictionary.")

            for key, value in dictionary.items():
                if isinstance(value, dict) and not isinstance(value, DotDict):
                    value = DotDict(value)
                self[key] = value

    # --- Attribute Access (for valid identifiers) ---

    def __getattr__(self, key):
        # Called for obj.key when key is not found by normal attribute lookup
        # Allow access to internal methods/attributes starting with '_'
        if key.startswith("_"):
            return super().__getattribute__(
                key
            )  # Use superclass method for internal attrs
        try:
            return self._data[key]
        except KeyError:
            # Mimic standard attribute access behavior
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key, value):
        # Called for obj.key = value
        # Protect internal attributes
        if key == "_data" or key.startswith("_"):
            super().__setattr__(key, value)
        else:
            if isinstance(value, dict) and not isinstance(value, DotDict):
                value = DotDict(value)
            self._data[key] = value

    def __delattr__(self, key):
        # Called for del obj.key
        if key.startswith("_"):
            super().__delattr__(key)
        else:
            try:
                del self._data[key]
            except KeyError:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{key}'"
                )

    # --- Item Access (for any key type) ---

    def __getitem__(self, key):
        # Called for obj[key]
        return self._data[key]  # Raises KeyError if not found

    def __setitem__(self, key, value):
        # Called for obj[key] = value
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        self._data[key] = value

    def __delitem__(self, key):
        # Called for del obj[key]
        del self._data[key]  # Raises KeyError if not found

    # --- Standard Dictionary Methods (operating on _data) ---

    def get(self, key, default=None):
        # Use _data's get method
        return self._data.get(key, default)

    def to_dict(self):
        """
        Recursively converts DotDict and nested DotDict objects back to ordinary dictionaries.
        """
        result = {}
        for key, value in self._data.items():
            if isinstance(value, DotDict):
                value = value.to_dict()
            result[key] = value
        return result

    def __str__(self):
        """
        Returns a string representation, handling non-JSON-serializable objects.
        """

        def default_handler(obj):
            # Handle DotDict specifically during serialization if needed,
            # otherwise represent non-serializable items as strings.
            if isinstance(obj, DotDict):
                return obj.to_dict()
            try:
                # Attempt standard JSON serialization first
                json.dumps(obj)
                return obj  # Let json.dumps handle it if possible
            except (TypeError, OverflowError):
                return str(obj)  # Fallback for non-serializable types

        try:
            # Use the internal _data for representation
            return json.dumps(
                self.to_dict(), indent=4, default=default_handler
            )
        except TypeError as e:
            # Fallback if default_handler still fails (e.g., complex recursion)
            return f"<DotDict object at {hex(id(self))}, contains: {list(self._data.keys())}> Error: {e}"

    def __repr__(self):
        """
        Returns a string representation suitable for debugging.
        Shows the class name and the internal data representation.
        """
        # Use repr of the internal data for clarity
        return f"{type(self).__name__}({repr(self._data)})"

    def __len__(self):
        """
        Returns the number of key-value pairs in the dictionary.
        """
        return len(self._data)

    def keys(self):
        """
        Returns a view object displaying a list of all the keys.
        """
        return self._data.keys()

    def values(self):
        """
        Returns a view object displaying a list of all the values.
        """
        return self._data.values()

    def items(self):
        """
        Returns a view object displaying a list of all the items (key, value pairs).
        """
        return self._data.items()

    def update(self, dictionary):
        """
        Updates the dictionary with the key-value pairs from another dictionary or iterable.
        """
        if isinstance(dictionary, dict):
            iterator = dictionary.items()
        # Allow updating from iterables of key-value pairs
        elif hasattr(dictionary, "__iter__"):
            iterator = dictionary
        else:
            raise TypeError(
                "Input must be a dictionary or an iterable of key-value pairs."
            )

        for key, value in iterator:
            # Use __setitem__ to handle potential DotDict conversion
            self[key] = value

    def setdefault(self, key, default=None):
        """
        Returns the value of the given key. If the key does not exist, insert the key
        with the specified default value and return the default value.
        """
        if key not in self._data:
            # Use __setitem__ for potential DotDict conversion of default
            self[key] = default
            return default
        else:
            return self._data[key]

    def pop(self, key, *args):
        """
        Removes the specified key and returns the corresponding value.
        If key is not found, default is returned if given, otherwise KeyError is raised.
        Accepts optional default value like dict.pop.
        """
        # Mimic dict.pop behavior with optional default
        if len(args) > 1:
            raise TypeError(
                f"pop expected at most 2 arguments, got {1 + len(args)}"
            )
        if key not in self._data:
            if args:
                return args[0]  # Return default if provided
            else:
                raise KeyError(key)
        return self._data.pop(key)  # Use internal dict's pop

    def __contains__(self, key):
        """
        Checks if the dotdict contains the specified key.
        """
        return key in self._data

    def __iter__(self):
        """
        Returns an iterator over the keys of the dictionary.
        """
        return iter(self._data)

    def copy(self):
        """
        Creates a shallow copy of the DotDict object.
        Nested DotDicts/dicts/lists will be references, not copies.
        Use deepcopy for a fully independent copy.
        """
        # Create a new instance using a copy of the internal data
        return DotDict(self._data.copy())  # Shallow copy of internal dict

    def __dir__(self):
        """
        Provides attribute suggestions for dir() and tab completion.
        Includes both standard methods/attributes and the keys stored in _data.
        """
        # Get standard attributes/methods from the object's structure
        standard_attrs = set(super().__dir__())

        # Get the keys from the internal data dictionary
        # Filter for keys that are valid identifiers for attribute access
        data_keys = set(
            key
            for key in self._data.keys()
            if isinstance(key, str) and key.isidentifier()
        )

        # Return a sorted list of the combined unique names
        return sorted(list(standard_attrs.union(data_keys)))


# Example Usage:
if __name__ == "__main__":
    data = {
        "name": "example",
        "version": 1,
        100: "integer key",
        "nested": {"value1": True, 200: False},
        "list_val": [1, {"a": 2}],
        "invalid-key": "hyphenated",
    }

    dd = DotDict(data)

    # Access via attribute (for valid identifiers)
    print(f"dd.name: {dd.name}")
    print(f"dd.version: {dd.version}")
    print(f"dd.nested.value1: {dd.nested.value1}")
    # print(dd.100)  # This would be a SyntaxError, as expected

    # Access via item (for any key)
    print(f"dd[100]: {dd[100]}")
    print(f"dd['nested'][200]: {dd['nested'][200]}")
    print(f"dd['invalid-key']: {dd['invalid-key']}")

    # Modify values
    dd.name = "updated example"
    dd[100] = "new integer value"
    dd.nested[200] = "updated nested int key"
    dd[300] = "new top-level int key"  # Add new int key
    dd["new-key"] = "another invalid id key"

    print("\n--- After Modifications ---")
    print(f"dd.name: {dd.name}")
    print(f"dd[100]: {dd[100]}")
    print(f"dd.nested[200]: {dd.nested[200]}")
    print(f"dd[300]: {dd[300]}")
    print(f"dd['new-key']: {dd['new-key']}")

    print("\n--- Representation ---")
    print(f"repr(dd): {repr(dd)}")

    print("\n--- String (JSON) Representation ---")
    print(f"str(dd):\n{str(dd)}")

    print("\n--- Convert back to dict ---")
    plain_dict = dd.to_dict()
    print(f"plain_dict: {plain_dict}")
    print(f"plain_dict[100]: {plain_dict[100]}")
    print(f"plain_dict['nested'][200]: {plain_dict['nested'][200]}")

    print("\n--- Iteration ---")
    for k in dd:
        print(f"Key: {k}, Value: {dd[k]}")

    print("\n--- Contains ---")
    print(f"100 in dd: {100 in dd}")
    print(f"'name' in dd: {'name' in dd}")
    print(f"999 in dd: {999 in dd}")

    print("\n--- Copy ---")
    dd_copy = dd.copy()
    dd_copy[100] = "value in copy"
    dd_copy.name = "name in copy"
    print(f"Original dd[100]: {dd[100]}")
    print(f"Copy dd_copy[100]: {dd_copy[100]}")
    print(f"Original dd.name: {dd.name}")
    print(f"Copy dd_copy.name: {dd_copy.name}")

# class DotDict:
#     """
#     A dictionary subclass that allows attribute-like access to keys.
#     """

#     def __init__(self, dictionary):
#         for key, value in dictionary.items():
#             if isinstance(value, dict):
#                 value = DotDict(value)
#             setattr(self, key, value)

#     def __getitem__(self, key):
#         return getattr(self, key)

#     def __setitem__(self, key, value):
#         setattr(self, key, value)

#     def get(self, key, default=None):
#         return getattr(self, key, default)

#     def to_dict(self):
#         """
#         Recursively converts DotDict and nested DotDict objects back to ordinary dictionaries.
#         """
#         result = {}
#         for key, value in self.__dict__.items():
#             if isinstance(value, DotDict):
#                 value = value.to_dict()
#             result[key] = value
#         return result

#     # def __str__(self):
#     #     """
#     #     Returns a string representation of the dotdict by converting it to a dictionary and pretty-printing it.
#     #     """
#     #     return json.dumps(self.to_dict(), indent=4)

#     def __str__(self):
#         """
#         Returns a string representation, handling non-JSON-serializable objects.
#         """
#         def default_handler(obj):
#             return str(obj)

#         return json.dumps(self.to_dict(), indent=4, default=default_handler)

#     def __repr__(self):
#         """
#         Returns a string representation of the dotdict for debugging and development.
#         """
#         return self.__str__()

#     def __len__(self):
#         """
#         Returns the number of key-value pairs in the dictionary.
#         """
#         return len(self.__dict__)

#     def keys(self):
#         """
#         Returns a view object displaying a list of all the keys in the dictionary.
#         """
#         return self.__dict__.keys()

#     def values(self):
#         """
#         Returns a view object displaying a list of all the values in the dictionary.
#         """
#         return self.__dict__.values()

#     def items(self):
#         """
#         Returns a view object displaying a list of all the items (key, value pairs) in the dictionary.
#         """
#         return self.__dict__.items()

#     def update(self, dictionary):
#         """
#         Updates the dictionary with the key-value pairs from another dictionary.
#         """
#         for key, value in dictionary.items():
#             if isinstance(value, dict):
#                 value = DotDict(value)
#             setattr(self, key, value)

#     def setdefault(self, key, default=None):
#         """
#         Returns the value of the given key. If the key does not exist, insert the key with the specified default value.
#         """
#         if key not in self.__dict__:
#             self[key] = default
#         return self[key]

#     def pop(self, key, default=None):
#         """
#         Removes the specified key and returns the corresponding value.
#         """
#         return self.__dict__.pop(key, default)

#     def __contains__(self, key):
#         """
#         Checks if the dotdict contains the specified key.
#         """
#         return key in self.__dict__

#     def __iter__(self):
#         """
#         Returns an iterator over the keys of the dictionary.
#         """
#         return iter(self.__dict__)

#     def copy(self):
#         """
#         Creates a deep copy of the DotDict object.
#         """
#         return DotDict(self.to_dict().copy())

#     def __delitem__(self, key):
#         """
#         Deletes the specified key from the dictionary.
#         """
#         delattr(self, key)

# EOF
