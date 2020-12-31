from api.models import Task
from django.contrib.auth.models import User
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_auth import *

from .views import GoogleLogin

# Create your tests here.
class AuthenticationTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("rest-auth/", include("rest_auth.urls")),
        path("rest-auth/registration/", include("rest_auth.registration.urls")),
    ]

    def setUp(self):
        super()
        self.test_email = "example@example.com"
        self.test_password = "password"
        User.objects.create_user(
            username=self.test_email,
            email=self.test_email,
            password=self.test_password,
        )

    def test_login_account_success(self):
        """
        Ensure we can login to newly created account
        """
        url = reverse("rest_login")
        data = {
            "username": self.test_email,
            "email": self.test_email,
            "password": self.test_password,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, self.test_email)

    def test_login_account_failed(self):
        """
        Check for missing field
        """
        url = reverse("rest_login")
        data = {
            "email": self.test_email,
            "password": self.test_password,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_account_success(self):
        """
        Ensure we can register new account
        """
        url = reverse("rest_register")
        test_email = "example2@example.com"
        test_password = "password"
        data = {
            "username": test_email,
            "email": test_email,
            "password1": test_password,
            "password2": test_password,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(id=2).username, test_email)

    def test_register_account_already_exists(self):
        """
        Ensure we can only register with unique email
        """
        url = reverse("rest_register")
        data = {
            "username": self.test_email,
            "email": self.test_email,
            "password1": self.test_password,
            "password2": self.test_password,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path("", include("api.urls")),
    ]

    def setUp(self) -> None:
        test_email = "example@example.com"
        test_second_email = "example1@example.com"
        test_password = "password"
        self.test_user = User.objects.create_user(
            username=test_email,
            email=test_email,
            password=test_password,
        )
        self.test_second_user = User.objects.create_user(
            username=test_second_email,
            email=test_second_email,
            password=test_password,
        )
        self.client.force_login(self.test_user)

        self.test_title = "Testing"
        self.test_description = "Testing Description"
        self.test_date = "2020-12-31"

        self.test_task = Task.objects.create(
            title=self.test_title, owner=self.test_user
        )
        self.test_update_task = Task.objects.create(
            title=self.test_title + "1", owner=self.test_user
        )
        return super().setUp()

    def test_create_task_success(self):
        """
        Ensure we can create new task
        """
        url = reverse("task-list")
        data = {
            "title": self.test_title,
            "description": self.test_description,
            "date": self.test_date,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], self.test_title)
        self.assertEqual(response.json()["owner"], self.test_user.email)

    def test_create_task_missing_field(self):
        """
        Ensure needed field are validated before create new task
        """
        url = reverse("task-list")
        data = {
            "description": self.test_description,
            "date": self.test_date,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_list_task_success(self):
        """
        Ensure we can read all task
        """
        url = reverse("task-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_read_list_task_owned_by_self(self):
        """
        Ensure we can only read all task owned by ourself
        """
        url = reverse("task-list")
        self.client.force_login(self.test_second_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_read_task_success(self):
        """
        Ensure we can read a task
        """
        url = reverse("task-detail", args=[self.test_task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_read_task_owned_by_self(self):
        """
        Ensure we can only read a task owned by ourself
        """
        url = reverse("task-detail", args=[self.test_task.id])
        self.client.force_login(self.test_second_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task_success(self):
        """
        Ensure we can update a task
        """
        url = reverse("task-detail", args=[self.test_update_task.id])
        data = {
            "title": self.test_title + "2",
            "description": self.test_description,
            "date": self.test_date,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], self.test_title + "2")

    def test_update_task_missing_fields(self):
        """
        Ensure needed field are validated before update a task
        """
        url = reverse("task-detail", args=[self.test_update_task.id])
        data = {
            "description": self.test_description,
            "date": self.test_date,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_task_success(self):
        """
        Ensure we can delete a task
        """
        url = reverse("task-detail", args=[self.test_update_task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_task_not_found(self):
        """
        Ensure we check for task before delete a task
        """
        url = reverse("task-detail", args=[self.test_update_task.id])
        self.client.delete(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
