IMAGE = ollabot
TAG = latest-version
NAMESPACE = tartarus
DOCKERFILE_DIR = /Docker\ Files
DOCKERFILE1 = $(DOCKERFILE_DIR)/ollama-service.DockerFile

OllamaImage = ollama
FastapiImage = fastapi
StreamlitImage = streamlit
switch-context:
	@kubectl config use-context docker-desktop || (echo "docker-desktop context is not available. Exiting." && exit 1)
	@kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)


build-ollama:
	docker build -t ${OllamaImage}:${TAG} -f "./Docker Files/ollama-service.DockerFile" .

build-fastapi:
	docker build -t ${FastapiImage}:${TAG} -f "./Docker Files/fastapi.DockerFile" .


build-streamlit:
	docker build -t ${StreamlitImage}:${TAG} -f "./Docker Files/streamlit.DockerFile" .

dockerrun:
	docker run -p 8000:8000 -p 8501:8501 ${IMAGE}:${TAG}

k8sdeploy: switch-context
	kubectl apply -n $(NAMESPACE) -f ./k8s-manifests/Ollama_Deployment.yaml

k8sdeployfastapi: switch-context
	kubectl apply -n $(NAMESPACE) -f ./k8s-manifests/FastApi_Deployment.yaml

k8sdeploystreamlit: switch-context
	kubectl apply -n $(NAMESPACE) -f ./k8s-manifests/Streamlit_Deployment.yaml