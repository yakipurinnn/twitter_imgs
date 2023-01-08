import os
import sys
import json
sys.path.append("./API-to-DB/functions")
from open_json import open_json

key_list_path = './API-to-DB/config/api_keys.json'
key_list = open_json(key_list_path)

print(key_list)