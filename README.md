# is_instance

A better isinstance for python.

## examples

```python3
import is_instance

>>> is_instance(['spam', 'and', 'eggs'], list[str])
True

>>> is_instance(['spam', 'and', 'eggs'], list[int])
False

>>> is_instance({'bird': True, 'alive': False}, dict[str, bool])
True

>>> is_instance({(),(1,2),(4,5,'6')}, set[tuple[int]])
False

>>> is_instance({(),(1,2),(4,5,6)}, set[tuple[int]])
True

>>> is_instance([{'a': 1, 'b': None}, {'a': 3, 'b': 4}], list[dict[str, int]])
False

>>> is_instance([{'a': 1, 'b': None}, {'a': 3, 'b': 4}], list[dict[str, int|None]])
True
```

The following type slang is also supported, inspired by the Haskell type system.

```python3
import is_instance

>>> is_instance(['spam', 'and', 'eggs'], [str])
True

>>> is_instance(['spam', 'and', 'eggs'], [int])
False

>>> is_instance({'bird': True, 'alive': False}, {str: bool})
True

>>> is_instance([{'a': 1, 'b': None}, {'a': 3, 'b': 4}], [{str: int}])
False

>>> is_instance([{'a': 1, 'b': None}, {'a': 3, 'b': 4}], [{str: int | None}])
True
```

`is_instance` can also be used in place of pydantic's `.model_validate` with `strict=True`.

```python3
>>> from pydantic import BaseModel
>>> class Person(BaseModel):
...    name: str
...    age: int
>>> person_init = {"name": "Eric", "age": 42}
>>> person = Person(**person_init)

>>> is_instance(person_init, Person)
True

>>> is_instance(person_init, dict)
True

>>> is_instance(person, Person)
True

>>> is_instance(person, dict)
False

>>> is_instance(person, dict[str, int | str])
False

>>> is_instance(person_init, str)
False
```
