# library used to validate JSON data against a schema (rules/structure).
import pytest
from jsonschema import validate, ValidationError
from src.utils.logger import logger

def validate_schema(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        logger.error(f"Schema validation error:{e}")
        return False

def assert_valid_schema(data: dict, schema: dict, label: str):
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Schema validation failed for [{label}]: {e.message}")

