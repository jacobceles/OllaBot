IMAGE = ollabot
TAG = latest-version
OllamaImage = ollama
FastapiImage = fastapi
StreamlitImage = streamlit

switch-context:
	@kubectl config use-context docker-desktop || (echo "docker-desktop context is not available. Exiting." && exit 1)

build-ollabot:
	docker build -t ${FastapiImage}:${TAG} -f "./Docker Files/fastapi/DockerFile" .
	docker build -t ${StreamlitImage}:${TAG} -f "./Docker Files/streamlit/DockerFile" .


deploy-dev: switch-context
	kubectl apply -k k8s-manifests/applications/ollabot/environments/dev -n dev

deploy-personal: switch-context
	kubectl apply -k k8s-manifests/applications/ollabot/environments/developers/vineeth -n tartarus