from django.urls import include, path
from rest_framework import routers
from rest_framework_jwt.views import verify_jwt_token

from .views import TaskViewSet, GoogleLogin

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"tasks", TaskViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("rest-auth/", include("rest_auth.urls")),
    path("rest-auth/verify/", verify_jwt_token),
    path("rest-auth/registration/", include("rest_auth.registration.urls")),
    path("rest-auth/google/", GoogleLogin.as_view(), name="google_login"),
]
