def format_assertion_error(field: str, expected, actual) -> str:
    return f"Field {field!r}: expected {expected!r}, got {actual!r}"


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