IMAGE = ollabot
TAG = latest-version
OllamaImage = ollama
FastapiImage = fastapi
StreamlitImage = streamlit

build-ollabot:
	docker build -t ${OllamaImage}:${TAG} -f "./Docker Files/ollama-service.DockerFile" .
	docker build -t ${FastapiImage}:${TAG} -f "./Docker Files/fastapi.DockerFile" .
	docker build -t ${StreamlitImage}:${TAG} -f "./Docker Files/streamlit.DockerFile" .


deploy-dev:
	kubectl apply -k k8s-manifests/applications/ollabot/environments/Dev

deploy-personal:
	kubectl apply -k k8s-manifests/applications/ollabot/environments/Developers/Vineeth