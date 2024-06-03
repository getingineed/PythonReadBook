import socket
import threading

lock=threading.Lock()

def handle_client(client_socket):

    request = client_socket.recv(4096)
    print(f"Received request:\n{request.decode()}")

    proxy_host, proxy_port = '127.0.0.1', 7890
    server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((proxy_host, proxy_port))
    server_socket.send(request)

    def forward_data(source, destination):
        while True:
            try:
                data = source.recv(1024)
                destination.send(data)
            except socket.timeout:
                print("timeout")
                break
            except (ConnectionAbortedError, ConnectionResetError) as e:
                print(f"Connection error: {e}")
                break
    client_to_server = threading.Thread(target=forward_data, args=(client_socket, server_socket))
    server_to_client = threading.Thread(target=forward_data, args=(server_socket, client_socket))
    client_to_server.start()
    server_to_client.start()
    client_to_server.join()
    server_to_client.join()
    client_socket.close()
    server_socket.close()


def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind(('0.0.0.0', 9090))
    proxy_socket.listen(5)
    print("Proxy server listening on port 9090...")
    while True:
        client_socket, address = proxy_socket.accept()
        print(f"Received connection from {address}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket))
        client_handler.start()

start_proxy()