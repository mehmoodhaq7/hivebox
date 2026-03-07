# HiveBox 🐝

A scalable RESTful API for beekeepers using openSenseMap data.

## Version

Current version: v0.0.1

## What is HiveBox?

HiveBox fetches temperature data from beehive-mounted sensors
via openSenseMap API and exposes it through a REST API.

## SenseBox IDs Used

- 5eba5fbad46fb8001b799786
- 5c21ff8f919bf8001adf2488
- 5ade1acf223bd80019a1011c

## How to Run

### Local

```bash
pip install -r requirements.txt
python src/app.py
```

### Docker

```bash
docker build -t hivebox:0.0.1 .
docker run -p 8080:8080 hivebox:0.0.1
```

### Kubernetes (KIND)

```bash
# Making Cluster
kind create cluster --name hivebox --config kind-config.yaml

# Install Ingress-Nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Load Image
kind load docker-image hivebox:0.0.1 --name hivebox

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## API Endpoints

| Endpoint     | Method | Description                             |
| ------------ | ------ | --------------------------------------- |
| /version     | GET    | Returns current app version             |
| /temperature | GET    | Returns average temperature with status |
| /metrics     | GET    | Returns Prometheus metrics              |

## How to Test

```bash
# Unit tests
python -m pytest tests/test_app.py -v

# Integration tests
python -m pytest tests/test_integration.py -v

# All tests with coverage
python -m pytest tests/test_app.py -v --cov=src --cov-report=xml
```

## CI/CD Pipeline

- **CI:** Lint, Tests, Docker Build, K8s Scan, SonarCloud
- **CD:** Auto push to GitHub Container Registry on main merge

## Project Status

- Phase 1 - Initial version with app versioning ✔️
- Phase 2 - Flask REST API + Dockerized ✔️
- Phase 3 - Unit tests, CI pipeline, Docker best practices ✔️
- Phase 4 - Kubernetes, Observability, CD pipeline ✔️
