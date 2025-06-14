from rest_framework.throttling import UserRateThrottle

class HeavyRateThrottle(UserRateThrottle):
    scope = "heavy"

    def throttle_success(self):
        self.remaining = max(self.num_requests - len(self.history), 0)
        return super().throttle_success()

    def throttle_failure(self):
        self.remaining = 0
        return super().throttle_failure()
