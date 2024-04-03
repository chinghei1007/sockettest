import email.utils
import socket
import os
import datetime
import mimetypes
import threading
from concurrent.futures import ThreadPoolExecutor


def file_send(path, conn, request_headers):
    path = 'html' + path
    # 404 Not Found
    if not os.path.exists(path):
        response = "HTTP/1.1 404 File Not Found \r\n\r\n"
        f = open('html/404.html')
        file_data = f.read()
        conn.sendall((response+file_data).encode())
        return

    if path == 'html/':
        path = 'html/index.html'
    # open file in binary, last modified timestmap check
    with open(path, 'rb') as f:
        file_data = f.read()

    last_modified = get_last_modified(path)
    if "If-Modified-Since" in request_headers:
        client_last_modified = request_headers.get("If-Modified-Since")
        if client_last_modified == last_modified:
            # 304 Not modified
            response = b"HTTP/1.1 304 Not Modified\r\n\r\n"
            print(response)
            conn.sendall(response)
            return

    # 200 OK header
    content_type = get_extension_type(path)
    header = b"HTTP/1.1 200 OK\r\n"
    header += f"Content-Type: {content_type}\r\n".encode()
    header += f"Content-Length: {len(file_data)}\r\n".encode()
    header += f"Last-Modified: {last_modified}\r\n".encode()
    header += b"\r\n"
    write_log(header+file_data)
    conn.sendall(header + file_data)


def head_function(path, conn, request_headers):
    path = 'html' + path
    # 404 Not Found
    if not os.path.exists(path):
        response = "HTTP/1.1 404 File Not Found\r\n\r\n"
        f = open('html/404.html')
        file_data = f.read()
        conn.sendall((response + file_data).encode())
        return

    if path == 'html/':
        path = 'html/index.html'

    last_modified = get_last_modified(path)
    content_type = get_extension_type(path)

    # 200 OK header
    header = "HTTP/1.1 200 OK\r\n"
    header += f"Content-Type: {content_type}\r\n"
    header += f"Last-Modified: {last_modified}\r\n"
    header += "\r\n"
    write_log(header)
    conn.sendall(header.encode())
    conn.close()

def request_rcv(conn,request):
    command = request.split()[0]
    path = request.split()[1]
    print(path)
    headers = {}
    lines = request.splitlines()
    for line in lines[1:]:
        if not line.strip():
            break
        head,value = line.split(': ', 1)
        headers[head] = value
    if command == 'HEAD': #HEAD
        head_function(path,conn,headers)
    else: #GET
        file_send(path,conn,headers)
    conn.close()

def write_log(text):
    with open('log/log.txt','a+') as file:
        file.write(request + '\n')

def get_last_modified(path):
    timestamp = os.path.getmtime(path)
    l_modi = datetime.datetime.utcfromtimestamp(timestamp)
    l_modi_str = email.utils.formatdate(timeval=l_modi.timestamp(),localtime=False,usegmt=True)
    return l_modi_str


def get_extension_type(path):
    content_type, _ = mimetypes.guess_type(path)
    return content_type or 'application/octet-stream'


ip = '127.0.0.1'
port = 8080

skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
skt.bind((ip,port))
skt.listen(5)
print('Listening on port ', port)

pool = ThreadPoolExecutor(max_workers=5)
while True:
    conn,addr = skt.accept()

    request = conn.recv(1024).decode()
    if not request:
        continue
    print(request)
    write_log(request)

    pool.submit(request_rcv, conn, request)
skt.close()
