import json
import yaml
import copy

from yaml import YAMLObject

from enum import Enum

from .encode_base64 import encodeb64

class ConversionType(Enum):
    quoted_string = 1
    integer_string = 2
    normal = 3

class K8Selector(YAMLObject):

    def __init__(self, matchLabels_dict):
        self.matchLabels = copy.deepcopy(matchLabels_dict)
class K8Labels(YAMLObject):

    def __init__(self, labels):
        self.labels = copy.deepcopy(labels)
class K8EnvironmentVariable(YAMLObject):

    def __init__(self, name, value, convert_type):
        self.name = name
        if convert_type == ConversionType.quoted_string:
            self.value = "\"{0}\"".format(value)
        elif convert_type == ConversionType.integer_string:
            self.value = str(value)
        elif convert_type == ConversionType.normal:
            self.value = value
        else:
            raise Exception("Unrecognised conversion type: {0}".format(convert_type))
class K8EnvironmentVariableContainerRuntime(YAMLObject):

    def __init__(self, name, fieldPath):
        self.name = name
        self.valueFrom = {"fieldRef": {"fieldPath": fieldPath}}
class K8EnvironmentVariableFromSecrets(YAMLObject):

    def __init__(self, name, secret_name, secret_key):
        self.name = name
        self.valueFrom = {"secretKeyRef": {"name": secret_name, "key": secret_key}}
class K8ContainerVolumeMount(YAMLObject):

    def __init__(self, name, mountPath):
        self.name = name
        self.mountPath = "{0}".format(mountPath)
        # self.mountPath = mountPath
class K8Container(YAMLObject):

    def __init__(self,
                name,
                registry,
                image_name,
                image_tag,
                env_var_list,
                env_var_list_runtime,
                env_var_list_fromsecrets,
                vol_mounts_list,
                res_handling):
        self.name = name
        self.image = "{0}/{1}:{2}".format(registry, image_name, image_tag)
        self.imagePullPolicy = "Always"
        self.env = self.get_env_vars(env_var_list,
                                    env_var_list_runtime,
                                    env_var_list_fromsecrets)
        if vol_mounts_list:
            self.volumeMounts = self.get_vol_mounts(vol_mounts_list)
        if res_handling:
            self.resources = res_handling.__dict__

    @staticmethod
    def get_env_vars(env_var_list,
                    env_var_list_runtime,
                    env_var_list_fromsecrets):
        new_list = []
        for eee in env_var_list:
            new_list.append(K8EnvironmentVariable(eee[0], eee[1], eee[2]).__dict__)
        for eee in env_var_list_runtime:
            new_list.append(K8EnvironmentVariableContainerRuntime(eee[0], eee[1]).__dict__)
        for eee in env_var_list_fromsecrets:
            new_list.append(K8EnvironmentVariableFromSecrets(eee[0], eee[1], eee[2]).__dict__)

        return new_list
    @staticmethod
    def get_vol_mounts(vol_mounts_list):
        new_list = []
        for vvv in vol_mounts_list:
            new_list.append(K8ContainerVolumeMount(vvv[0], vvv[1]).__dict__)

        return new_list
class K8Volume(YAMLObject):

    def __init__(self,
                name,
                azureFile_secret_name,
                azureFile_share_name):
        self.name = name
        self.azureFile = {}
        self.azureFile["secretName"] = azureFile_secret_name
        self.azureFile["shareName"] = azureFile_share_name
        self.azureFile["readOnly"] = False
class K8Template(YAMLObject):
    def __init__(self,
                metadata,
                spec):
        if metadata:
            self.metadata = K8Labels(metadata).__dict__
        self.spec = spec
class K8Port(YAMLObject):
    def __init__(self,
                name,
                port,
                targetPort):
        self.name = name
        self.port = port
        self.targetPort = targetPort
        self.protocol = "TCP"
class K8ResourceHandling(YAMLObject):
    def __init__(self,
                cpu,
                mem):
        self.requests = {}
        self.requests["cpu"] = cpu
        self.requests["memory"] = mem
class K8SecretName(YAMLObject):
    def __init__(self,
                name):
        self.name = name

class K8BaseResource(YAMLObject):

    yaml_tag = u'!BaseResource'

    def __init__(self,
        apiVersion,
        kind,
        metadata):
        self.apiVersion = apiVersion
        self.kind = kind

        self.metadata = copy.deepcopy(metadata)

    @staticmethod
    def dictify_list(input_list):
        new_list = []
        for iii in input_list:
            new_list.append(iii.__dict__)
        return new_list
class K8Deployment(K8BaseResource):

    yaml_tag = u'!Deployment'

    def __init__(self,
        metadata={}):
        super(K8Deployment, self).__init__("apps/v1", "Deployment", metadata)

    def fill_specification(self,
                            replicas,
                            revisionHistoryLimit,
                            selector,
                            template):
        spec_dict = {}
        spec_dict["replicas"] = replicas
        spec_dict["revisionHistoryLimit"] = revisionHistoryLimit
        spec_dict["selector"] = selector.__dict__
        spec_dict["template"] = template.__dict__

        self.spec = spec_dict
    def get_template_spec(self,
        container_list,
        volume_list,
        imgPullSecretName=None):
        spec_dict = {}
        spec_dict["containers"] = self.dictify_list(container_list)
        if volume_list:
            spec_dict["volumes"] = self.dictify_list(volume_list)
        if imgPullSecretName:
            spec_dict["imagePullSecrets"] = self.dictify_list([imgPullSecretName])

        return spec_dict
class K8Service(K8BaseResource):

    yaml_tag = u'!Service'

    def __init__(self,
        metadata={}):
        super(K8Service, self).__init__("v1", "Service", metadata)

    def fill_specification(self,
                            port_list,
                            selector_dict,
                            svc_type=None,
                            static_ip=None,
                            ip_whitelist=[]):
        spec_dict = {}
        spec_dict["ports"] = self.dictify_list(port_list)
        spec_dict["selector"] = selector_dict

        if svc_type and svc_type.lower() == "loadbalancer":
            spec_dict["type"] = svc_type
            spec_dict["loadBalancerIP"] = static_ip
            spec_dict["externalTrafficPolicy"] = "Local"
            if len(ip_whitelist) > 0:
                spec_dict["loadBalancerSourceRanges"] = [iii + "/32" for iii in ip_whitelist]

        self.spec = spec_dict
class K8Job(K8BaseResource):

    yaml_tag = u'!Job'

    def __init__(self,
        metadata={}):
        super(K8Job, self).__init__("batch/v1", "Job", metadata)

    def fill_specification(self,
                            backoffLimit,
                            template):
        spec_dict = {}
        spec_dict["backoffLimit"] = backoffLimit
        spec_dict["template"] = template.__dict__

        self.spec = spec_dict

    def get_template_spec(self,
        container_list,
        volume_list,
        node_selector=None,
        imgPullSecretName=None):
        spec_dict = {}
        spec_dict["restartPolicy"] = "Never"
        spec_dict["containers"] = self.dictify_list(container_list)
        if volume_list:
            spec_dict["volumes"] = self.dictify_list(volume_list)
        if node_selector:
            spec_dict["nodeSelector"] = {"agentpool": node_selector}
        if imgPullSecretName:
            spec_dict["imagePullSecrets"] = self.dictify_list([imgPullSecretName])

        return spec_dict
class K8Secret(K8BaseResource):

    yaml_tag = u'!Secret'

    def __init__(self,
        metadata={},
        input_type="Opaque"):
        super(K8Secret, self).__init__("v1", "Secret", metadata)
        self.type = input_type

    def fill_data(self,
                input_data_dict):
        data_dict = {}
        for kkk, vvv in input_data_dict.items():
            data_dict[kkk] = encodeb64(vvv)

        self.data = data_dict
