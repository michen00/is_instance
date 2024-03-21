# type: ignore
# pylint: disable=all
__all__ = [
    "is_instance",
]

import sys
import types
import typing
from collections import Counter, deque
from collections.abc import Callable, Container, Generator, Iterable, Iterator, Mapping
from functools import reduce
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
    last, _types = False, []
    append = _types.append
    for type_ in types_:
        if type_ is Ellipsis and last is Ellipsis:
            continue
        append(type_)
        last = type_
    types_ = deque(_types)
    print(types_, 1)

    # passing beyond this block indicates the remaining types sequence starts or ends
    # with Ellipsis
    deque_dots = deque([...])
    while len(types_) >= 2:
        if (first := types_[0] is not Ellipsis) or (last := types_[-1] is not Ellipsis):
            if not objs:
                return False
            if first and not is_instance(objs.popleft(), types_.popleft()):
                return False
            if not objs and types_ == deque_dots:
                return True
            if last:
                obj, typ = objs.pop(), types_.pop()
                if not (typ is Ellipsis or is_instance(obj, typ)):
                    return False
            continue
        break
    print(types_, 2)
    if len(types_) == 1:
        return types_[0] is Ellipsis or (
            len(objs) != 1 and is_instance(objs[0], types_[0])
        )
    print(types_, 3)

    # passing beyond this block additionally indicates that there remain fewer
    # non-ellipsis types to check than objects
    # if (non_ellipsis := len(types_) - Counter(types_)[...]) == (num_objs := len(objs)):
    #     return all(
    #         is_instance(obj, type_)
    #         for obj, type_ in zip(
    #             objs, filter(lambda _type: _type is not Ellipsis, types_)
    #         )
    #     )
    # print(types_, 4)
    # if non_ellipsis > num_objs:
    #     return False
    # print(types_, 5)

    # split remaining types on ...
    split_types = []
    store = split_types.append
    intermediate_result = []
    store_intermediate = intermediate_result.append
    for _type in types_:
        if _type is Ellipsis:
            if intermediate_result:
                store(intermediate_result)
                intermediate_result = []
            continue
        store_intermediate(_type)
    types_ = deque(split_types)
    print(types_, 6)

    while types_:
        current_types = types_.popleft()
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
