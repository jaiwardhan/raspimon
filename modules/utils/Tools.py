import yaml
import json
import os

class YamlToJSON:
    
    @staticmethod
    def convert_file(with_path, to_path=None):
        if  with_path is None or\
            len(str(with_path)) == 0 or\
            not os.path.exists(with_path) or\
            not os.path.isfile(with_path):
            return {}
        converted_json = {}
        try:
            converted_json = {}
            with open(str(with_path)) as yamlfile:
                converted_json = yaml.load(yamlfile)
        except:
            converted_json = {}
        if to_path and not os.path.isdir(to_path):
            with open(str(to_path), "w+") as write_file:
                write_file.write(json.dumps(converted_json, indent=4))
        return converted_json
    
    @staticmethod
    def convert(some_yaml, to_path=None, json_format=False):
        converted_json = {}
        try:
            converted_json = yaml.safe_load(some_yaml)
        except:
            converted_json = {}
        if to_path and not os.path.isdir(to_path):
            with open(str(to_path), "w+") as write_file:
                write_file.write(json.dumps(converted_json, indent=4))
        return converted_json
