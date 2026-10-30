# Python Task Manager in Kubernetes 🚀

Пет-проект, демонстрирующий полный цикл разработки и деплоя приложения (FastAPI + PostgreSQL) в локальном Kubernetes-кластере с использованием GitOps-подхода.

## 🏗 Архитектура и стек

Проект разворачивается в локальном окружении и включает в себя следующие компоненты:

*   **Приложение:** Python 3.12, FastAPI, SQLAlchemy (async), Pydantic, JWT-авторизация.
*   **База данных:** PostgreSQL 15 (StatefulSet).
*   **Оркестратор:** Minikube (Kubernetes).
*   **CI/CD:** Локальный GitLab (Docker Compose) + GitLab Runner (в Minikube).
*   **Реестр образов:** Harbor (в Minikube).
*   **GitOps:** Argo CD (в Minikube).
*   **Сборка образов:** Kaniko (без Docker-in-Docker).

## 📂 Структура репозитория

```text
.
├── app/                  # Исходный код FastAPI приложения
│   ├── auth.py           # Логика JWT и хеширования паролей
│   ├── crud.py           # CRUD операции с БД
│   ├── database.py       # Подключение к PostgreSQL
│   ├── k8s_client.py     # Клиент для K8s API (вывод списка подов)
│   ├── main.py           # Точка входа, эндпоинты
│   ├── models.py         # SQLAlchemy модели (User, Task, Comment)
│   ├── schemas.py        # Pydantic схемы
│   └── templates/        # HTML фронтенд (Bootstrap)
├── infrastructure/       # Инфраструктурные конфигурации
│   ├── gitlab/           # Docker Compose для локального GitLab
│   └── harbor/           # Конфигурация Harbor (Helm)
├── k8s/                  # Kubernetes манифесты
│   ├── argocd/           # Манифест Application для Argo CD
│   ├── deployment.yaml   # Деплоймент приложения
│   ├── service.yaml      # Сервис приложения
│   ├── postgres-single.yaml # StatefulSet и Service для PostgreSQL
│   └── ...               # RBAC, ConfigMap и др.
├── .gitlab-ci.yml        # Пайплайн CI/CD
├── Dockerfile            # Многоступенчатая сборка приложения
└── sync_to_github.ps1    # Скрипт синхронизации с публичным GitHub
