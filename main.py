import socket
import os
import time
import datetime
import mimetypes
from concurrent.futures import ThreadPoolExecutor


def GET_function(path, conn, request_headers):
    print(path)
    print(request_headers)
    path = 'html' + path
    # 404 Not Found
    if not os.path.exists(path):
        response = "HTTP/1.1 404 File Not Found \r\n\r\n"
        f = open('html/404.html')
        file_data = f.read()
        conn.send((response + file_data).encode())
        # log
        write_log("404 Not Found\n")
        return

    if path == 'html/':
        path = 'html/index.html'

    # open file in binary, last modified timestmap check
    with open(path, 'rb') as f:
        file_data = f.read()

    last_modified = get_last_modified(path)
    if 'If-Modified-Since' in request_headers:
        client_last_modified = str(request_headers.get("If-Modified-Since"))
        print(path + str(client_last_modified) + "vs" + str(last_modified))
        if client_last_modified == last_modified:
            # 304 Not modified
            response = b"HTTP/1.1 304 Not Modified\r\n\r\n"
            # log
            write_log("304 Not Modified\n")
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
    write_log("200 OK\n")
    conn.sendall(header + file_data)
    return


def head_function(path, conn):
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
    write_log("200 OK\n")
    connection.sendall(header.encode())


def send_bad_request(conn):
    response = "HTTP/1.0 400 Bad Request\r\n\r\n"
    f = open('html/400.html')
    file_data = f.read()
    conn.sendall((response + file_data).encode())


def request_rcv(conn, request, address):
    command = request.split()[0]
    path = request.split()[1]
    print(path)
    if path == "/":
        path = "/index.html"
    log_text = "Client: "+ str(address[0]) + ":" + str(address[1]) + "|" + str(time.ctime()) + "|" + "Host: " + request.split(" ")[0] + request.split(" ")[1] + "|"
    write_log(log_text)
    headers = {}
    lines = request.splitlines()
    for line in lines[1:]:
        if not line.strip():
            break
        head, value = line.split(': ', 1)
        headers[head] = value
    if 'Connection' in headers and headers['Connection'] == 'keep-alive':
        connection_alive = True
    else:
        connection_alive = False

    if command == 'HEAD':  # HEAD
        head_function(path, conn)
    elif command == 'GET':  # GET
        get_function(path, conn, headers)
    else:
        send_bad_request(conn)
    remove_short_lines()
    if not connection_alive:
        future.cancel()
        conn.close()


def write_log(text):
    file = open('log/log.txt', 'a+')
    file.write(text)
    file.close()
    # write_log1(text) #testing purposes
    return
def write_log1(text): #testing purposes
    file = open('log/log1.txt', 'a+')
    file.write(text)
    file.close()
    return


def get_last_modified(path):
    timestamp = os.path.getmtime(path)
    return str(timestamp)


def get_extension_type(path):
    content_type, _ = mimetypes.guess_type(path)
    return content_type or 'application/octet-stream'


def remove_short_lines():
    file_path = 'log/log.txt'
    strip = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if len(line) > 70:
            strip.append(str(line))
    with open(file_path, 'w') as file:
        file.writelines(strip)
    return


ip = '127.0.0.1'
port = 8080

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
skt.bind((ip, port))
skt.listen(5)
print('Listening on port ', port)

pool = ThreadPoolExecutor(max_workers=5)
while True:
    conn,addr = skt.accept()
    request = conn.recv(1024).decode('utf-8')
    if not request:
        continue
    print(request)
    # request_rcv(conn,request,addr)
    future = pool.submit(request_rcv, conn, request, addr)
skt.close()
