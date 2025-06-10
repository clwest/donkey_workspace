from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def list_assistants(self):
        self.client.get("/api/assistants/")
