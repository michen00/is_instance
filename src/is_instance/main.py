# type: ignore
# pylint: disable=all
__all__ = [
    "is_instance",
    "_ellipsis",
]

import sys
import types
import typing
from collections import Counter, deque
from collections.abc import Callable, Container, Generator, Iterable, Iterator, Mapping
from functools import reduce
from itertools import groupby, tee, zip_longest
from operator import or_


def is_instance(obj, cls, /) -> bool:
    """Turducken typing."""

    if isinstance(cls, tuple):
        return any(is_instance(obj, sub) for sub in cls)

    if isinstance(cls, types.UnionType):
        return any(is_instance(obj, sub) for sub in cls.__args__)

    if isinstance(cls, (list, set, dict)):
        cls = translate_slang(cls)

    if cls is None:
        cls = types.NoneType

    if not isinstance(cls, (types.GenericAlias, typing._GenericAlias)):
        return isinstance(obj, cls)

    if isinstance(cls, typing._LiteralGenericAlias):
        return obj in cls.__args__

    if not is_instance(obj, cls.__origin__):
        return False

    outer_type = cls.__origin__
    inner_types = typing.get_args(cls)

    if issubclass(outer_type, tuple):
        if Ellipsis in inner_types:
            return _ellipsis(obj, inner_types)
        if len(inner_types) != len(obj):
            return False
        return all(
            is_instance(item, inner_type) for item, inner_type in zip(obj, inner_types)
        )

    if issubclass(outer_type, Mapping):
        assert len(inner_types) == 2
        key_type, val_type = inner_types
        return all(
            is_instance(key, key_type) and is_instance(val, val_type)
            for key, val in obj.items()
        )

    if issubclass(outer_type, Generator):
        raise NotImplementedError("Generator not yet supported")

    if issubclass(outer_type, Iterator):
        raise NotImplementedError("Iterator not yet supported")

    if issubclass(outer_type, (Container, Iterable)):
        assert len(inner_types) == 1
        [inner_type] = inner_types
        if len(obj):
            return all(is_instance(item, inner_type) for item in obj)
        return is_instance(obj, inner_type) or hasattr(obj, "__class_getitem__")

    if issubclass(outer_type, Callable):
        raise NotImplementedError("Callable not yet supported")

    raise TypeError(obj, cls)


def _ellipsis(objs, types_, /) -> bool:
    """Check if objs is a valid ordering according to types in the subscript."""
    print("Called _ellipsis")
    objs, types_ = deque(objs), deque(types_)

    # collapse consecutive ellipses
    # _last, _types = False, []
    # append = _types.append
    # for type_ in types_:
    #     if type_ is Ellipsis and _last is Ellipsis:
    #         continue
    #     append(type_)
    #     _last = type_
    # types_ = deque(_types)
    # print(types_, 1)

    types_iter1, types_iter2 = tee(types_)
    next(types_iter2, None)
    types_ = deque(
        curr
        for curr, next_ in zip_longest(types_iter1, types_iter2)
        if curr is not Ellipsis or next_ is not Ellipsis
    )

    # passing beyond this block indicates the remaining types sequence starts or ends
    # with Ellipsis
    pop_objs_left, pop_objs_right = objs.popleft, objs.pop
    pop_types_left, pop_types_right = types_.popleft, types_.pop
    while len(types_) >= 2 and not (
        (first := types_[0] is Ellipsis) & (last := types_[-1] is Ellipsis)
    ):
        if not (objs and (first or is_instance(pop_objs_left(), pop_types_left()))) or (
            objs and not (last or is_instance(pop_objs_right(), pop_types_right()))
        ):
            return False
        continue
    print(types_, 2)

    # split remaining types on Ellipsis
    types_ = [
        [*group]
        for key, group in groupby(types_, lambda typ: typ is Ellipsis)
        if not key
    ]

    while types_:
        current_types = types_.pop()
        while current_types:
            if not objs:
                return False
            if not is_instance(objs.pop(), current_types[-1]):
                continue
            current_types.pop()

    return True


if sys.version_info >= (3, 11):
    # translate_slang needs to write cls[*obj],
    # which is apparently a syntax error in older
    # versions of python, so we shouldn't even
    # import the .slang module unless we're running
    # at least python 3.11
    from .slang import translate_slang
else:
    translate_slang = lambda x: x
