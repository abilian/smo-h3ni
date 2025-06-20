# Change to Host's IP
HOST_IP := 10.0.3.53
REGISTRY := ${HOST_IP}:5000
HDAR := http://${HOST_IP}:5000
PROJECT := test

default: help

all help: ## Show this help
	@grep -F -h "##" $(MAKEFILE_LIST) | grep -F -v grep -F | sed -e 's/\\$$//' | sed -e 's/##//'

build-image: ## Build the docker image for the hello-world app
	echo "Creating docker image..."
	docker build -t "${REGISTRY}/hello-world" src/hello-world/

push-images: build-image ## Push the docker image to the registry
	echo "Pushing image to the registry..."
	docker push "${REGISTRY}/hello-world"

change-ips: ## Changes the IPs declared in the artifacts to the proper ones
	echo "Changing IPs in the helmchart and hdag descriptor..."
	sed -i 's|image: [^/]*/|image: ${REGISTRY}/|' hello-world/templates/deployment.yaml
	sed -i 's|ociImage: "oci://[^/]*/|ociImage: "oci://${REGISTRY}/|' hdag/hdag.yaml

package-artifacts: ## Package artifacts
	echo "Packaging artifacts..."
	hdarctl package tar hello-world/
	hdarctl package tar hdag/

push-artifacts: change-ips package-artifacts ## Push packaged artifacts to the HDAR
	echo "Pushing artifacts..."
	hdarctl push hello-world-0.1.0.tar.gz ${HDAR}/${PROJECT}
	hdarctl push hello-world-graph-1.0.0.tar.gz ${HDAR}/${PROJECT}

.PHONY: all build-image push-images change-ips package-artifacts push-artifacts help
