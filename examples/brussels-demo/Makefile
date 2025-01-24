# Change to Host's IP
HOST_IP := 10.0.3.53
REGISTRY := ${HOST_IP}:5000
HDAR := http://${HOST_IP}:5000
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

change-ips: ## Changes the IPs declared in the artifacts to the proper ones
	echo "Changing IPs in the helmcharts..."
	sed -i 's|image: [^/]*/|image: ${REGISTRY}/|' image-compression-vo/templates/deployment.yaml
	sed -i 's|image: [^/]*/|image: ${REGISTRY}/|' image-detection/templates/deployment.yaml
	sed -i 's|image: [^/]*/|image: ${REGISTRY}/|' noise-reduction/templates/deployment.yaml
	sed -i 's|ociImage: "oci://[^/]*/|ociImage: "oci://${REGISTRY}/|' hdag/hdag.yaml

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
