"""
    Tool for scanning an IP address for any directories, using a 
    wordlist of your choice.

"""
from operator import eq
import socket
import gzip
import argparse

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
    """ Wrapper for a http socket """

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
        """ Connect the socket """
        self.http_sock.connect((self.host, self.port))
        print('Socket connected ...')

    
    def send(self, header):
        """ Sends the header to remote host. """
        self.header = header

        total_sent = 0

        self.header_bytes = self.header.encode('utf-8')

        while total_sent < len(self.header_bytes):
            sent = self.http_sock.send(self.header_bytes[total_sent:])
            if sent == 0:
                raise RuntimeError("socket connection broken.")
            total_sent += sent
        print('Data sent ...')
        
    
    def receive(self):
        """ Receive data from the host """
        self.chunks = []

        while True:
            data = self.http_sock.recv(self.BUFF_SIZE)
            self.chunks.append(data)
            if len(data) < self.BUFF_SIZE: break
        
        print('Data received ...')

    def decode(self):
        """ Decodes the data into utf-8 and returns the string, if data is
            gzip compressed, it decompresses first before decoding.
        """
        self.byte_data = b''.join(self.chunks)

        self.byte_data_decompress = is_gzip_encoded(self.byte_data)

        self.string_data = self.byte_data_decompress.decode('utf-8')

        return self.string_data

    def close(self):
        self.http_sock.close()



    
def get_header(directory, host):
    """ Creates a GET request with directory and host. """
    return f"GET /{directory} HTTP/1.1\r\nHost: {host}\r\n\r\n"


# Option parser.
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--file", help="Wordlist file.")

parser.add_argument("-ht", "--host", help="Host address to search.")

args = parser.parse_args()



sock = HttpSocket(args.host)

sock.connect()

with open(args.file, 'r') as file:

    for line in file:

        line = line.replace('\n', '')

        header = get_header(line, args.host)

        sock.send(header)

        sock.receive()

        response = sock.decode()

        print(response)


sock.close()

