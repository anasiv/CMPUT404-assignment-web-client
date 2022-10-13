#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from ast import arg
from email.quoprimime import header_decode
import sys
import socket
import re
from urllib import request, response
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):

        headers = data.split("\r\n\r\n")[0].split("\r\n")[1:]

        return headers

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    #figure out the hostname, port and path of a given URL
    #https://docs.python.org/3/library/urllib.parse.html
    def parse_URL(self, url):
        parsedurl = urllib.parse.urlparse(url)
        
        hostname = parsedurl.hostname

        #if port val is empty then use port 80 as default
        if parsedurl.port != None:
            port = parsedurl.port
        else:
            port = 80

        #if path stirng val is empty then return a forward slash as default
        if len(parsedurl.path) != 0:
            path = parsedurl.path
        else:
            path = "/"

        return hostname, port, path

    def GET(self, url, args=None):
        code = 500
        body = ""

        #call functon to split the different parts
        hostname, port, path = self.parse_URL(url)

        #connect, create and send request
        self.connect(hostname, port)

        #setup headders
        request = "GET {path} HTTP/1.1\r\n".format(path = path) + "Host: {hostname}:{port}\r\n".format(hostname = hostname, port = port) + "Connection: close\r\n" + "\r\n"

        self.sendall(request)

        #recieve and split request into code and body
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        #call functon to split the different parts
        hostname, port, path = self.parse_URL(url)

        #connect, create and send request
        self.connect(hostname, port)

        if args != None:
            content = urllib.parse.urlencode(args)
        else:
            content = ""
            
        #setup headders
        request = "POST {path} HTTP/1.1\r\n".format(path = path) + "Host: {hostname}:{port}\r\n".format(hostname = hostname, port = port) + "Connection: close\r\n" + "Content-Length: {content_len}\r\n".format(content_len = len(content)) + "\r\n" + "{content}\r\n".format(content = content) + "\r\n"

        self.sendall(request)

        #recieve and split request into code and body
        response = self.recvall(self.socket)
        code = self.get_code(response)
        body = self.get_body(response)
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
