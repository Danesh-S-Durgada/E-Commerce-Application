# Cloud E-Commerce DevOps

A production-style learning project using Angular, FastAPI, MySQL, Docker, Jenkins, Terraform, AWS ECR/EKS, Kubernetes, Helm, Argo CD, Trivy, Prometheus, Grafana and Loki.

## Local run

```bash
docker compose up -d --build
```

Open:
- Frontend: http://localhost:4200
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- API health: http://localhost:8000/health
- DB health: http://localhost:8000/health/db

## API

Products:
- GET `/api/products/`
- GET `/api/products/{id}`
- POST `/api/products/`
- PUT `/api/products/{id}`
- DELETE `/api/products/{id}`

This repository is intentionally built in phases. Start with local Docker Compose, then configure CI/CD, Terraform, EKS, Helm, Argo CD and observability.
