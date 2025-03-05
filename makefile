IMAGE = ollabot
TAG = latest-version
NAMESPACE = tartarus
switch-context:
	@kubectl config use-context docker-desktop || (echo "docker-desktop context is not available. Exiting." && exit 1)
	@kubectl get namespace $(NAMESPACE) || kubectl create namespace $(NAMESPACE)

build:
	docker build -t ${IMAGE}:${TAG} .

dockerrun:
	docker run -p 8000:8000 -p 8501:8501 ${IMAGE}:${TAG}

k8sdeploy: switch-context
	kubectl apply -n $(NAMESPACE) -f deployment.yaml