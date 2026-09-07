# Profitilo 🚀

**Amit Pal's Interactive AI Portfolio** - A modern, dynamic portfolio website powered by FastAPI and Groq's LLaMA 3 LLM. Features an intelligent chatbot that answers questions about my ML/AI projects and experience.

## Features

- 🎨 Beautiful, responsive HTML/CSS design
- 🤖 AI-powered chatbot using Groq's LLaMA 3
- 💬 Real-time chat interface with FastAPI backend
- 🔒 Secure API key management with `.env` file
- 📱 Mobile-friendly UI

## Setup

1. Create and activate the conda environment:
   `conda create --name profitilo python=3.12 -y`
   `conda activate profitilo`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Run the application backend:
   `python main.py` or `uvicorn main:app --reload`

## Run with Docker

Build and start the container locally:

```bash
docker build -t profitilo:local .
docker run --rm -p 8000:8000 --env-file .env profitilo:local
```

Open `http://localhost:8000`.

## Run with Kubernetes

These commands use Minikube or another local Kubernetes cluster. Create the
Secret from your local `.env` value; never put the real API key in YAML:

```bash
docker build -t profitilo:local .
minikube image load profitilo:local
set -a; source .env; set +a
kubectl create secret generic profitilo-secrets \
   --from-literal=groq-api-key="$GROQ_API_KEY" \
   --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/app.yaml
kubectl rollout status deployment/profitilo
kubectl port-forward service/profitilo 8000:80
```

Then open `http://localhost:8000`. The optional `k8s/ingress.yaml` requires an
NGINX Ingress controller and is useful for practising Kubernetes routing.
