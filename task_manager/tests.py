from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from task_manager.models import Status, Label, Task


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем пользователей для тестов
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="testpass123",
            first_name="Test",
            last_name="User1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpass123",
            first_name="Test",
            last_name="User2",
        )
        self.admin = User.objects.create_superuser(
            username="adminuser",
            password="testpass123",
            first_name="Admin",
            last_name="User",
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
                "password1": "testpass123",
                "password2": "testpass123",
            },
        )

        self.assertRedirects(response, "/login/")
        self.assertTrue(User.objects.filter(username="newuser").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("Регистрация прошла успешно", str(messages[0]))

    def test_user_registration_password_mismatch(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "password1": "pass123",
                "password2": "pass456",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration.html")
        self.assertFalse(User.objects.filter(username="newuser").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Пароли не совпадают" in str(msg) for msg in messages))

    def test_user_registration_short_password(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "newuser",
                "password1": "12",
                "password2": "12",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("минимум 3 символа" in str(msg) for msg in messages))

    def test_user_registration_duplicate_username(self):
        response = self.client.post(
            self.register_url,
            {
                "first_name": "New",
                "last_name": "User",
                "username": "testuser1",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("уже существует" in str(msg) for msg in messages))


class UserLoginTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.login_url = "/login/"

    def test_login_page_status_code(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(
            self.login_url, {"username": "testuser1", "password": "testpass123"}
        )

        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url, {"username": "testuser1", "password": "wrongpass"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Неверное имя пользователя или пароль" in str(msg) for msg in messages)
        )

    def test_login_nonexistent_user(self):
        response = self.client.post(
            self.login_url, {"username": "nonexistent", "password": "pass123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserUpdateTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.update_url = f"/users/{self.user1.id}/update/"

    def test_update_page_requires_login(self):
        response = self.client.get(self.update_url)
        self.assertRedirects(response, f"/login/?next={self.update_url}")

    def test_update_page_status_code_authenticated(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(self.update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_update.html")

    def test_user_update_success(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.post(
            self.update_url,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "username": "testuser1",
                "password1": "",
                "password2": "",
            },
        )

        self.assertRedirects(response, "/users/")

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "Updated")
        self.assertEqual(self.user1.last_name, "Name")

    def test_user_update_with_new_password(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.post(
            self.update_url,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "username": "testuser1",
                "password1": "newpass123",
                "password2": "newpass123",
            },
        )

        self.assertRedirects(response, "/login/")

        # Проверяем, что старый пароль больше не работает
        login_success = self.client.login(username="testuser1", password="testpass123")
        self.assertFalse(login_success)

        # Проверяем, что можно войти с новым паролем
        login_success = self.client.login(username="testuser1", password="newpass123")
        self.assertTrue(login_success)

    def test_user_update_unauthorized(self):
        self.client.login(username="testuser1", password="testpass123")
        other_update_url = f"/users/{self.user2.id}/update/"
        response = self.client.get(other_update_url)

        self.assertRedirects(response, "/users/")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("нет прав" in str(msg) for msg in messages))


class UserDeleteTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.delete_url = f"/users/{self.user1.id}/delete/"

    def test_delete_page_requires_login(self):
        response = self.client.get(self.delete_url)
        self.assertRedirects(response, f"/login/?next={self.delete_url}")

    def test_delete_page_status_code_authenticated(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_delete.html")

    def test_user_delete_success(self):
        self.client.login(username="testuser1", password="testpass123")
        response = self.client.post(self.delete_url)

        self.assertRedirects(response, "/users/")
        self.assertFalse(User.objects.filter(id=self.user1.id).exists())

    def test_user_delete_unauthorized(self):
        self.client.login(username="testuser1", password="testpass123")
        other_delete_url = f"/users/{self.user2.id}/delete/"
        response = self.client.post(other_delete_url)

        self.assertRedirects(response, "/users/")
        self.assertTrue(User.objects.filter(id=self.user2.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("нет прав" in str(msg) for msg in messages))


class UserListViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.users_url = "/users/"

    def test_users_list_public_access(self):
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users.html")

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
        self.client.login(username="adminuser", password="testpass123")

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
                "password1": "",
                "password2": "",
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
        self.client.login(username="testuser1", password="testpass123")

    def test_logout_post(self):
        response = self.client.post(self.logout_url)
        self.assertRedirects(response, "/")
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("вышли из системы" in str(msg) for msg in messages))

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
        self.client.login(username="testuser1", password="testpass123")
        self.status = Status.objects.create(name="Test Status")
        self.statuses_url = "/statuses/"
        self.status_create_url = "/statuses/create/"
        self.status_update_url = f"/statuses/{self.status.id}/update/"
        self.status_delete_url = f"/statuses/{self.status.id}/delete/"

    def test_status_list_view_authenticated(self):
        """Тест: список статусов доступен авторизованному пользователю"""
        response = self.client.get(self.statuses_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "statuses.html")
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
        self.assertTemplateUsed(response, "status_create.html")

    def test_status_create_success(self):
        """Тест: успешное создание статуса"""
        response = self.client.post(self.status_create_url, {"name": "New Status"})

        self.assertRedirects(response, "/statuses/")
        self.assertTrue(Status.objects.filter(name="New Status").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("успешно создан" in str(msg) for msg in messages))

    def test_status_create_duplicate(self):
        """Тест: создание статуса с существующим именем"""
        response = self.client.post(self.status_create_url, {"name": "Test Status"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "status_create.html")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("уже существует" in str(msg) for msg in messages))

    def test_status_create_empty_name(self):
        """Тест: создание статуса с пустым именем"""
        response = self.client.post(self.status_create_url, {"name": ""})

        self.assertEqual(response.status_code, 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("обязательно" in str(msg) for msg in messages))

    def test_status_update_view_get(self):
        """Тест: форма редактирования статуса доступна"""
        response = self.client.get(self.status_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "status_update.html")
        self.assertContains(response, "Test Status")

    def test_status_update_success(self):
        """Тест: успешное обновление статуса"""
        response = self.client.post(self.status_update_url, {"name": "Updated Status"})

        self.assertRedirects(response, "/statuses/")
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "Updated Status")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("успешно изменен" in str(msg) for msg in messages))

    def test_status_update_duplicate(self):
        """Тест: обновление статуса на существующее имя"""
        Status.objects.create(name="Another Status")

        response = self.client.post(self.status_update_url, {"name": "Another Status"})

        self.assertEqual(response.status_code, 200)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, "Test Status")

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("уже существует" in str(msg) for msg in messages))

    def test_status_delete_view_get(self):
        """Тест: страница подтверждения удаления доступна"""
        response = self.client.get(self.status_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "status_delete.html")
        self.assertContains(response, "Test Status")

    def test_status_delete_success(self):
        """Тест: успешное удаление статуса без задач"""
        response = self.client.post(self.status_delete_url)

        self.assertRedirects(response, "/statuses/")
        self.assertFalse(Status.objects.filter(id=self.status.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("успешно удален" in str(msg) for msg in messages))

    def test_status_delete_with_tasks(self):
        """Тест: нельзя удалить статус, связанный с задачами"""
        # Создаем задачу с этим статусом
        task = Task.objects.create(
            name="Test Task", status=self.status, author=self.user1
        )

        response = self.client.post(self.status_delete_url)

        self.assertRedirects(response, "/statuses/")
        self.assertTrue(Status.objects.filter(id=self.status.id).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("используется в задачах" in str(msg) for msg in messages))

    def test_status_list_requires_login(self):
        """Тест: все view статусов требуют авторизации"""
        self.client.logout()

        # Проверяем все URL
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
        """Тест: неавторизованный пользователь не может зайти на страницы статусов"""
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
        self.client.login(username="testuser1", password="testpass123")
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
