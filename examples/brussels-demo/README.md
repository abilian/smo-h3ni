# Brussels demo
This demo is composed of an image detection graph.

## Layout
```
├── hdag
├── image-compression-vo
├── image-detection
├── noise-reduction
├── src
├── create-existing-artifact.sh
├── Makefile
└── README.md
```
- **hdag**: Directory that has the Hyper Distributed Application Graph (HDAG) descriptor
- **image-compression-vo**: Helmchart of a VO that does image compression
- **image-detection**: Helmchart of an image detection application
- **noise-reduction**: Helmchart of a noise reduction application
- **src**: Source code for the docker images of each application
- **create-existing-artifact.sh**: Bash script that sends a request to the SMO to deploy this graph
- **Makefile**: Makefile with rules to build images, helmchart artifacts and push them to a registry
- **README.md**: This file

## Instructions
This directory has a Makefile to more easily prepare the demo.
> ### ⚠️ Warning
> Make sure to change the values of the variables on top of the Makefile
### Build images
By running:
```bash
make build-images
make push-images
```
the docker images of the three services are built and pushed to a local Distribution registry.
### Package artifacts
To package the helmchart the `hdarctl` is needed. The current version used is [here](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/nephele-development-sandbox/-/raw/main/tools/hdarctl).
Afterwards we run the command:
```bash
make package-artifacts
```
The output of this command is four artifacts (VO, HDAG and two application nodes).
### Push artifacts
The artifacts can be pushed to the Hyper Distributed Application Registry (HDAR) by running:
```bash
make push-artifacts
```
This command runs the `package-artifacts` rule and then pushes the created artifacts to the registry/HDAR.
