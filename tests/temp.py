assert is_instance(None, None)

assert is_instance("", Iterable[str]) and is_instance("", Reversible[str])
assert is_instance("", Iterable[Iterable[str]]) and is_instance(
    "", Reversible[Reversible[str]]
)

assert not is_instance(
    "", (Collection[int], Container[int], Iterable[int], Reversible[int], Sequence[int])
)
