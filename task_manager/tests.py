# NOSONAR - тестовые учетные данные

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase

from task_manager import constants
from task_manager.models import Label, Status, Task

# NOSONAR - тестовые учетные данные


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="testpass123",  # NOSONAR
            first_name="Test",
            last_name="User1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpass123",  # NOSONAR
            first_name="Test",
            last_name="User2",
        )
        self.admin = User.objects.create_superuser(
            username="adminuser",
            password="testpass123",  # NOSONAR
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
        )


class UserRegistrationTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.register_url = "/users/create/"

    def test_user_registration_page_status_code(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_user_registration_success(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "password1": "testpass123",  # NOSONAR
                "password2": "testpass123",  # NOSONAR
            },
        )

        self.assertRedirects(response, "/login/")
        self.assertTrue(User.objects.filter(username="newuser").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn(constants.SUCCESS_REGISTRATION, str(messages[0]))

    def test_user_registration_password_mismatch(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "password1": "pass123",  # NOSONAR
                "password2": "pass456",  # NOSONAR
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/registration.html")
        self.assertFalse(User.objects.filter(username="newuser").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_PWD_MISMATCH in str(msg) for msg in messages)
        )

    def test_user_registration_short_password(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "password1": "12",  # NOSONAR
                "password2": "12",  # NOSONAR
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_PWD_SHORT in str(msg) for msg in messages)
        )

    def test_user_registration_duplicate_username(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "testuser1",
                "password1": "newpass123",  # NOSONAR
                "password2": "newpass123",  # NOSONAR
            },
        )

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_USERNAME_EXISTS in str(msg) for msg in messages)
        )


class UserLoginTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = "/login/"

    def test_login_page_status_code(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "testuser1",
                "password": "testpass123",  # NOSONAR
            },
        )

        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {"username": "testuser1", "password": "wrongpass"},  # NOSONAR
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.ERROR_INVALID_CREDENTIALS in str(msg)
                for msg in messages
            )
        )

    def test_login_nonexistent_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "nonexistent",
                "password": "pass123",  # NOSONAR
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


# NOSONAR
class UserUpdateTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.update_url = f"/users/{self.user1.id}/update/"

    def test_update_page_requires_login(self):
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f"/login/?next={self.update_url}")

    def test_update_page_status_code_authenticated(self):
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/user_update.html")

    def test_user_update_success(self):
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR
        response = self.client.post(
            self.update_url,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "username": "testuser1",
                "password1": "",  # NOSONAR
                "password2": "",  # NOSONAR
            },
        )

        self.assertRedirects(response, "/users/")

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "Updated")
        self.assertEqual(self.user1.last_name, "Name")

    def test_user_update_with_new_password(self): 
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR
        response = self.client.post(
            self.update_url,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "username": "testuser1",
                "password1": "newpass123",  # NOSONAR
                "password2": "newpass123",  # NOSONAR
            },
        )

        self.assertRedirects(response, "/users/")

        login_success = self.client.login(
            username="testuser1",
            password="testpass123",  # NOSONAR
        )
        self.assertFalse(login_success)

        login_success = self.client.login(
            username="testuser1",
            password="newpass123",  # NOSONAR
        )
        self.assertTrue(login_success)

    def test_user_update_unauthorized(self):
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR
        other_update_url = f"/users/{self.user2.id}/update/"
        response = self.client.get(other_update_url)

        self.assertRedirects(response, "/users/")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_NO_RIGHTS in str(msg) for msg in messages)
        )


class UserDeleteTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.delete_url = f"/users/{self.user1.id}/delete/"

    def test_delete_page_requires_login(self):
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, f"/login/?next={self.delete_url}")

    def test_delete_page_status_code_authenticated(self):
        self.client.login(
            username="testuser1",
            password="testpass123",  # NOSONAR
        )
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/user_delete.html")

    def test_user_delete_success(self):
        self.client.login(username="testuser1", password="testpass123") # NOSONAR
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, "/users/")
        self.assertFalse(User.objects.filter(id=self.user1.id).exists())

    def test_user_delete_unauthorized(self):
        self.client.login(username="testuser1", password="testpass123") # NOSONAR
        other_delete_url = f"/users/{self.user2.id}/delete/"
        response = self.client.post(other_delete_url)

        self.assertRedirects(response, "/users/")
        self.assertTrue(User.objects.filter(id=self.user2.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_NO_RIGHTS in str(msg) for msg in messages)
        )


class UserListViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.users_url = "/users/"

    def test_users_list_public_access(self):
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/users.html")

    def test_users_list_contains_all_users(self):
        response = self.client.get(self.users_url)
        self.assertEqual(len(response.context["users"]), 3)

    def test_users_list_contains_usernames(self):
        response = self.client.get(self.users_url)
        self.assertContains(response, "testuser1")
        self.assertContains(response, "testuser2")
        self.assertContains(response, "adminuser")

    def test_users_list_links(self):
        response = self.client.get(self.users_url)
        self.assertContains(response, f"/users/{self.user1.id}/update/")
        self.assertContains(response, f"/users/{self.user1.id}/delete/")
        self.assertContains(response, f"/users/{self.user2.id}/update/")
        self.assertContains(response, f"/users/{self.user2.id}/delete/")


class AdminUserTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="adminuser", password="testpass123") # NOSONAR

    def test_admin_can_edit_any_user(self):
        update_url = f"/users/{self.user1.id}/update/"
        response = self.client.get(update_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            update_url,
            {
                "first_name": "AdminEdited",
                "last_name": "User",
                "username": self.user1.username,
                "password1": "",  # NOSONAR
                "password2": "",  # NOSONAR
            },
        )

        self.assertRedirects(response, "/users/")
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "AdminEdited")

    def test_admin_can_delete_any_user(self):
        delete_url = f"/users/{self.user1.id}/delete/"
        response = self.client.post(delete_url)

        self.assertRedirects(response, "/users/")
        self.assertFalse(User.objects.filter(id=self.user1.id).exists())


class LogoutTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.logout_url = "/logout/"
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR

    def test_logout_post(self):
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_LOGOUT in str(msg) for msg in messages)
        )

    def test_logout_get(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class StatusModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.status = Status.objects.create(name="Test Status")

    def test_status_creation(self):
        self.assertEqual(self.status.name, "Test Status")
        self.assertIsNotNone(self.status.created_at)

    def test_status_str(self):
        self.assertEqual(str(self.status), "Test Status")


class LabelModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.label = Label.objects.create(name="Test Label")

    def test_label_creation(self):
        self.assertEqual(self.label.name, "Test Label")
        self.assertIsNotNone(self.label.created_at)

    def test_label_str(self):
        self.assertEqual(str(self.label), "Test Label")


class TaskModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.status = Status.objects.create(name="Test Status")
        self.label1 = Label.objects.create(name="Label 1")
        self.label2 = Label.objects.create(name="Label 2")

        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            status=self.status,
            author=self.user1,
            executor=self.user2,
        )
        self.task.labels.set([self.label1, self.label2])

    def test_task_creation(self):
        self.assertEqual(self.task.name, "Test Task")
        self.assertEqual(self.task.description, "Test Description")
        self.assertEqual(self.task.status, self.status)
        self.assertEqual(self.task.author, self.user1)
        self.assertEqual(self.task.executor, self.user2)
        self.assertEqual(self.task.labels.count(), 2)

    def test_task_str(self):
        self.assertEqual(str(self.task), "Test Task")


class StatusCRUDTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR
        self.status = Status.objects.create(name="Test Status")
        self.statuses_url = "/statuses/"
        self.status_create_url = "/statuses/create/"
        self.status_update_url = f"/statuses/{self.status.id}/update/"
        self.status_delete_url = f"/statuses/{self.status.id}/delete/"

    def test_status_list_view_authenticated(self):
        """Тест: список статусов доступен авторизованному пользователю"""
        response = self.client.get(self.statuses_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/statuses.html")
        self.assertContains(response, "Test Status")

    def test_status_list_view_unauthenticated(self):
        """Тест: неавторизованный пользователь перенаправляется на логин"""
        self.client.logout()
        response = self.client.get(self.statuses_url)
        self.assertRedirects(response, f"/login/?next={self.statuses_url}")

    def test_status_create_view_get(self):
        """Тест: форма создания статуса доступна"""
        response = self.client.get(self.status_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/status_create.html")

    def test_status_create_success(self):
        """Тест: успешное создание статуса"""
        response = self.client.post(
            self.status_create_url, {"name": "New Status"}
        )

        self.assertRedirects(response, "/statuses/")
        self.assertTrue(Status.objects.filter(name="New Status").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.SUCCESS_STATUS_CREATED in str(msg) for msg in messages
            )
        )

    def test_status_create_duplicate(self):
        """Тест: создание статуса с существующим именем"""
        response = self.client.post(
            self.status_create_url, {"name": "Test Status"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/status_create.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_STATUS_EXISTS in str(msg) for msg in messages)
        )

    def test_status_create_empty_name(self):
        """Тест: создание статуса с пустым именем"""
        response = self.client.post(self.status_create_url, {"name": ""})

        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_NAME_REQUIRED in str(msg) for msg in messages)
        )

    def test_status_update_view_get(self):
        """Тест: форма редактирования статуса доступна"""
        response = self.client.get(self.status_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/status_update.html")
        self.assertContains(response, "Test Status")

    def test_status_update_success(self):
        """Тест: успешное обновление статуса"""
        response = self.client.post(
            self.status_update_url, {"name": "Updated Status"}
        )

        self.assertRedirects(response, "/statuses/")
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "Updated Status")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.SUCCESS_STATUS_UPDATED in str(msg) for msg in messages
            )
        )

    def test_status_update_duplicate(self):
        """Тест: обновление статуса на существующее имя"""
        Status.objects.create(name="Another Status")

        response = self.client.post(
            self.status_update_url, {"name": "Another Status"}
        )

        self.assertEqual(response.status_code, 200)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "Test Status")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_STATUS_EXISTS in str(msg) for msg in messages)
        )

    def test_status_delete_view_get(self):
        """Тест: страница подтверждения удаления доступна"""
        response = self.client.get(self.status_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses/status_delete.html")
        self.assertContains(response, "Test Status")

    def test_status_delete_success(self):
        """Тест: успешное удаление статуса без задач"""
        response = self.client.post(self.status_delete_url)

        self.assertRedirects(response, "/statuses/")
        self.assertFalse(Status.objects.filter(id=self.status.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.SUCCESS_STATUS_DELETED in str(msg) for msg in messages
            )
        )

    def test_status_delete_with_tasks(self):
        """Тест: нельзя удалить статус, связанный с задачами"""
        Task.objects.create(
            name="Test Task", status=self.status, author=self.user1
        )

        response = self.client.post(self.status_delete_url)

        self.assertRedirects(response, "/statuses/")
        self.assertTrue(Status.objects.filter(id=self.status.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.ERROR_CANNOT_DELETE_STATUS in str(msg)
                for msg in messages
            )
        )

    def test_status_list_requires_login(self):
        """Тест: все view статусов требуют авторизации"""
        self.client.logout()

        urls = [
            "/statuses/",
            "/statuses/create/",
            f"/statuses/{self.status.id}/update/",
            f"/statuses/{self.status.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={url}")


class StatusPermissionTest(BaseTestCase):
    def test_unauthenticated_user_cannot_access_status_pages(self):
        """Тест: неавторизованный пользователь не может зайти на
        страницы статусов"""
        urls = [
            "/statuses/",
            "/statuses/create/",
            "/statuses/1/update/",
            "/statuses/1/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={url}")

    def test_authenticated_user_can_access_status_pages(self):
        """Тест: авторизованный пользователь может зайти на страницы статусов"""
        self.client.login(username="testuser1", password="testpass123") # NOSONAR
        status = Status.objects.create(name="Test Status")

        urls = [
            "/statuses/",
            "/statuses/create/",
            f"/statuses/{status.id}/update/",
            f"/statuses/{status.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class UserDeleteWithTasksTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.status = Status.objects.create(name="Test Status")

        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            status=self.status,
            author=self.user1,
            executor=self.user2,
        )

    def test_cannot_delete_user_with_authored_tasks(self):
        """Тест: нельзя удалить пользователя, который является автором задач"""
        self.client.login(username="testuser1", password="testpass123") # NOSONAR
        delete_url = f"/users/{self.user1.id}/delete/"

        response = self.client.post(delete_url)

        self.assertRedirects(response, "/users/")
        self.assertTrue(User.objects.filter(id=self.user1.id).exists())

        messages = list(get_messages(response.wsgi_request))
        message_text = " ".join([str(msg) for msg in messages])
        self.assertIn(constants.ERROR_CANNOT_DELETE_USER, message_text)

    def test_cannot_delete_user_with_executed_tasks(self):
        """Тест: нельзя удалить пользователя, который является 
        исполнителем задач"""
        self.client.login(username="testuser2", password="testpass123") # NOSONAR
        delete_url = f"/users/{self.user2.id}/delete/"

        response = self.client.post(delete_url)

        self.assertRedirects(response, "/users/")
        self.assertTrue(User.objects.filter(id=self.user2.id).exists())

        messages = list(get_messages(response.wsgi_request))
        message_text = " ".join([str(msg) for msg in messages])
        self.assertIn(constants.ERROR_CANNOT_DELETE_USER, message_text)

    def test_admin_can_delete_user_with_tasks(self):
        """Тест: админ НЕ может удалить пользователя с задачами"""
        self.client.login(username="adminuser", password="testpass123") # NOSONAR
        delete_url = f"/users/{self.user1.id}/delete/"

        response = self.client.post(delete_url)

        self.assertRedirects(response, "/users/")
        self.assertTrue(User.objects.filter(id=self.user1.id).exists())

        messages = list(get_messages(response.wsgi_request))
        message_text = " ".join([str(msg) for msg in messages])
        self.assertIn(constants.ERROR_CANNOT_DELETE_USER, message_text)


class TaskCRUDTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR

        self.status = Status.objects.create(name="Test Status")
        self.label1 = Label.objects.create(name="Label 1")
        self.label2 = Label.objects.create(name="Label 2")

        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            status=self.status,
            author=self.user1,
            executor=self.user2,
        )
        self.task.labels.set([self.label1])

        self.tasks_url = "/tasks/"
        self.task_create_url = "/tasks/create/"
        self.task_detail_url = f"/tasks/{self.task.id}/"
        self.task_update_url = f"/tasks/{self.task.id}/update/"
        self.task_delete_url = f"/tasks/{self.task.id}/delete/"

    def test_task_list_view_authenticated(self):
        """Тест: список задач доступен авторизованному пользователю"""
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/tasks.html")
        self.assertContains(response, "Test Task")

    def test_task_list_view_unauthenticated(self):
        """Тест: неавторизованный пользователь перенаправляется на логин"""
        self.client.logout()
        response = self.client.get(self.tasks_url)
        self.assertRedirects(response, f"/login/?next={self.tasks_url}")

    def test_task_create_view_get(self):
        """Тест: форма создания задачи доступна"""
        response = self.client.get(self.task_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_create.html")
        self.assertContains(response, "Test Status")
        self.assertContains(response, "Label 1")
        self.assertContains(response, "Label 2")

    def test_task_create_success(self):
        """Тест: успешное создание задачи"""
        response = self.client.post(
            self.task_create_url,
            {
                "name": "New Task",
                "description": "New Description",
                "status": self.status.id,
                "executor": self.user2.id,
                "labels": [self.label1.id, self.label2.id],
            },
        )

        self.assertRedirects(response, "/tasks/")

        task = Task.objects.get(name="New Task")
        self.assertEqual(task.description, "New Description")
        self.assertEqual(task.status, self.status)
        self.assertEqual(task.author, self.user1)
        self.assertEqual(task.executor, self.user2)
        self.assertEqual(task.labels.count(), 2)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_TASK_CREATED in str(msg) for msg in messages)
        )

    def test_task_create_without_executor(self):
        """Тест: создание задачи без исполнителя"""
        response = self.client.post(
            self.task_create_url,
            {
                "name": "New Task",
                "description": "New Description",
                "status": self.status.id,
                "executor": "",
                "labels": [],
            },
        )

        self.assertRedirects(response, "/tasks/")

        task = Task.objects.get(name="New Task")
        self.assertIsNone(task.executor)
        self.assertEqual(task.labels.count(), 0)

    def test_task_create_without_name(self):
        """Тест: создание задачи без имени"""
        response = self.client.post(
            self.task_create_url,
            {
                "name": "",
                "description": "New Description",
                "status": self.status.id,
                "executor": "",
            },
        )

        self.assertRedirects(response, "/tasks/create/")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_NAME_REQUIRED in str(msg) for msg in messages)
        )

    def test_task_create_without_status(self):
        """Тест: создание задачи без статуса"""
        response = self.client.post(
            self.task_create_url,
            {
                "name": "New Task",
                "description": "New Description",
                "status": "",
                "executor": "",
            },
        )

        self.assertRedirects(response, "/tasks/create/")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_STATUS_REQUIRED in str(msg) for msg in messages)
        )

    def test_task_detail_view(self):
        """Тест: просмотр задачи"""
        response = self.client.get(self.task_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_detail.html")
        self.assertContains(response, "Test Task")
        self.assertContains(response, "Test Description")
        self.assertContains(response, "Test Status")
        self.assertContains(response, "Label 1")

    def test_task_update_view_get(self):
        """Тест: форма редактирования задачи доступна"""
        response = self.client.get(self.task_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_update.html")
        self.assertContains(response, "Test Task")
        self.assertContains(response, "Test Status")

    def test_task_update_success(self):
        """Тест: успешное обновление задачи"""
        response = self.client.post(
            self.task_update_url,
            {
                "name": "Updated Task",
                "description": "Updated Description",
                "status": self.status.id,
                "executor": self.user1.id,
                "labels": [self.label2.id],
            },
        )

        self.assertRedirects(response, "/tasks/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Updated Task")
        self.assertEqual(self.task.description, "Updated Description")
        self.assertEqual(self.task.executor, self.user1)
        self.assertEqual(self.task.labels.count(), 1)
        self.assertEqual(self.task.labels.first(), self.label2)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_TASK_UPDATED in str(msg) for msg in messages)
        )

    def test_task_update_by_non_author(self):
        """Тест: не автор не может редактировать задачу"""
        self.client.logout()
        self.client.login(username="testuser2", password="testpass123")  # NOSONAR

        response = self.client.get(self.task_update_url)
        self.assertRedirects(response, "/tasks/")

        response = self.client.post(
            self.task_update_url,
            {
                "name": "Hacked Task",
                "description": "Hacked Description",
                "status": self.status.id,
            },
        )

        self.assertRedirects(response, "/tasks/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.name, "Test Task")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.ERROR_TASK_EDIT_RIGHTS in str(msg) for msg in messages
            )
        )

    def test_task_delete_view_get(self):
        """Тест: страница подтверждения удаления доступна автору"""
        response = self.client.get(self.task_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasks/task_delete.html")
        self.assertContains(response, "Test Task")

    def test_task_delete_success(self):
        """Тест: автор может удалить свою задачу"""
        response = self.client.post(self.task_delete_url)

        self.assertRedirects(response, "/tasks/")
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_TASK_DELETED in str(msg) for msg in messages)
        )

    def test_task_delete_by_non_author(self):
        """Тест: не автор не может удалить задачу"""
        self.client.logout()
        self.client.login(username="testuser2", password="testpass123")  # NOSONAR

        response = self.client.post(self.task_delete_url)

        self.assertRedirects(response, "/tasks/")
        self.assertTrue(Task.objects.filter(id=self.task.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.ERROR_TASK_DELETE_RIGHTS in str(msg)
                for msg in messages
            )
        )

    def test_task_filter_by_status(self):
        """Тест: фильтрация задач по статусу"""
        status2 = Status.objects.create(name="Another Status")
        Task.objects.create(
            name="Another Task", status=status2, author=self.user1
        )

        response = self.client.get(f"{self.tasks_url}?status={self.status.id}")
        self.assertContains(response, "Test Task")
        self.assertNotContains(response, "Another Task")

    def test_task_filter_by_executor(self):
        """Тест: фильтрация задач по исполнителю"""
        response = self.client.get(f"{self.tasks_url}?executor={self.user2.id}")
        self.assertContains(response, "Test Task")

    def test_task_filter_by_label(self):
        """Тест: фильтрация задач по метке"""
        response = self.client.get(f"{self.tasks_url}?label={self.label1.id}")
        self.assertContains(response, "Test Task")

    def test_task_filter_self_tasks(self):
        """Тест: фильтрация задач, где пользователь автор"""
        Task.objects.create(
            name="Other Task", status=self.status, author=self.user2
        )

        response = self.client.get(f"{self.tasks_url}?self_tasks=on")
        self.assertContains(response, "Test Task")
        self.assertNotContains(response, "Other Task")


class LabelCRUDTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR

        self.label = Label.objects.create(name="Test Label")

        self.labels_url = "/labels/"
        self.label_create_url = "/labels/create/"
        self.label_update_url = f"/labels/{self.label.id}/update/"
        self.label_delete_url = f"/labels/{self.label.id}/delete/"

    def test_label_list_view_authenticated(self):
        """Тест: список меток доступен авторизованному пользователю"""
        response = self.client.get(self.labels_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/labels.html")
        self.assertContains(response, "Test Label")

    def test_label_list_view_unauthenticated(self):
        """Тест: неавторизованный пользователь перенаправляется на логин"""
        self.client.logout()
        response = self.client.get(self.labels_url)
        self.assertRedirects(response, f"/login/?next={self.labels_url}")

    def test_label_create_view_get(self):
        """Тест: форма создания метки доступна"""
        response = self.client.get(self.label_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/label_create.html")

    def test_label_create_success(self):
        """Тест: успешное создание метки"""
        response = self.client.post(
            self.label_create_url, {"name": "New Label"}
        )

        self.assertRedirects(response, "/labels/")
        self.assertTrue(Label.objects.filter(name="New Label").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_LABEL_CREATED in str(msg) for msg in messages)
        )

    def test_label_create_duplicate(self):
        """Тест: создание метки с существующим именем"""
        response = self.client.post(
            self.label_create_url, {"name": "Test Label"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/label_create.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_LABEL_EXISTS in str(msg) for msg in messages)
        )

    def test_label_create_empty_name(self):
        """Тест: создание метки с пустым именем"""
        response = self.client.post(self.label_create_url, {"name": ""})

        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_NAME_REQUIRED in str(msg) for msg in messages)
        )

    def test_label_update_view_get(self):
        """Тест: форма редактирования метки доступна"""
        response = self.client.get(self.label_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/label_update.html")
        self.assertContains(response, "Test Label")

    def test_label_update_success(self):
        """Тест: успешное обновление метки"""
        response = self.client.post(
            self.label_update_url, {"name": "Updated Label"}
        )

        self.assertRedirects(response, "/labels/")
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "Updated Label")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_LABEL_UPDATED in str(msg) for msg in messages)
        )

    def test_label_update_duplicate(self):
        """Тест: обновление метки на существующее имя"""
        Label.objects.create(name="Another Label")

        response = self.client.post(
            self.label_update_url, {"name": "Another Label"}
        )

        self.assertEqual(response.status_code, 200)
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, "Test Label")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.ERROR_LABEL_EXISTS in str(msg) for msg in messages)
        )

    def test_label_delete_view_get(self):
        """Тест: страница подтверждения удаления доступна"""
        response = self.client.get(self.label_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "labels/label_delete.html")
        self.assertContains(response, "Test Label")

    def test_label_delete_success(self):
        """Тест: успешное удаление метки без задач"""
        response = self.client.post(self.label_delete_url)

        self.assertRedirects(response, "/labels/")
        self.assertFalse(Label.objects.filter(id=self.label.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(constants.SUCCESS_LABEL_DELETED in str(msg) for msg in messages)
        )

    def test_label_delete_with_tasks(self):
        """Тест: нельзя удалить метку, связанную с задачами"""
        status = Status.objects.create(name="Test Status")
        task = Task.objects.create(
            name="Test Task", status=status, author=self.user1
        )
        task.labels.add(self.label)

        response = self.client.post(self.label_delete_url)

        self.assertRedirects(response, "/labels/")
        self.assertTrue(Label.objects.filter(id=self.label.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                constants.ERROR_CANNOT_DELETE_LABEL in str(msg)
                for msg in messages
            )
        )

    def test_label_list_requires_login(self):
        """Тест: все view меток требуют авторизации"""
        self.client.logout()

        urls = [
            "/labels/",
            "/labels/create/",
            f"/labels/{self.label.id}/update/",
            f"/labels/{self.label.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={url}")


class LabelInTaskTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR

        self.status = Status.objects.create(name="Test Status")
        self.label1 = Label.objects.create(name="Label 1")
        self.label2 = Label.objects.create(name="Label 2")

        self.task = Task.objects.create(
            name="Test Task",
            description="Test Description",
            status=self.status,
            author=self.user1,
        )
        self.task.labels.set([self.label1, self.label2])

    def test_task_has_labels(self):
        """Тест: задача имеет метки"""
        self.assertEqual(self.task.labels.count(), 2)
        self.assertIn(self.label1, self.task.labels.all())
        self.assertIn(self.label2, self.task.labels.all())

    def test_task_create_with_labels(self):
        """Тест: создание задачи с метками"""
        response = self.client.post(
            "/tasks/create/",
            {
                "name": "New Task",
                "description": "New Description",
                "status": self.status.id,
                "executor": "",
                "labels": [self.label1.id, self.label2.id],
            },
        )

        self.assertRedirects(response, "/tasks/")

        task = Task.objects.get(name="New Task")
        self.assertEqual(task.labels.count(), 2)

    def test_task_update_with_labels(self):
        """Тест: обновление задачи с метками"""
        update_url = f"/tasks/{self.task.id}/update/"

        response = self.client.post(
            update_url,
            {
                "name": "Updated Task",
                "description": "Updated Description",
                "status": self.status.id,
                "executor": "",
                "labels": [self.label1.id],
            },
        )

        self.assertRedirects(response, "/tasks/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.labels.count(), 1)
        self.assertEqual(self.task.labels.first(), self.label1)

    def test_task_update_without_labels(self):
        """Тест: обновление задачи без меток"""
        update_url = f"/tasks/{self.task.id}/update/"

        response = self.client.post(
            update_url,
            {
                "name": "Updated Task",
                "description": "Updated Description",
                "status": self.status.id,
                "executor": "",
                "labels": [],
            },
        )

        self.assertRedirects(response, "/tasks/")

        self.task.refresh_from_db()
        self.assertEqual(self.task.labels.count(), 0)

    def test_task_create_form_has_labels(self):
        """Тест: форма создания задачи содержит список меток"""
        response = self.client.get("/tasks/create/")
        self.assertContains(response, "Label 1")
        self.assertContains(response, "Label 2")
        self.assertContains(response, "multiple")

    def test_task_update_form_has_labels_with_selected(self):
        """Тест: форма редактирования задачи содержит выбранные метки"""
        update_url = f"/tasks/{self.task.id}/update/"
        response = self.client.get(update_url)

        self.assertContains(response, "Label 1")
        self.assertContains(response, "Label 2")
        self.assertContains(response, "selected")


class LabelPermissionTest(BaseTestCase):
    def test_unauthenticated_user_cannot_access_label_pages(self):
        """Тест: неавторизованный пользователь не может зайти на
        страницы меток"""
        urls = [
            "/labels/",
            "/labels/create/",
            "/labels/1/update/",
            "/labels/1/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"/login/?next={url}")

    def test_authenticated_user_can_access_label_pages(self):
        """Тест: авторизованный пользователь может зайти на страницы меток"""
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR
        label = Label.objects.create(name="Test Label")

        urls = [
            "/labels/",
            "/labels/create/",
            f"/labels/{label.id}/update/",
            f"/labels/{label.id}/delete/",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)


class TaskFilterTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="testuser1", password="testpass123")  # NOSONAR

        self.status1 = Status.objects.create(name="Status 1")
        self.status2 = Status.objects.create(name="Status 2")

        self.label1 = Label.objects.create(name="Label 1")
        self.label2 = Label.objects.create(name="Label 2")
        self.label3 = Label.objects.create(name="Label 3")

        self.task1 = Task.objects.create(
            name="Task 1",
            description="Description 1",
            status=self.status1,
            author=self.user1,
            executor=self.user2,
        )
        self.task1.labels.set([self.label1, self.label2])

        self.task2 = Task.objects.create(
            name="Task 2",
            description="Description 2",
            status=self.status2,
            author=self.user2,
            executor=self.user1,
        )
        self.task2.labels.set([self.label2, self.label3])

        self.task3 = Task.objects.create(
            name="Task 3",
            description="Description 3",
            status=self.status1,
            author=self.user1,
            executor=None,
        )
        self.task3.labels.set([self.label1])

        self.task4 = Task.objects.create(
            name="Task 4",
            description="Description 4",
            status=self.status2,
            author=self.admin,
            executor=self.user2,
        )
        self.task4.labels.set([self.label3])

        self.tasks_url = "/tasks/"

    def test_filter_by_status(self):
        """Тест: фильтрация задач по статусу"""
        response = self.client.get(f"{self.tasks_url}?status={self.status1.id}")
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 3")
        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Task 4")

        response = self.client.get(f"{self.tasks_url}?status={self.status2.id}")
        self.assertContains(response, "Task 2")
        self.assertContains(response, "Task 4")
        self.assertNotContains(response, "Task 1")
        self.assertNotContains(response, "Task 3")

    def test_filter_by_executor(self):
        """Тест: фильтрация задач по исполнителю"""
        response = self.client.get(f"{self.tasks_url}?executor={self.user2.id}")
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 4")
        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Task 3")

        response = self.client.get(f"{self.tasks_url}?executor={self.user1.id}")
        self.assertContains(response, "Task 2")
        self.assertNotContains(response, "Task 1")
        self.assertNotContains(response, "Task 3")
        self.assertNotContains(response, "Task 4")

        response = self.client.get(f"{self.tasks_url}?executor=999")
        self.assertEqual(len(response.context["tasks"]), 0)

    def test_filter_by_label(self):
        """Тест: фильтрация задач по метке"""
        response = self.client.get(f"{self.tasks_url}?label={self.label1.id}")
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 3")
        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Task 4")

        response = self.client.get(f"{self.tasks_url}?label={self.label2.id}")
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 2")
        self.assertNotContains(response, "Task 3")
        self.assertNotContains(response, "Task 4")

        response = self.client.get(f"{self.tasks_url}?label={self.label3.id}")
        self.assertContains(response, "Task 2")
        self.assertContains(response, "Task 4")
        self.assertNotContains(response, "Task 1")
        self.assertNotContains(response, "Task 3")

    def test_filter_self_tasks(self):
        """Тест: фильтрация задач, где пользователь является автором"""
        response = self.client.get(f"{self.tasks_url}?self_tasks=on")
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 3")
        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Task 4")

        self.client.logout()
        self.client.login(username="testuser2", password="testpass123")  # NOSONAR
        response = self.client.get(f"{self.tasks_url}?self_tasks=on")
        self.assertContains(response, "Task 2")
        self.assertNotContains(response, "Task 1")
        self.assertNotContains(response, "Task 3")
        self.assertNotContains(response, "Task 4")

        self.client.logout()
        self.client.login(username="adminuser", password="testpass123")  # NOSONAR
        response = self.client.get(f"{self.tasks_url}?self_tasks=on")
        self.assertContains(response, "Task 4")
        self.assertNotContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")
        self.assertNotContains(response, "Task 3")

    def test_combined_filters(self):
        """Тест: комбинированная фильтрация"""
        response = self.client.get(
            f"{self.tasks_url}?status={self.status1.id}&self_tasks=on"
        )
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 3")
        self.assertEqual(len(response.context["tasks"]), 2)

        response = self.client.get(
            f"{self.tasks_url}?status={self.status1.id}&label={self.label1.id}"
        )
        self.assertContains(response, "Task 1")
        self.assertContains(response, "Task 3")
        self.assertEqual(len(response.context["tasks"]), 2)

        response = self.client.get(
            f"{self.tasks_url}?status={self.status2.id}&executor={self.user2.id}"
        )
        self.assertContains(response, "Task 4")
        self.assertNotContains(response, "Task 2")
        self.assertEqual(len(response.context["tasks"]), 1)

        response = self.client.get(
            f"{self.tasks_url}?label={self.label2.id}&self_tasks=on"
        )
        self.assertContains(response, "Task 1")
        self.assertNotContains(response, "Task 2")
        self.assertEqual(len(response.context["tasks"]), 1)

    def test_filter_with_no_results(self):
        """Тест: фильтр, не дающий результатов"""
        response = self.client.get(f"{self.tasks_url}?status=999")
        self.assertEqual(len(response.context["tasks"]), 0)

        response = self.client.get(f"{self.tasks_url}?label=999")
        self.assertEqual(len(response.context["tasks"]), 0)

        response = self.client.get(
            f"{self.tasks_url}?status={self.status1.id}&executor={self.admin.id}"
        )
        self.assertEqual(len(response.context["tasks"]), 0)

    def test_filter_preserves_selected_values(self):
        """Тест: форма фильтрации сохраняет выбранные значения"""
        response = self.client.get(
            f"{self.tasks_url}?status={self.status1.id}&self_tasks=on&label={self.label1.id}"
        )

        self.assertContains(
            response, f'<option value="{self.status1.id}" selected'
        )
        self.assertContains(response, "checked")
        self.assertContains(
            response, f'<option value="{self.label1.id}" selected'
        )

    def test_filter_form_display(self):
        """Тест: форма фильтрации отображается корректно"""
        response = self.client.get(self.tasks_url)

        self.assertContains(response, 'name="status"')
        self.assertContains(response, 'name="executor"')
        self.assertContains(response, 'name="label"')
        self.assertContains(response, 'name="self_tasks"')

        self.assertContains(response, "Status 1")
        self.assertContains(response, "Status 2")

        self.assertContains(response, "Test User1")
        self.assertContains(response, "Test User2")
        self.assertContains(response, "Admin User")

        self.assertContains(response, "Label 1")
        self.assertContains(response, "Label 2")
        self.assertContains(response, "Label 3")
