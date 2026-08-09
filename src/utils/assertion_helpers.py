def format_assertion_error(field: str, expected, actual) -> str:
    return f"Field {field!r}: expected {expected!r}, got {actual!r}"


def assert_fields_match(actual: dict, expected: dict, context: str = "") -> None:
    """
    Asserts every key/value pair in `expected` is present and equal in `actual`.
    Extra keys in `actual` are ignored — checks that `expected` is a subset of
    `actual`, not that the two dicts are identical.
    """
    prefix = f"{context}: " if context else ""

    for field, expected_value in expected.items():
        if field not in actual:
            raise AssertionError(
                f"{prefix}Field {field!r} missing from actual response. Expected {field!r}={expected_value!r}"
            )

        actual_value = actual[field]
        if actual_value != expected_value:
            raise AssertionError(f"{prefix}{format_assertion_error(field, expected_value, actual_value)}")


def assert_description_update(response_json: dict, expected_keyword: str) -> bool:
    description = response_json["description"]
    return expected_keyword.lower() in description.lower()


def normalize_visibility(visibility: str) -> str:
    normalized = visibility.strip().lower()
    allowed_visibility = ["public", "private", "internal"]
    if normalized not in allowed_visibility:
        raise ValueError(
            f"Invalid visibility value: '{normalized}'. Expected one of {allowed_visibility}"
        )
    return normalized