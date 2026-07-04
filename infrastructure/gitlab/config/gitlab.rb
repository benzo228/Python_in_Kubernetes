prometheus_monitoring['enable'] = false
alertmanager['enable'] = false
node_exporter['enable'] = false
postgres_exporter['enable'] = false
redis_exporter['enable'] = false
gitlab_exporter['enable'] = false

sidekiq['max_concurrency'] = 10
sidekiq['min_concurrency'] = 5
puma['worker_processes'] = 0
puma['min_threads'] = 1
puma['max_threads'] = 4
postgresql['shared_buffers'] = "256MB"
postgresql['max_worker_processes'] = 4

logging['logrotate_frequency'] = "daily"
logging['logrotate_keep'] = 7

gitlab_rails['gitlab_ssh_host'] = 'localhost'
gitlab_rails['gitlab_ssh_port'] = 2224
