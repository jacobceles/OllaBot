IMAGE = ollabot
TAG = latest-version

build:
	docker build -t ${IMAGE}${TAG} .