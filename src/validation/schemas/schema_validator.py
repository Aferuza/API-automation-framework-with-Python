# library used to validate JSON data against a schema (rules/structure).
from jsonschema import validate, ValidationError
from src.utils.logger import logger

def validate_schema(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        logger.error(f"Schema validation error:{e}")
        return False
