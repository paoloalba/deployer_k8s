# K8s deployer

This repository implementes helpers for the programmatic deployment of K8s resources on a cluster.

The core of the logic is contained in the ```k8s_yaml_obj.py```, which implements classes for relevant YAML elements on K8s resources.

The generated YAML files can be then normally used through ```kubectl``` inline commands or within the desired script.

## Pypi Installation
The core can also be installed as pypi package: `pip install k8syaml`

## Use cases

For examples of end uses please refer to
- https://github.com/paoloalba/dev_tf_model
- https://github.com/paoloalba/tf_api
- https://github.com/paoloalba/image_segmentation_distributed