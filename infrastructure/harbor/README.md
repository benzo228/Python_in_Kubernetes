# Harbor - Приватный Docker Registry

Этот каталог содержит конфигурацию для развертывания [Harbor](https://goharbor.io/) в локальном кластере Kubernetes (Minikube). Harbor используется как приватный реестр для хранения Docker-образов нашего приложения.

## Предварительные требования

Перед развертыванием убедитесь, что у вас установлены:
*   `kubectl` (настроенный на ваш кластер Minikube)
*   `helm` (версия 3.8+)

## Структура

*   `harbor_helm/` — Helm-чарт Harbor (скачанная версия).
*   `harbor-values.yaml` — Файл конфигурации с настройками для локальной среды (порты, ресурсы, отключение TLS).

## Развертывание

Выполните следующие команды из **корня этого каталога** (`infrastructure/harbor`):

1.  **Убедитесь, что старый релиз удален (если есть):**
    ```bash
    helm uninstall harbor -n harbor

2. **Разверните Harbor:**

helm upgrade --install harbor ./harbor_helm -n harbor --create-namespace -f harbor-values.yaml --wait

3. **Дождитесь, пока все поды перейдут в статус Running:**

kubectl get pods -n harbor -w

4. **Доступ к веб-интерфейсу**

kubectl port-forward svc/harbor -n harbor 8081:30002

Откройте в браузере: http://localhost:8081

Логин: admin
Пароль: Harbor12345 (указан в harbor-values.yaml)