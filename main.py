import email.utils
import socket
import os
import datetime
import mimetypes


def file_send(path, conn, request_headers):
    path = 'html' + path
    # 404 Not Found
    if not os.path.exists(path):
        response = "HTTP/1.1 404 File Not Found \r\n\r\n"
        f = open('html/404.html')
        file_data = f.read()
        conn.sendall((response+file_data).encode())
        return

    if path == '/':
        path = '/index.html'
    # open file in binary, last modified timestmap check
    with open(path, 'rb') as f:
        file_data = f.read()

    last_modified = get_last_modified(path)
    if "If-Modified-Since" in request_headers:
        client_last_modified = request_headers.get("If-Modified-Since")
        if client_last_modified == last_modified:
            # 304 Not modified
            response = b"HTTP/1.1 304 Not Modified\r\n\r\n"
            conn.sendall(response)
            return

    # 200 OK header
    content_type = get_extension_type(path)
    header = b"HTTP/1.1 200 OK\r\n"
    header += f"Content-Type: {content_type}\r\n".encode()
    header += f"Content-Length: {len(file_data)}\r\n".encode()
    header += f"Last-Modified: {last_modified}\r\n".encode()
    header += b"\r\n"
    conn.sendall(header + file_data)


def request_rcv(conn,request):
    path = request.split()[1]
    print(path)
    headers = {}
    lines = request.splitlines()
    for line in lines[1:]:
        if not line.strip():
            break
        head,value = line.split(': ', 1)
        headers[head] = value
    file_send(path,conn,headers)
    conn.close()


def get_last_modified(path):
    timestamp = os.path.getmtime(path)
    l_modi = datetime.datetime.utcfromtimestamp(timestamp)
    l_modi_str = email.utils.formatdate(timeval=l_modi.timestamp(),localtime=False,usegmt=True)
    return l_modi_str


def get_extension_type(path):
    content_type, _ = mimetypes.guess_type(path)
    return content_type or 'application/octet-stream'


ip = '0.0.0.0'
port = 8080

skt = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
skt.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
skt.bind((ip,port))
skt.listen()
print('Listening on port ', port)

while True:
    conn,addr = skt.accept()
    request = conn.recv(1024).decode()
    if not request:
        continue
    print(request)
    request_rcv(conn,request)
    conn.close()
skt.close()