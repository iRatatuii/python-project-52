# URL константы
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"
USERS_URL = "/users/"
STATUSES_URL = "/statuses/"
LABELS_URL = "/labels/"
TASKS_URL = "/tasks/"

# Сообщения об ошибках
ERROR_NO_RIGHTS = "У вас нет прав для редактирования этого пользователя"
ERROR_CANNOT_DELETE_USER = (
    "Невозможно удалить пользователя, потому что он связан с задачами"
)
ERROR_CANNOT_DELETE_STATUS = (
    "Невозможно удалить статус, потому что он используется в задачах"
)
ERROR_CANNOT_DELETE_LABEL = (
    "Невозможно удалить метку, потому что она используется в задачах"
)
ERROR_TASK_DELETE_RIGHTS = "Задачу может удалить только ее автор"
ERROR_TASK_EDIT_RIGHTS = "Задачу может редактировать только ее автор"
ERROR_INVALID_CREDENTIALS = "Неверное имя пользователя или пароль"
ERROR_NAME_REQUIRED = "Имя обязательно"
ERROR_STATUS_REQUIRED = "Статус обязателен"
ERROR_PWD_MISMATCH = "Пароли не совпадают"  # NOSONAR
ERROR_PWD_SHORT = "Пароль должен содержать минимум 3 символа"  # NOSONAR
ERROR_USERNAME_EXISTS = "Пользователь с таким именем уже существует"
ERROR_STATUS_EXISTS = "Статус с таким именем уже существует"
ERROR_LABEL_EXISTS = "Метка с таким именем уже существует"

# Сообщения об успехе
SUCCESS_LOGIN = "Вы залогинены"
SUCCESS_LOGOUT = "Вы разлогинены"
SUCCESS_USER_UPDATED = "Пользователь успешно изменен"
SUCCESS_REGISTRATION = "Пользователь успешно зарегистрирован"
SUCCESS_USER_DELETED = "Пользователь успешно удален"
SUCCESS_STATUS_CREATED = "Статус успешно создан"
SUCCESS_STATUS_UPDATED = "Статус успешно изменен"
SUCCESS_STATUS_DELETED = "Статус успешно удален"
SUCCESS_LABEL_CREATED = "Метка успешно создана"
SUCCESS_LABEL_UPDATED = "Метка успешно изменена"
SUCCESS_LABEL_DELETED = "Метка успешно удалена"
SUCCESS_TASK_CREATED = "Задача успешно создана"
SUCCESS_TASK_UPDATED = "Задача успешно изменена"
SUCCESS_TASK_DELETED = "Задача успешно удалена"

# Константы для моделей (verbose names)
CREATED_AT_VERBOSE = "Дата создания"
NAME_VERBOSE = "Имя"
STATUS_VERBOSE = "Статус"
LABELS_VERBOSE = "Метки"
TASK_NAME_VERBOSE = "Имя"
TASK_DESCRIPTION_VERBOSE = "Описание"
AUTHOR_VERBOSE = "Автор"
EXECUTOR_VERBOSE = "Исполнитель"
