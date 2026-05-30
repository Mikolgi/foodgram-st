from locust import HttpUser, between, task


class FoodgramUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def recipes(self):
        self.client.get("/api/recipes/?page=1", name="GET /api/recipes/")

    @task(2)
    def ingredients(self):
        self.client.get("/api/ingredients/", name="GET /api/ingredients/")
