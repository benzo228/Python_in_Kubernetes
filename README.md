# Python_in_Kubernetes

my-pet-project/
├── app/
│   ├── __init__.py                  # Пустой файл, чтобы Python считал папку пакетом
│   ├── main.py                      # FastAPI приложение (входная точка)
│   ├── models.py                    # Pydantic-схемы для задач
│   ├── crud.py                      # CRUD-операции (сейчас in-memory хранилище)
│   ├── k8s_client.py                # Обёртка для работы с Kubernetes API (список подов)
│   └── templates/
│       └── index.html               # HTML-фронтенд (Bootstrap + Fetch API)
│
├── k8s/                             # Манифесты Kubernetes
│   ├── namespace.yaml               # Опционально, изолирует всё в неймспейс pet-project
│   ├── configmap.yaml               # Переменные окружения (порт и др.)
│   ├── service-account.yaml         # ServiceAccount + ClusterRole + ClusterRoleBinding для доступа к K8s API
│   ├── deployment.yaml              # Деплоймент приложения (2 реплики, пробросы здоровья, ресурсы)
│   ├── service.yaml                 # Сервис типа NodePort (порт 30080)
│   └── ingress.yaml                 # Опционально, если хочешь URL через Ingress (требует включенного Ingress-контроллера)
│
├── Dockerfile                       # Многоступенчатая сборка с использованием uv
├── requirements.txt                 # Список зависимостей (fastapi, uvicorn, kubernetes, jinja2, python-multipart)
├── .dockerignore                    # Исключает лишние файлы из сборки
├── .gitignore                       # Игнорирует временные файлы, __pycache__, .env и т.д.
└── README.md                        # Инструкция по запуску (локально и в K8s)
