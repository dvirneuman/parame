import json
import jsonschema

from json_utils import default_values_from_schema

class Config(object):
    def __init__(self, schema_file):
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)
        self.config = default_values_from_schema(self.schema)
        self.read_callbacks = {}
        self.write_callbacks = {}

    def _generate_tree(self, location, value):
        sub_dirs = location.split('/')[1:]
        tree = {}
        current_tree = tree
        for sub_path in sub_dirs[:-1]:
            current_tree[sub_path] = {}
            current_tree = current_tree[sub_path]
        current_tree[sub_dirs[-1]] = value
        return tree

    def _get_containing_dir_and_filename(self, path):
        sub_dirs = path.split('/')[1:]
        current_dir = self.config
        for sub_path in sub_dirs[:-1]:
            current_dir = current_dir[sub_path]
        return current_dir, sub_dirs[-1]

    def direct_set_by_path(self, path, value):
        directory, filename = self._get_containing_dir_and_filename(path)
        directory[filename] = value

    def direct_get_by_path(self, path):
        directory, filename = self._get_containing_dir_and_filename(path)
        return directory[filename]

    def set_value(self, location, value):
        try:
            value = self._convert_value_type(location, value)
        except Exception as e:
            print(f'{location}: could not set to {value}. reason: {repr(e)}')
            raise e
        
        tree = self._generate_tree(location, value)
        try:
            jsonschema.validate(tree, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            print(sys.exc_info(e)[2])
            raise e
        
        callback = self._find_closest_callback(location, is_read=False)
        if callback:
            value = callback(location, value)

        self.direct_set_by_path(location, value)
        return value 

    def get_value(self, location):
        callback = self._find_closest_callback(location, is_read=True)
        if callback:
            value = callback(location)
            self.direct_set_by_path(location, value)
            return value

        return self.direct_get_by_path(location)

    def _convert_value_type(self, location, value):
        directory, filename = self._get_containing_dir_and_filename(location)
        return type(directory[filename])(value)

    def add_read_callback(self, location, callback):
        self.read_callbacks[location] = callback

    def add_write_callback(self, location, callback):
        self.write_callbacks[location] = callback

    def _find_closest_callback(self, location, is_read):
        callbacks = self.read_callbacks if is_read else self.write_callbacks
        
        matched_callback = None
        matched_length = 0
        for cb_location, callback in callbacks.items():
            if location.startswith(cb_location):
                if len(cb_location) > matched_length:
                    matched_length = len(cb_location)
                    matched_callback = callback

        return matched_callback

