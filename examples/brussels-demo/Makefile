# Change to Host's IP
REGISTRY := 10.0.3.53:5000
HDAR := http://10.0.3.53:5000
PROJECT := test

default: help

all help: ## Show this help
	@grep -F -h "##" $(MAKEFILE_LIST) | grep -F -v grep -F | sed -e 's/\\$$//' | sed -e 's/##//'

build-images: ## Build all docker images
	echo "Creating docker images and pushing to dockerhub..."
	docker build -t "${REGISTRY}/custom-vo" src/virtual-object/
	docker build -t "${REGISTRY}/noise-reduction" src/noise-reduction/
	docker build -t "${REGISTRY}/image-detection" src/image-detection/

push-images: build-images ## Push all docker images to the registry
	echo "Pushing images to the registry..."
	docker push "${REGISTRY}/custom-vo"
	docker push "${REGISTRY}/noise-reduction"
	docker push "${REGISTRY}/image-detection"

registry-login: ## Login to the HDAR registry
	echo "Logging in to HDAR located at ${HDAR}..."
	hdarctl login ${HDAR}

package-artifacts: ## Package artifacts
	echo "Packaging artifacts..."
	hdarctl package tar image-compression-vo/
	hdarctl package tar hdag/
	hdarctl package tar image-detection/
	hdarctl package tar noise-reduction/

push-artifacts: package-artifacts ## Push packaged artifacts to the HDAR them to the HDAR
	echo "Pushing artifacts..."
	hdarctl push image-compression-vo-0.1.0.tar.gz  ${HDAR}/${PROJECT}
	hdarctl push image-detection-graph-1.0.0.tar.gz ${HDAR}/${PROJECT}
	hdarctl push image-detection-0.1.0.tar.gz ${HDAR}/${PROJECT}
	hdarctl push noise-reduction-0.1.0.tar.gz ${HDAR}/${PROJECT}

.PHONY: all build-images registry-login package-artifacts push-artifacts help
