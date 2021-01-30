import os
from os.path import join, abspath
import socket

from config import Config

class FsConfig(Config):
    def __init__(self, schema):
        super().__init__(schema)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('127.0.0.1', 1337))

    def serve(self):
        while True:
            cmd, addr = self.s.recvfrom(1024)
            args = [x.decode() for x in cmd.split()]
            print(f'got: {args}')

            try:
                if args[0] == 'set':
                    response = self.set_from_cwd(*args[1:])    
                elif args[0] == 'get':
                    response = self.get_from_cwd(*args[1:])
                elif args[0] == 'save':
                    raise NotImplementedError()
                    response = self.set_from_cwd(*args[1:])
                else:
                    response = f'unrecognized command {args[0]}'
            except Exception as e:
                response = repr(e)
                
            response_encoded = str(response).encode()
            print(response_encoded)
            self.s.sendto(response_encoded, addr)

    def _find_absolute_path(self, cwd, relative_location):
        print(f'{cwd} ---- {relative_location}')
        total_location = abspath(join(abspath(cwd), relative_location.lstrip('/')))
        print(f'{total_location} ---- {self.deployed_path}')
        if not total_location.startswith(self.deployed_path):
            raise ValueError('not in our conf dir!')
        print(total_location[len(self.deployed_path):])
        return total_location[len(self.deployed_path):].replace('\\', '/')

    def set_from_cwd(self, cwd, relative_location, value):
        return self.set_value(self._find_absolute_path(cwd, relative_location), value)

    def get_from_cwd(self, cwd, relative_location):
        return self.get_value(self._find_absolute_path(cwd, relative_location))

    def save(self, output):
        with open(output, 'w') as f:
            json.dump(self.config, f, ident=4)

    def deploy_to_fs(self, location, schema=None):
        if schema is None:
            schema = self.schema
            self.deployed_path = abspath(location)
        if schema.get('type') != 'object':
            return False

        os.mkdir(location)
        for sub_dir in schema['properties']:
            sub_dir_path = join(location, sub_dir)
            if not self.deploy_to_fs(sub_dir_path, schema['properties'][sub_dir]):
                with open(sub_dir_path, 'w') as f:
                    pass
        return True