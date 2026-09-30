import pytest
from jsonschema import validate, ValidationError


def assert_valid_schema(data: dict, schema: dict, label: str):
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed for [{label}]: {e.message}")

