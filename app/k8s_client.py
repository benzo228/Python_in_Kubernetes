import logging

from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

def get_pods(namespace: str = "default"):
    """
    Возвращает список подов в указанном namespace.
    Если запущено внутри кластера — использует in-cluster config,
    иначе пытается загрузить kubeconfig.
    """
    try:
        # Пытаемся загрузить конфиг из кластера (работает в Pod'е)
        config.load_incluster_config()
        logger.info("Loaded in-cluster config")
    except config.ConfigException:
        # Если не получилось — загружаем из ~/.kube/config (локальная разработка)
        try:
            config.load_kube_config()
            logger.info("Loaded kubeconfig from file")
        except RuntimeError as e:  # <-- Исправлено с Exception
            logger.error(f"Failed to load kubeconfig: {e}")
            return {"error": f"Failed to load kubeconfig: {e!s}"}

    v1 = client.CoreV1Api()
    try:
        pods = v1.list_namespaced_pod(namespace)
        return [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods.items]
    except ApiException as e:
        logger.error(f"Kubernetes API error: {e.status} - {e.reason}")
        return {"error": f"Kubernetes API error: {e.status} - {e.reason}"}
    except RuntimeError as e:  # <-- Исправлено с Exception
        logger.error(f"Unexpected error: {e!s}")
        return {"error": f"Unexpected error: {e!s}"}