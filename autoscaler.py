import socket
import docker
from math import ceil, floor

# -- Constants --
# Response time thresholds in milliseconds
response_upper_threshold = 4000.0
response_lower_threshold = 3000.0
n_services = 0 # Default when locust is started up

HOST = socket.gethostbyname(socket.gethostname())
DATA_SIZE = 64
PORT = 65432

web_service_token = 'j6l7gvw0gdm0'
web_service = docker.from_env().services.get(web_service_token)

# Decide what to do with current avg response time
def analyze_response_time(avg_response_time):
    margin = response_upper_threshold - response_lower_threshold
    global n_services

    if (avg_response_time > response_upper_threshold): # Increase services
        service_change = ceil((avg_response_time - response_upper_threshold) / margin)
        scale_web_services(service_change)

    elif (avg_response_time < response_lower_threshold): # Decrease services
        service_change = floor((avg_response_time - response_lower_threshold) / margin)
        if (n_services + service_change) > 0: # Dont go below 1 service
            scale_web_services(service_change)

# Change number of web services
def scale_web_services(service_change):
    global n_services
    global web_service

    print("Services: {} -> {}".format(n_services, n_services + service_change))
    n_services = n_services + service_change
    web_service.update(mode={'Replicated': {'Replicas': n_services}})
    web_service = docker.from_env().services.get(web_service_token)


if __name__ == "__main__":

    # web_service.update(mode={'Replicated': {'Replicas': 1}})
    n_services = web_service.attrs["Spec"]["Mode"]["Replicated"]["Replicas"]
    print("Autoscaler started ({} services)".format(n_services))

    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Wait for client to connect
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            client_socket, client_address = server_socket.accept()

            # Receive average response time from client
            with client_socket:
                avg_response_time = float(client_socket.recv(DATA_SIZE).decode())
                print("Received avg_response_time: " + str(avg_response_time))
                analyze_response_time(avg_response_time)