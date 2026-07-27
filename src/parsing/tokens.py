from typing import Dict, Tuple

def extract_metadata(raw_data: str) -> Tuple[str , Dict[str, str]]:
    if '[' not in raw_data:
        return (raw_data.strip(), {})
    if ']' not in raw_data:
        raise ValueError()
    
    content , meta_data = raw_data.split('[')
    meta_data =meta_data.strip("]")
    
    filtered_data = {}
    
    meta_data = meta_data.split()
    for data in meta_data:
        key , value = data.split("=", 1)
        filtered_data[key.strip()] = value.strip()
    
    return (content.strip() , filtered_data)

def parse_hub_parts(content: str) -> Tuple[str, int, int]:
    
    try:
        name, X, Y = content.split()
        X, Y = int(X), int(Y)
        return (name, X, Y)
    except ValueError:
        raise ValueError()
    
def split_connection(connection_name: str) -> Tuple[str, str]:
    n1, n2 = connection_name.split('-', 1)
    if not n1 or not n2 or '-' in n2:
        raise ValueError()
    return (n1, n2)