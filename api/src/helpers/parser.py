'''
Author: Thomas Grant
Copyright: © 2023 Thomas Grant
License: MIT License
'''
# Returns a list of objects that contain a keyword
def find_keyword(json_list, keyword):
    result = []
    for json_obj in json_list:
        if search_json(json_obj, keyword):
            result.append(json_obj)
    return result

# Search for a keyword through a json object
def search_json(json_obj, keyword):
    if isinstance(json_obj, dict):
        for value in json_obj.values():
            if search_json(value, keyword):
                return True
    elif isinstance(json_obj, list):
        for item in json_obj:
            if search_json(item, keyword):
                return True
    elif isinstance(json_obj, str):
        if keyword in json_obj:
            return True
    elif isinstance(json_obj, int):
        if keyword == json_obj:
            return True
    elif isinstance(json_obj, float):
        if keyword == json_obj:
            return True
    elif isinstance(json_obj, bool):
        if keyword == json_obj:
            return True
    return False