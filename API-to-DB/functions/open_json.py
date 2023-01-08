import json

def open_json(path):
    json_data = open(path,'r', encoding='utf8')
    json_data = json.load(json_data)

    return json_data