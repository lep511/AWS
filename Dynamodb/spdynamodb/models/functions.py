from decimal import Decimal

def convert_floats_to_decimals(data):
    """
    Converts all float values in a dictionary (or nested data structure) to Decimal.
    """
    if isinstance(data, dict):
        return {key: convert_floats_to_decimals(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimals(item) for item in data]
    elif isinstance(data, float):
        return Decimal(str(data))  # Convert to Decimal for DynamoDB compatibility
    else:
        return data 