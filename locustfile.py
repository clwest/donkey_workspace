from locust import HttpUser, task, between

class BasicLoadTest(HttpUser):
    wait_time = between(1, 5)

    @task
    def health(self):
        self.client.get("/health/")

    @task
    def list_assistants(self):
        self.client.get("/api/assistants/")
