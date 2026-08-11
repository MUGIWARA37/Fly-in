# mypy: ignore-errors
from typing import Dict, Tuple


def extract_metadata(raw_data: str) -> Tuple[str, Dict[str, str]]:
    raw_data = raw_data.strip()
    if "[" not in raw_data:
        return (raw_data, {})
    if not raw_data.endswith("]"):
        raise ValueError("trailing characters after metadata bracket")
    if raw_data.count("]") != 1:
        raise ValueError("multiple ']' brackets found")

    parts = raw_data.split("[")
    if len(parts) != 2:
        raise ValueError("multiple '[' brackets found")

    content, meta_data = parts
    meta_data = meta_data[:-1]

    filtered_data = {}
    if meta_data.strip():
        for data in meta_data.split():
            if "=" not in data:
                raise ValueError(f"metadata '{data}' is missing '='")
            key, value = data.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key in ("color", "zone"):
                if not value.isalpha():
                    raise ValueError(
                        f"metadata '{key}' must contain only letters")
            elif key in ("max_drones", "max_link_capacity"):
                if not value.isdigit():
                    raise ValueError(
                        f"metadata '{key}' must contain only numbers")

            filtered_data[key] = value

    return (content.strip(), filtered_data)


def parse_hub_parts(content: str) -> Tuple[str, int, int]:

    try:
        name, X, Y = content.split()
        X, Y = int(X), int(Y)
        return (name, X, Y)
    except ValueError:
        raise ValueError()


def split_connection(connection_name: str) -> Tuple[str, str]:
    n1, n2 = connection_name.split("-", 1)
    if not n1 or not n2 or "-" in n2:
        raise ValueError()
    return (n1, n2)


def validate_positive_int(line: str) -> int:
    try:
        value = int(line)
        if value > 0:
            return value
        else:
            raise ValueError("the number is negative !!")
    except Exception as e:
        raise ValueError(e)
