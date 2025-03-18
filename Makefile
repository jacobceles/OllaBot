IMAGE = ollabot
TAG = latest-version
OllamaImage = ollama
FastapiImage = fastapi
StreamlitImage = streamlit
MonitoringNamespace = monitoring

switch-context:
	@kubectl config use-context docker-desktop || (echo "docker-desktop context is not available. Exiting." && exit 1)
	kubectl config set-context --current --namespace=$(NAMESPACE)

build-ollabot:
	docker build -t ${FastapiImage}:${TAG} -f "./docker/fastapi/DockerFile" .
	docker build -t ${StreamlitImage}:${TAG} -f "./docker/streamlit/DockerFile" .

deploy-dev: switch-context
	kubectl apply -k k8s-manifests/environments/dev -n dev

deploy-personal: switch-context
	kubectl apply -k k8s-manifests/environments/vineeth/
	kubectl apply -k k8s-manifests/applications/ollabot/base/monitoring

deploy-monitoring:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || (echo "Not able to fetch repo from git. Exiting." && exit 1)
	helm repo update
	helm install prometheus prometheus-community/kube-prometheus-stack \
	--namespace $(MonitoringNamespace) \
	--values k8s-manifests/applications/ollabot/base/monitoring/prometheus-values.yaml
	--set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
	--set prometheus.prometheusSpec.serviceMonitorSelector.matchLabels.monitoring=enabled
	@echo "Patching Node Exporter DaemonSet to remove mountPropagation..."
	@echo "Applying patched Node Exporter DaemonSet..."
	kubectl patch daemonset prometheus-prometheus-node-exporter -n $(MonitoringNamespace) --type='json' -p='[{"op": "remove", "path": "/spec/template/spec/containers/0/volumeMounts/2/mountPropagation"}]'
	@echo "Node Exporter DaemonSet updated successfully."

port-forward-prometheus:
	@echo "Setting up port forwarding..."
	kubectl port-forward -n $(MonitoringNamespace) svc/prometheus-grafana 3000:80 &
	#{kubectl port-forward -n $(MonitoringNamespace) svc/prometheus-operated 9090:9090} &&
	@echo "Port forwarding active. Press Ctrl+C to terminate."

port-forward-grafana:
	@echo "Setting up port forwarding..."
	kubectl port-forward -n $(MonitoringNamespace) svc/prometheus-operated 9090:9090 &
	@echo "Port forwarding active. Press Ctrl+C to terminate."
# Grafana Creds - user - admin, Pass - prom-operator.
