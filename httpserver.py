#!/usr/bin/env python3
import argparse

from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import urllib.request
from http_server_utils import *
from http_cache import HTTPCache
import os

MY_SERVER_NAME = 'cdn-http4.5700.network'
ORIGIN_SERVER = 'http://cs5700cdnorigin.ccs.neu.edu:8080'
DISK_LIMIT = 20000000


class ReplicaHTTPServer(BaseHTTPRequestHandler):
    """
    This class inherits from the BaseHTTPRequestHandler in the 'http.server' library and outlines logic for
    a GET request on the replica HTTP server.
    """

    def __init__(self, request: bytes, client_address: tuple[str, int], server: socketserver.BaseServer):
        super().__init__(request, client_address, server)
        self.http_cache = HTTPCache()

    def do_GET(self):
        """
        This method is an override of the do_GET function specified in the BaseHTTPRequestHandler class.
        If the data we are looking for based on the path exists in our cache, then we send that data over. Otherwise,
        we send the data from the origin server.
        """

        current_directory = get_current_directory()

        # if the file we're looking for exists in the disk cache, then pull the data
        # from there, otherwise go to the Origin server and pull the data from there.
        if does_file_exist(f'{current_directory}/{CACHE_DIRECTORY}/{self.path[1:]}'):

            # open the file from the cache
            with open(f'{current_directory}/{CACHE_DIRECTORY}/{self.path[1:]}', "r") as file:
                file_lines = file.readlines()

            # join the string list and send the data back out.
            joined_result = "".join(file_lines)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(joined_result.encode('utf-8'))
            return

        else:
            # self.send_response(200)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()
            # self.wfile.write(bytes("<html><body><h1>Hello World</h1></body></html>", "utf-8"))
            #
            # file = open("example.html", "w")
            # actual_resource_path = f'{ORIGIN_SERVER}/{self.path[1:]}'
            # # Write some text to the file
            # file.write(actual_resource_path)
            #
            # # Close the file
            # file.close()
            try:
                # actual path to the resource on the Origin server
                actual_resource_path = f'{ORIGIN_SERVER}/{self.path[1:]}'

                # contact the Origin server for the requested resource
                with urllib.request.urlopen(actual_resource_path) as response:
                    # Set the response status code and headers
                    self.send_response(response.status)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.read())

                # work on caching the data we just found
                # todo
                """
                1. determine the size of the cache directory
                2.      -> if the size + current file size > limit,
                            -> keep removing lowest priority files until there is enough space to hold this new file
                            (i.e. until the size of the directory + current file size <= limit)
                        -> else:
                            add the file to the directory
                """

            except Exception as e:
                print("Unble to retrieve data from the origin server. Please request for the resource again")
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()


def main(server_port_number):
    """
    The entry point into the http server.
    Args:
        server_port_number: the port number this http server is listening/sending on

    """
    # create the cache directory if it doesn't exist, because this is where we
    # store all the cached data.
    if not os.path.exists(CACHE_DIRECTORY):
        os.makedirs(CACHE_DIRECTORY)

    with socketserver.TCPServer(("127.0.0.1", server_port_number), ReplicaHTTPServer) as httpd:
        print("serving at port", server_port_number)
        httpd.serve_forever()

if __name__ == "__main__":
    # Define the command line arguments
    parser = argparse.ArgumentParser(description="Determine HTTP Server arguments")
    parser.add_argument('-p', dest="port", action='store', type=int, help="Port Number")
    parser.add_argument('-o', dest="origin", action='store', type=str, help="The origin server")

    # specify the port number and the origin server
    port_number = 0

    origin_server = ''
    # Parse the arguments
    args = parser.parse_args()

    # if the origin server and the port number are stated in the arguments, then we set them here,
    # otherwise we revert them to their defaults.
    if args.origin and args.port:
        port_number = args.port
        ORIGIN_SERVER = args.origin
    else:
        port_number = 20200  # port 20200 is bitbuster's specific port number
        ORIGIN_SERVER = 'cs5700cdnorigin.ccs.neu.edu:8080'

    # Call the main method with the specified port and origin
    main(port_number)