from rest_framework.throttling import UserRateThrottle

class HeavyRateThrottle(UserRateThrottle):
    scope = "heavy"
