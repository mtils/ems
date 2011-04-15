#!/usr/bin/env python
# Copyright (c) 2007 Qtrac Ltd. All rights reserved.
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# The API and implementation are based on ideas from Paul Hankin.
# Efficiency improvements (addkeys/delkeys) and repr() implemented by
# Duncan Booth.

"""
A dictionary that is sorted by key or by the given cmp or key function.

Provides a dictionary with the same methods and behavior as a standard
dict and that can be used as a drop-in replacement for a dict (apart
from the constructor), but which always returns iterators and lists
(whether of keys or values) in sorted order. It does not matter when
items are inserted or when removed, the items in the sorteddict are
always returned in sorted order. The ordering is implicitly based on the
key's __lt__() (or failing that __cmp__()) method if no cmp or key
function is given.

The main benefit of sorteddicts is that you never have to explicitly
sort.

One use case is where you have a set of objects that you want to make
available in various sorted orders. You could, of course, sort on demand,
but if the number of objects is very large (and if you're prepared to
sacrifice some memory), it may be faster to use a sorteddict. For
example:

>>> class PrimeMinister:
...    def __init__(self, forename, surname, elected):
...        self.forename = forename
...        self.surname = surname
...        self.elected = elected
>>> byForename = sorteddict(key=lambda pm: (pm.forename, pm.surname))
>>> bySurname = sorteddict(key=lambda pm: (pm.surname, pm.forename))
>>> byName = sorteddict(key=lambda pm: (pm.surname, pm.forename,
...                                     pm.elected), reverse=True)
>>> byElected = sorteddict(key=lambda pm: pm.elected)
>>> for forename, surname, elected in (
...         ("Ramsay", "MacDonald", "1924-01-22"),
...         ("Arthur", "Balfour", "1902-07-11"),
...         ("Herbert Henry", "Asquith", "1908-04-07"),
...         ("Stanley", "Baldwin", "1924-11-04"),
...         ("David", "Lloyd George", "1916-12-07"),
...         ("Andrew", "Bonar Law", "1922-10-23"),
...         ("Henry", "Campbell-Bannerman", "1905-12-05"),
...         ("Stanley", "Baldwin", "1923-05-23"),
...         ("Ramsay", "MacDonald", "1929-06-05")):
...     pm = PrimeMinister(forename, surname, elected)
...     byForename[pm] = pm
...     bySurname[pm] = pm
...     byName[pm] = pm
...     byElected[pm] = pm
>>> [pm.forename for pm in byForename.values()]
['Andrew', 'Arthur', 'David', 'Henry', 'Herbert Henry', 'Ramsay', \
'Ramsay', 'Stanley', 'Stanley']
>>> [pm.surname for pm in bySurname.values()]
['Asquith', 'Baldwin', 'Baldwin', 'Balfour', 'Bonar Law', \
'Campbell-Bannerman', 'Lloyd George', 'MacDonald', 'MacDonald']
>>> ["%s %s %s" % (pm.forename, pm.surname, pm.elected) \
     for pm in byName.values()]
['Ramsay MacDonald 1929-06-05', 'Ramsay MacDonald 1924-01-22', \
'David Lloyd George 1916-12-07', 'Henry Campbell-Bannerman 1905-12-05', \
'Andrew Bonar Law 1922-10-23', 'Arthur Balfour 1902-07-11', \
'Stanley Baldwin 1924-11-04', 'Stanley Baldwin 1923-05-23', \
'Herbert Henry Asquith 1908-04-07']
>>> ["%s %s %s" % (pm.forename, pm.surname, pm.elected) \
     for pm in byElected.values()]
['Arthur Balfour 1902-07-11', 'Henry Campbell-Bannerman 1905-12-05', \
'Herbert Henry Asquith 1908-04-07', 'David Lloyd George 1916-12-07', \
'Andrew Bonar Law 1922-10-23', 'Stanley Baldwin 1923-05-23', \
'Ramsay MacDonald 1924-01-22', 'Stanley Baldwin 1924-11-04', \
'Ramsay MacDonald 1929-06-05']

Thanks to Python's object references, even though there are four
sorteddicts referring to the same PrimeMinister objects, only one instance
of each object is held in memory.

>>> files = ["README.txt", "readme", "MANIFEST", "test.py"]
>>> d = sorteddict([(name, name) for name in files],
...                cmp=lambda a, b: cmp(a.lower(), b.lower()))
>>> d.keys()
['MANIFEST', 'readme', 'README.txt', 'test.py']

Here are a few tests for some of the base class methods that are not
reimplemented:

>>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
>>> d.get("X", 21)
21
>>> d.get("i")
4
>>> d.has_key("a")
True
>>> d.has_key("x")
False
>>> "a" in d
True
>>> "x" in d
False
>>> len(d)
6
>>> del d["n"]
>>> del d["y"]
>>> len(d)
4
>>> d.clear()
>>> len(d)
0
>>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
>>> d["i"]
4
>>> d["y"]
6
>>> d["z"]
Traceback (most recent call last):
...
KeyError: 'z'

Check that a mix of adding and removing keys doesn't cause confusion:

>>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
>>> d.keys()
['a', 'i', 'n', 's', 't', 'y']
>>> del d["t"]
>>> d["t"]=6
>>> d.keys()
['a', 'i', 'n', 's', 't', 'y']

"""

__author__ = "Mark Summerfield"
__version__ = "1.2.1"

class sorteddict(dict):
    """A dictionary that is sorted by key or by the given cmp or key function.

    The sorteddict always returns any list or iterator in sorted order.
    For best performance prefer a key argument to a cmp one. If neither
    is given __lt__() (falling back to __cmp__()) will be used for
    ordering.

    This particular implementation has reasonable performance if the
    pattern of use is: lots of edits, lots of lookups, ..., but gives
    its worst performance if the pattern of use is: edit, lookup, edit,
    lookup, ..., in which case using a plain dict and sorted() will
    probably be better.

    If you want to initialize with a dict, either use
    sorteddict(dict(...), ...), or create the sorteddict and then call
    update with the arguments normally passed to a dict constructor.
    """

    def __init__(self, iterable=None, cmp=None, key=None, reverse=False):
        """Initializes the sorteddict using the same arguments as sorted()

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d.items()
        [('a', 2), ('i', 4), ('n', 3), ('s', 1), ('t', 5), ('y', 6)]
        >>> str(sorteddict())
        '{}'
        >>> e = sorteddict(d)
        >>> e.items()
        [('a', 2), ('i', 4), ('n', 3), ('s', 1), ('t', 5), ('y', 6)]
        """
        if iterable is None:
            iterable = []
        dict.__init__(self, iterable)
        self.__cmp = cmp
        self.__key = key
        self.__reverse = reverse
        self.__keycache = None
        self.__addkeys = set()
        self.__delkeys = set()


    @property
    def __keys(self):
        if self.__keycache is None:
            self.__keycache = dict.keys(self)
            self.__addkeys = set()
            self.__delkeys = set()
            self.__keycache.sort(cmp=self.__cmp, key=self.__key,
                                 reverse=self.__reverse)
        else:
            if self.__delkeys:
                delkeys = self.__delkeys
                self.__delkeys = set()
                self.__keycache = [key for key in self.__keycache \
                                   if key not in delkeys]
            if self.__addkeys:
                self.__keycache += list(self.__addkeys)
                self.__addkeys = set()
                self.__keycache.sort(cmp=self.__cmp, key=self.__key,
                                     reverse=self.__reverse)
        return self.__keycache


    def __invalidate_key_cache(self):
        self.__keycache = None
        self.__addkeys = set()
        self.__delkeys = set()


    def __addkey(self, key):
        if key in self.__delkeys:
            self.__delkeys.remove(key)
        else:
            self.__addkeys.add(key)


    def __removekey(self, key):
        if key in self.__addkeys:
            self.__addkeys.remove(key)
        else:
            self.__delkeys.add(key)


    def update(self, *args, **kwargs):
        """Updates the sorteddict using the same arguments as dict

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5))
        >>> d.update(a=4, z=-4)
        >>> d.items()
        [('a', 4), ('i', 4), ('n', 3), ('s', 1), ('t', 5), ('z', -4)]
        >>> del d["a"]
        >>> del d["i"]
        >>> d.update({'g': 9}, a=1, z=3)
        >>> d.items()
        [('a', 1), ('g', 9), ('n', 3), ('s', 1), ('t', 5), ('z', 3)]
        >>> e = sorteddict(dict(p=4, q=5))
        >>> del d["a"]
        >>> del d["n"]
        >>> e.update(d)
        >>> e.items()
        [('g', 9), ('p', 4), ('q', 5), ('s', 1), ('t', 5), ('z', 3)]
        """
        self.__invalidate_key_cache()
        dict.update(self, *args, **kwargs)


    @classmethod
    def fromkeys(cls, iterable, value=None):
        """A class method that returns an sorteddict whose keys are
        from the iterable and each of whose values is value

        >>> d = sorteddict()
        >>> e = d.fromkeys("KYLIE", 21)
        >>> e.items()
        [('E', 21), ('I', 21), ('K', 21), ('L', 21), ('Y', 21)]
        >>> e = sorteddict.fromkeys("KYLIE", 21)
        >>> e.items()
        [('E', 21), ('I', 21), ('K', 21), ('L', 21), ('Y', 21)]
        """
        dictionary = cls()
        for key in iterable:
            dictionary[key] = value
        return dictionary


    def copy(self):
        """Returns a shallow copy of this sorteddict

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> e = d.copy()
        >>> e.items()
        [('a', 2), ('i', 4), ('n', 3), ('s', 1), ('t', 5), ('y', 6)]
        >>> d = sorteddict()
        >>> e = d.copy()
        >>> e.items()
        []
        """
        return sorteddict(dict.copy(self), cmp=self.__cmp,
                          key=self.__key, reverse=self.__reverse)


    def clear(self):
        """Removes every item from this sorteddict

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> len(d)
        6
        >>> d.clear()
        >>> len(d)
        0
        >>> d["m"] = 3
        >>> d["a"] = 5
        >>> d["z"] = 7
        >>> d["e"] = 9
        >>> d.keys()
        ['a', 'e', 'm', 'z']
        """
        self.__invalidate_key_cache()
        dict.clear(self)


    def setdefault(self, key, value):
        """If key is in the dictionary, returns its value;
        otherwise adds the key with the given value which is also
        returned

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d.setdefault("n", 99)
        3
        >>> d.values()
        [2, 4, 3, 1, 5, 6]
        >>> d.setdefault("r", -20)
        -20
        >>> d.items()[2:]
        [('n', 3), ('r', -20), ('s', 1), ('t', 5), ('y', 6)]
        >>> d.setdefault("@", -11)
        -11
        >>> d.setdefault("z", 99)
        99
        >>> d.setdefault("m", 50)
        50
        >>> d.keys()
        ['@', 'a', 'i', 'm', 'n', 'r', 's', 't', 'y', 'z']
        """
        if key not in self:
            self.__addkey(key)
        return dict.setdefault(self, key, value)


    def pop(self, key, value=None):
        """If key is in the dictionary, returns its value and removes it
        from the dictionary; otherwise returns the given value

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d.pop("n")
        3
        >>> "n" in d
        False
        >>> d.pop("q", 41)
        41
        >>> d.keys()
        ['a', 'i', 's', 't', 'y']
        >>> d.pop("a")
        2
        >>> d.pop("t")
        5
        >>> d.keys()
        ['i', 's', 'y']
        """
        if key not in self:
            return value
        self.__removekey(key)
        return dict.pop(self, key, value)


    def popitem(self):
        """Returns and removes an arbitrary item from the dictionary

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> len(d)
        6
        >>> item = d.popitem()
        >>> item = d.popitem()
        >>> item = d.popitem()
        >>> len(d)
        3
        """
        item = dict.popitem(self)
        self.__removekey(item[0])
        return item


    def keys(self):
        """Returns the dictionary's keys in sorted order

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d.keys()
        ['a', 'i', 'n', 's', 't', 'y']
        """
        return self.__keys[:]


    def values(self):
        """Returns the dictionary's values in key order

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d.values()
        [2, 4, 3, 1, 5, 6]
        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6),
        ...               reverse=True)
        >>> d.values()
        [6, 5, 1, 3, 4, 2]
        >>> d = sorteddict(dict(S=1, a=2, N=3, i=4, T=5, y=6),
        ...                cmp=lambda a, b: cmp(a.lower(), b.lower()))
        >>> d.keys()
        ['a', 'i', 'N', 'S', 'T', 'y']
        """
        return [self[key] for key in self.__keys]


    def items(self):
        """Returns the dictionary's items in key order

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d.items()
        [('a', 2), ('i', 4), ('n', 3), ('s', 1), ('t', 5), ('y', 6)]
        """
        return [(key, self[key]) for key in self.__keys]


    def __iter__(self):
        """Returns an iterator over the dictionary's keys

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> list(d)
        ['a', 'i', 'n', 's', 't', 'y']
        """
        return iter(self.__keys)


    def iterkeys(self):
        """Returns an iterator over the dictionary's keys

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> list(d)
        ['a', 'i', 'n', 's', 't', 'y']
        """
        return iter(self.__keys)


    def itervalues(self):
        """Returns an iterator over the dictionary's values in key order

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> list(d.itervalues())
        [2, 4, 3, 1, 5, 6]
        """
        for key in self.__keys:
            yield self[key]


    def iteritems(self):
        """Returns an iterator over the dictionary's values in key order

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> list(d.iteritems())
        [('a', 2), ('i', 4), ('n', 3), ('s', 1), ('t', 5), ('y', 6)]
        """
        for key in self.__keys:
            yield key, self[key]


    def __delitem__(self, key):
        """Deletes the item with the given key from the dictionary

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> del d["s"]
        >>> del d["y"]
        >>> del d["a"]
        >>> d.keys()
        ['i', 'n', 't']
        >>> d = sorteddict()
        >>> d["a"] = "a"
        >>> d.keys()
        ['a']
        >>> del d["b"]
        Traceback (most recent call last):
        ...
        KeyError: 'b'
        >>> d["b"] = "b"
        >>> d.keys()
        ['a', 'b']
        """
        try:
            dict.__delitem__(self, key)
        except KeyError:
            raise
        else:
            self.__removekey(key)


    def __setitem__(self, key, value):
        """If key is in the dictionary, sets its value to value;
        otherwise adds the key to the dictionary with the given value

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5, y=6))
        >>> d["t"] = -17
        >>> d["z"] = 43
        >>> d["@"] = -11
        >>> d["m"] = 22
        >>> d["r"] = 5
        >>> d.keys()
        ['@', 'a', 'i', 'm', 'n', 'r', 's', 't', 'y', 'z']
        """
        if key not in self:
            self.__addkey(key)
        dict.__setitem__(self, key, value)


    def __repr__(self):
        """
        >>> sorteddict()
        sorteddict()
        >>> sorteddict({'a':1})
        sorteddict({'a': 1})
        >>> def comparison(a,b): return cmp(a,b)
        >>> def keyfn(a): return a
        >>> sorteddict({'a':1}, cmp=comparison) #doctest: +ELLIPSIS
        sorteddict({'a': 1}, cmp=<function comparison at ...>)
        >>> sorteddict({'a':1}, key=keyfn, reverse=True) #doctest: +ELLIPSIS
        sorteddict({'a': 1}, key=<function keyfn at ...>, reverse=True)
        """
        args = []
        if self:
            args.append(dict.__repr__(self))
        if self.__cmp is not None:
            args.append("cmp=%r" % self.__cmp)
        if self.__key is not None:
            args.append("key=%r" % self.__key)
        if self.__reverse is not False:
            args.append("reverse=%r" % self.__reverse)
        return "%s(%s)" % (self.__class__.__name__, ", ".join(args))


    def __str__(self):
        """Returns a human readable string representation of the
        dictionary

        The returned string is proportional in size to the number of
        items so could be very large.

        >>> d = sorteddict(dict(s=1, a=2, n=3, i=4, t=5))
        >>> str(d)
        "{'a': 2, 'i': 4, 'n': 3, 's': 1, 't': 5}"
        >>> d = sorteddict({2: 'a', 3: 'm', 1: 'x'})
        >>> str(d)
        "{1: 'x', 2: 'a', 3: 'm'}"
        """
        return "{%s}" % ", ".join(
               ["%r: %r" % (key, self[key]) for key in self.__keys])


if __name__ == "__main__":
    import doctest
    doctest.testmod()

