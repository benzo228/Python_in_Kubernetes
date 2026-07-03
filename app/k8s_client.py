import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def get_pods(namespace: str = "default"):
    """
    Возвращает список подов в указанном namespace.
    Если запущено внутри кластера — использует in-cluster config,
    иначе пытается загрузить kubeconfig.
    """
    try:
        # Пытаемся загрузить конфиг из кластера (работает в Pod'е)
        config.load_incluster_config()
    except config.ConfigException:
        # Если не получилось — загружаем из ~/.kube/config (локальная разработка)
        config.load_kube_config()

    v1 = client.CoreV1Api()
    try:
        pods = v1.list_namespaced_pod(namespace)
        return [{"name": pod.metadata.name, "status": pod.status.phase} for pod in pods.items]
    except ApiException as e:
        return {"error": f"Kubernetes API error: {e.status} - {e.reason}"}