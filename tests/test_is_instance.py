# type: ignore
# pylint: disable=all
from collections.abc import (
    Collection,
    Container,
    Iterable,
    Mapping,
    Reversible,
    Sequence,
)

import is_instance
from is_instance.main import _ellipsis


def test_compat():
    assert is_instance("spam", str)
    assert is_instance("spam", (str, int))
    assert is_instance(True, int)
    assert not is_instance("spam", int)
    assert not is_instance("spam", (float, int))
    assert not is_instance(True, float)


def test_nesting():
    d1 = {"age": 88, "old": True}
    d2 = {"age": 22, "old": False}
    assert is_instance(["spam", "and", "eggs"], list[str])
    assert is_instance([], (list[int],))
    assert is_instance({1, 2, 3}, set[int])
    assert is_instance({"bird": True, "alive": False}, dict[str, bool])
    assert is_instance([{3: int}, {"s": str}], list[dict[object, type]])
    assert is_instance([d1, d2], list[dict[str, int | bool]])
    assert is_instance([d1, d2], list[dict[str, int]])
    assert not is_instance([d1, d2], list[dict[str, bool]])
    assert not is_instance([d1, d2], list[dict[str, str]])


def test_typed_tuples():
    # note: this example does not work in the corresponding slang,
    # since it's impossible to support that behavior without
    # sacrificing the more important goal of matching the builtin
    # isinstance behavior whenever possible. in other words:
    assert is_instance(("cake", "pie", 42), tuple[str, str, int])

    # make sure we still match builtin isinstance's behavior
    assert not isinstance(("cake", "pie", 42), (str, str, int))
    assert not is_instance(("cake", "pie", 42), (str, str, int))

    assert is_instance((1, "None", 2, None, 3), tuple[..., str, int, ..., int])
    assert is_instance((1, 2), tuple[int, ...])
    assert is_instance((1,), tuple[int, ...])
    assert is_instance((), tuple[()])
    assert not is_instance((), tuple[int, ...])
    assert is_instance((1, None, 2), tuple[int, ..., int])
    assert is_instance((1, None, "2"), tuple[int, ..., str])
    assert not is_instance(("1", None, 2), tuple[int, ..., str])
    assert not is_instance(("1", None, 2), tuple[..., ..., str])
    assert is_instance(("1", None, 2), tuple[..., ..., int])
    assert is_instance(("1", None, 2), tuple[str, ..., int])
    assert is_instance(("1", None, 2), tuple[str, ..., ...])
    assert is_instance(("1", None, 2), tuple[str, None, ...])
    assert is_instance(("", None, 2), tuple[str, None, ...])
    assert is_instance((1, None, "2"), tuple[int, ..., str])
    assert not is_instance((1, None, "2"), tuple[int, ..., None])
    assert not is_instance((1, None, "2"), tuple[str, ..., int])
    assert not is_instance((1, None, "2"), tuple[int, str])
    assert is_instance((1, None, 2), tuple[int, ..., ..., int])
    assert not is_instance((1, None, 2), tuple[int, ..., int, ..., int])
    assert is_instance((1, None, 2), tuple[int, ..., None, ..., int])
    assert is_instance((1, None, 2, None, 3), tuple[int, ...])
    assert is_instance((1, None, 2, None, 3), tuple[..., int])
    assert is_instance((1, "None", 2, None, 3), tuple[..., int])
    assert not is_instance((1, "None", 2, None, 3), tuple[..., str])
    assert not is_instance((1, "None", 2, None, 3), tuple[..., str, int, ..., str])
    assert not is_instance((1, "None", 2, None, 3), tuple[..., str, int, ..., ..., str])
    assert is_instance((1, "None", 2, None, 3), tuple[..., int, ..., ...])
    assert not is_instance(
        (1, "None", 2, None, 3), tuple[..., int, ..., str, None, int, int, ...]
    )


def test_slang():
    d1 = {"age": 88, "old": True}
    d2 = {"age": 22, "old": False}
    assert is_instance(["spam", "and", "eggs"], [str])
    assert is_instance([], [int])
    assert is_instance({1, 2, 3}, {int})
    assert is_instance({"bird": True, "alive": False}, {str: bool})
    assert is_instance([{3: int}, {"s": str}], [{object: type}])
    assert is_instance([d1, d2], [{str: int | bool}])
    assert is_instance([d1, d2], [{str: int}])
    assert not is_instance([d1, d2], [{str: bool}])
    assert not is_instance([d1, d2], [{str: str}])


def test_collection():
    assert is_instance(["cake"], Collection[str])
    assert not is_instance(["cake"], Collection[int])


def test_container():
    assert is_instance(["cake"], Container[str])
    assert not is_instance(["cake"], Container[int])


def test_iterable():
    assert is_instance(["cake"], Iterable[str])
    assert not is_instance(["cake"], Iterable[int])


def test_mapping():
    assert is_instance({"cake": "pie"}, Mapping[str, str])
    assert not is_instance({"cake": "pie"}, Mapping[str, int])


def test_reversible():
    assert is_instance(["cake"], Reversible[str])
    assert not is_instance(["cake"], Reversible[int])


def test_sequence():
    assert is_instance(["cake"], Sequence[str])
    assert not is_instance(["cake"], Sequence[int])


def test__ellipsis():

    assert _ellipsis((1, "None", 2, None, 3), [..., str, int, ..., int])
    assert _ellipsis((1, 2), [int, ...])
    assert _ellipsis((1,), [int, ...])
    assert not _ellipsis((), [int, ...])
    assert _ellipsis((1, None, 2), [int, ..., int])
    assert _ellipsis((1, None, 2), [int, ..., ..., int])
    assert not _ellipsis((1, None, 2), [int, ..., int, ..., int])
    assert _ellipsis((1, None, 2), [int, ..., None, ..., int])
    assert _ellipsis((1, None, 2, None, 3), [int, ...])
    assert _ellipsis((1, None, 2, None, 3), [..., int])
    assert _ellipsis((1, "None", 2, None, 3), [..., int])
    assert not _ellipsis((1, "None", 2, None, 3), [..., str])
    assert not _ellipsis((1, "None", 2, None, 3), [..., str, int, ..., str])
    assert not _ellipsis((1, "None", 2, None, 3), [..., str, int, ..., ..., str])
    assert _ellipsis((1, "None", 2, None, 3), [..., int, ..., ...])

    # Test case 1: Valid ordering with ellipsis
    assert _ellipsis([1, 2, 3], [int, ..., int])
    assert _ellipsis([1, 2, 3], [int, ..., ..., int])
    assert _ellipsis([1, 2, 3], [int, ..., ..., ..., int])

    # Test case 2: Valid ordering without ellipsis
    # assert _ellipsis([1, 2, 3], [int, int, int])

    # Test case 3: Invalid ordering with ellipsis
    assert not _ellipsis([1, 2, 3], [int, ..., str])
    assert not _ellipsis([1, 2, 3], [int, ..., ..., str])
    assert not _ellipsis([1, 2, 3], [int, ..., ..., ..., str])

    # Test case 4: Invalid ordering without ellipsis
    # assert not _ellipsis([1, 2, 3], [int, int, str])

    # Test case 5: Empty objects or types
    assert not _ellipsis([], [int, ..., int])
    # assert _ellipsis([1, 2, 3], [])
    # assert _ellipsis([], [])

    # Test case 6: Single object or type
    # assert _ellipsis([1], [int])
    assert not _ellipsis([1], [int, ..., int])
    assert not _ellipsis([1], [int, ..., ..., int])

    # Test case 7: Objects and types with different lengths
    # assert not _ellipsis([1, 2, 3], [int, int])
    # assert not _ellipsis([1, 2], [int, int, int])

    # Test case 8: Objects and types with different types
    assert not _ellipsis([1, 2, 3], [str, ..., int])
    assert not _ellipsis([1, 2, 3], [int, ..., str])

    # Test case 9: Objects and types with different orderings
    assert _ellipsis([1, 2, 3], [int, ..., int, int])
    assert _ellipsis([1, 2, 3], [int, int, ..., int])

    # Test case 10: Objects and types with ellipsis in the middle
    assert _ellipsis([1, 2, 3], [int, ..., int, ..., int])
