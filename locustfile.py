from locust import HttpUser, task, between
from locust.env import Environment

import socket
import gevent

# -- Constants --
sample_time         = 10 # How often to send the average response time to the swarm manager (in seconds)
percentile          = 95.0 # Percentile of response times to consider for the average
swarm_manager_ip    = '10.2.6.117'
web_app_port        = 8000
autoscaler_port     = 65432

# -- Function to monitor average response time --
def update_avg_response_time(environment: Environment):
    while True:
        # Sample average response time
        avg_response_time = environment.    \
                            stats.  \
                            get("/", "GET").    \
                            get_current_response_time_percentile(percentile)
        print("Average response time: " + str(avg_response_time))

        # Send average response time to cluster manager
        if isinstance(avg_response_time, float):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                try:
                    server_socket.connect((swarm_manager_ip, autoscaler_port))
                    server_socket.send(str(avg_response_time).encode())
                    print("Sent to swarm manager: " + str(avg_response_time))
                except:
                    print("Cannot connect to swarm manager")

        gevent.sleep(sample_time)

# -- User simulator --
class AutoScaleUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://" + swarm_manager_ip + ":" + str(web_app_port)

    @task
    def workload(self):
        self.client.get('/')

# Swarm web app with "users"
env = Environment(user_classes=[AutoScaleUser])
runner = env.create_local_runner()
web_ui = env.create_web_ui("127.0.0.1", 8089)
runner.start(1,1)

# Start monitoring average response time
gevent.spawn(update_avg_response_time(env))
