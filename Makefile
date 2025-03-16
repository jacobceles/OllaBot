IMAGE = ollabot
TAG = latest-version
OllamaImage = ollama
FastapiImage = fastapi
StreamlitImage = streamlit

switch-context:
	@kubectl config use-context docker-desktop || (echo "docker-desktop context is not available. Exiting." && exit 1)

build-ollabot:
	docker build -t ${FastapiImage}:${TAG} -f "./docker/fastapi/DockerFile" .
	docker build -t ${StreamlitImage}:${TAG} -f "./docker/streamlit/DockerFile" .

deploy-dev: switch-context
	kubectl apply -k k8s-manifests/environments/dev -n dev

deploy-personal: switch-context
	kubectl apply -k k8s-manifests/environments/vineeth/
	kubectl apply -k k8s-manifests/applications/ollabot/base/monitoring