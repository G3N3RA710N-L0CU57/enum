"""
    Tool for scanning an IP address for any directories, using a 
    wordlist of your choice.

"""
from operator import eq
import socket
import gzip

def is_gzip_encoded(bytes_obj):
    """ Creates a new list while checking each line for gzip compressed data.
        If found, decompress using gzip module and append to new list. 
    """
    bytes_split = bytes_obj.split(b'\r\n')
    
    bytes_list = []
    for byte_line in bytes_split:

        if byte_line.startswith(b'\x1f\x8b'):
            decoded = gzip.decompress(byte_line)
            bytes_list.append(decoded)
            continue
        
        bytes_list.append(byte_line)

    return b''.join(bytes_list)

class HttpSocket():

    def __init__(self, host, port=80, http_sock=None):

        self.BUFF_SIZE = 4096
        self.host = host
        self.port = port
        self.chunks = []
        if http_sock == None:
            self.http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.http_sock = http_sock

    
    def connect(self):
        print('Connecting to socket ...')
        self.http_sock.connect((self.host, self.port))
        print('Socket connected ...')

    
    def send(self, header):
        
        self.header = header

        total_sent = 0

        self.header_bytes = self.header.encode('utf-8')

        while total_sent < len(self.header_bytes):
            sent = self.http_sock.send(self.header_bytes[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken.")
            total_sent += sent

        
    
    def receive(self):
        self.chunks = []

        print('Starting data received ...')
        while True:
            data = self.http_sock.recv(self.BUFF_SIZE)
            self.chunks.append(data)
            if len(data) < self.BUFF_SIZE: break
        
        print('Data received ...')

    def decode(self):
        self.byte_data = b''.join(self.chunks)

        self.byte_data_decompress = is_gzip_encoded(self.byte_data)

        self.string_data = self.byte_data_decompress.decode('utf-8')

        return self.string_data

    def close(self):
        self.http_sock.close()



    
def get_header(directory, host):

    return f"GET /{directory} HTTP 1.1\r\nHost:{host}\r\n\r\n"


host = 'www.python.org'

directory = '/docs'

http_obj = HttpSocket(host)

http_obj.connect()

header = get_header(directory, host)

http_obj.send(header)

http_obj.receive()

response = http_obj.decode()

print(response)