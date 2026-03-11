# HiveBox 🐝

A scalable RESTful API for beekeepers using openSenseMap data, built with DevSecOps best practices.

## Version

Current version: v0.0.1

## What is HiveBox?

HiveBox fetches temperature data from beehive-mounted sensors via openSenseMap API and exposes it through a REST API with caching, storage, and observability built-in.

## SenseBox IDs Used

- 5eba5fbad46fb8001b799786
- 5c21ff8f919bf8001adf2488
- 5ade1acf223bd80019a1011c

## Architecture

```
openSenseMap API → HiveBox App → Valkey (Cache)
                              → MinIO (Storage)
                              → Prometheus Metrics
                              → Grafana Cloud (Observability)
                              → ArgoCD (GitOps)
```

## How to Run

### Local

```bash
# Start Valkey and MinIO
docker run -d --name valkey -p 6379:6379 valkey/valkey:7.2
docker run -d --name minio -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  quay.io/minio/minio server /data --console-address ":9001"

# Run app
pip install -r requirements.txt
python src/app.py
```

### Docker

```bash
docker build -t hivebox:0.0.1 .
docker run -p 8080:8080 hivebox:0.0.1
```

### Kubernetes (KIND) — Local

```bash
# Create cluster
kind create cluster --name hivebox --config kind-config.yaml

# Install Ingress-Nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Deploy infrastructure (Valkey + MinIO)
kubectl apply -k kustomize/infrastructure/overlays/local
kubectl wait --for=condition=available deployment/valkey --timeout=60s
kubectl wait --for=condition=available deployment/minio --timeout=60s

# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/v3.3.2/manifests/install.yaml
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=120s

# Deploy app via ArgoCD
kubectl apply -f argocd/application.yaml
kubectl wait --for=condition=available deployment/hivebox --timeout=120s

# Access HiveBox
kubectl port-forward svc/hivebox 9090:8080
# Open http://localhost:9090

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
# Open https://localhost:8080 — Username: admin
```

### Kubernetes (EKS) — Cloud

```bash
# Create EKS cluster
cd terraform
terraform init
terraform apply

# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name hivebox

# Deploy infrastructure
kubectl apply -k kustomize/infrastructure/overlays/local

# Deploy app
helm upgrade --install hivebox helm/hivebox --namespace default
```

## Observability

Grafana Cloud is used for metrics and log aggregation.

### Setup Grafana Monitoring

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm upgrade --install grafana-k8s-monitoring grafana/k8s-monitoring \
  --namespace default \
  --values grafana-values.yaml
```

> **Note:** `grafana-values.yaml` contains sensitive credentials and is not committed to git. Create it locally with your Grafana Cloud details before deploying.

### What is monitored

- Kubernetes cluster metrics (CPU, Memory, Network)
- Pod logs from all namespaces
- Custom HiveBox metrics (temperature, cache hits/misses, accessible senseBoxes)

## API Endpoints

| Endpoint     | Method | Description                             |
| ------------ | ------ | --------------------------------------- |
| /version     | GET    | Returns current app version             |
| /temperature | GET    | Returns average temperature with status |
| /store       | GET    | Manually trigger MinIO storage          |
| /readyz      | GET    | Readiness probe endpoint                |
| /metrics     | GET    | Returns Prometheus metrics              |

## Custom Prometheus Metrics

| Metric                        | Type    | Description                 |
| ----------------------------- | ------- | --------------------------- |
| `hivebox_temperature_celsius` | Gauge   | Current average temperature |
| `hivebox_cache_hits_total`    | Counter | Total cache hits            |
| `hivebox_cache_misses_total`  | Counter | Total cache misses          |
| `hivebox_sensebox_accessible` | Gauge   | Accessible senseBoxes count |

## How to Test

```bash
# Unit tests
python -m pytest tests/test_app.py -v

# Integration tests
python -m pytest tests/test_integration.py -v

# E2E tests with Venom
venom run tests/e2e/hivebox.yaml --var url=http://localhost:8080

# All tests with coverage
python -m pytest tests/test_app.py -v --cov=src --cov-report=xml
```

## CI/CD Pipeline

### CI (`ci.yml`) — runs on all branches and PRs

| Job                | Description                 |
| ------------------ | --------------------------- |
| `test`             | Unit tests with coverage    |
| `lint`             | Pylint code quality check   |
| `lint-dockerfile`  | Hadolint Dockerfile check   |
| `scan-k8s`         | Terrascan K8s security scan |
| `docker`           | Docker build and test       |
| `integration-test` | Integration tests on KIND   |
| `e2e-test`         | Venom E2E tests on KIND     |
| `sonarcloud`       | SonarCloud code analysis    |

### CD (`cd.yml`) — runs after CI passes on main

| Job  | Description                                                                   |
| ---- | ----------------------------------------------------------------------------- |
| `cd` | Build + Trivy scan + push to GHCR + update Helm values → ArgoCD syncs cluster |

## Project Status

- Phase 1 - Initial version with app versioning ✔️
- Phase 2 - Flask REST API + Dockerized ✔️
- Phase 3 - Unit tests, CI pipeline, Docker best practices ✔️
- Phase 4 - Kubernetes, Observability, CD pipeline ✔️
- Phase 5 - Caching, Storage, Helm, Kustomize, Terraform, Grafana, E2E tests ✔️
- Phase 6 - GitOps with ArgoCD, Dependabot, Supply Chain Security ✔️
