# Jenkins Docker Permission Denied

Tags: #jenkins #docker #ci-cd

Related: [[Kubernetes CrashLoopBackOff]]

## Symptom

A Jenkins build fails while running Docker commands with a permission denied error.

## Confirmed Facts

- Docker access depends on the Jenkins agent model.
- Long-lived agents may need group membership or socket permissions.
- Containerized agents need explicit Docker socket or remote builder configuration.

## Checks

```bash
whoami
id
docker version
ls -l /var/run/docker.sock
```

## Safer Fix Order

1. Confirm the intended runner model.
2. Prefer a dedicated build agent or remote builder.
3. Limit Docker socket exposure to jobs that require it.
4. Avoid broad host mounts in shared CI workers.

## Notes

- Treat access to the Docker socket as privileged host access.
- Do not print registry credentials in pipeline logs.
