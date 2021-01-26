from config import Config

class Daemon(Config):
    def __init__(self, schema_file):
        super().__init__(schema_file)
        self.add_read_callback('/videotestsrc0/num-buffers', self.read_num_buffers)
        self.add_read_callback('/', self.read_generic)
        self.add_write_callback('/videotestsrc0/blocksize', self.write_block_size)
    
    def read_num_buffers(self, location):
        print('read')

        return 0

    def read_generic(self, location):
        print('generic read')
        return self.direct_get_by_path(location)
    
    def write_block_size(self, location, value):
        if value % 1024:
            print("block must be multiply of 1024")
            return 1024
        else:
            print('write')
            return value

d = Daemon('props_schema2.json')

print(d.config)
d.set_value('/videotestsrc0/num-buffers', '51')
d.set_value('/videotestsrc0/blocksize', 2048)
print(d.config)
d.set_value('/videotestsrc0/blocksize', 1023)
d.set_value('/videotestsrc0/num-buffers', '501')
d.get_value('/videotestsrc0/num-buffers')
print(d.config)
