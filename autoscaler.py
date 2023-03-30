import socket

# -- Constants --
# Response time thresholds in milliseconds
response_upper_threshold = 4000.0
response_lower_threshold = 1000.0

DATA_SIZE = 64
PORT = 65432

if __name__ == "__main__":

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Wait for client to connect
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('10.2.6.117', PORT))
            server_socket.listen()
            client_socket, client_address = server_socket.accept()

            # Receive average response time from client
            with client_socket:
                avg_response_time = float(client_socket.recv(DATA_SIZE).decode())
                print("Received avg_response_time: " + str(avg_response_time))