import socket

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
    print(request)

    filename = (request.split())[1]
    if filename == '/':
        filename = '/index.html'

    try:
        fin = open('html' + filename)
        content = fin.read()
        fin.close()

        response = 'HTTP/1.1 200 OK\n\n' + content
    except FileNotFoundError:
        fin404 = open('html/404.html')
        content404 = fin404.read()
        fin404.close()
        response = 'HTTP/1.1 404 NOT FOUND\n\n' + content404

    conn.sendall(response.encode())
    conn.close()