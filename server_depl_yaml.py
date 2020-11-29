import json
import yaml

from helpers.k8s_yaml_obj import ConversionType
from helpers.k8s_yaml_obj import K8Deployment, K8Job, K8Selector, K8ResourceHandling, K8Container, K8Volume
from helpers.k8s_yaml_obj import K8Template, K8Service, K8Port
from helpers.k8s_yaml_obj import K8Secret, K8SecretName

def create_deploy(
    app_name,
    mounted_vol_name,
    mnt_volume_path,
    share_name,
    registry,
    image_name,
    image_tag,
    version,
    connection_ports,
    imgPullSecretName
    ):

    metadata = {"name": app_name}

    res_deploy = K8Deployment(metadata)

    identifiers = {"app": app_name, "env": "dev"}
    k8s_sel = K8Selector(identifiers)

    env_var_list = []
    env_var_list.append(["MY_VERSION", version, ConversionType.quoted_string])
    env_var_list.append(["MY_ENVIRONMENT", "dev", ConversionType.normal])
    env_var_list.append(["IS_DOCKER", "y", ConversionType.quoted_string])
    env_var_list.append(["FORCE_NEW_DB", "y", ConversionType.quoted_string])
    env_var_list.append(["SQLITE_DB_NAME", "sicilian_cards_game", ConversionType.normal])

    env_var_list_runtime = []
    env_var_list_runtime.append(["MY_NODE_NAME", "spec.nodeName"])
    env_var_list_runtime.append(["MY_POD_NAME", "metadata.name"])

    vol_mounts_list = []
    vol_mounts_list.append([mounted_vol_name, mnt_volume_path])
    volume_list = [K8Volume(mounted_vol_name, "storage", share_name)]

    container_list = [
        K8Container(
            app_name, 
            registry,
            image_name,
            image_tag,
            env_var_list,
            env_var_list_runtime,
            vol_mounts_list,
            None)
        ]

    res_imgPullSecret = K8SecretName(imgPullSecretName)

    tmpl_spec = res_deploy.get_template_spec(
        container_list,
        volume_list,
        imgPullSecretName=res_imgPullSecret)
    k8s_template = K8Template(identifiers, tmpl_spec)

    res_deploy.fill_specification(1, 1, k8s_sel, k8s_template)

    res_svc = K8Service(metadata)

    port_list = []
    for ppp in connection_ports:
        port_list.append(K8Port("{0}{1}".format(app_name, ppp), ppp, ppp))
    res_svc.fill_specification(port_list, identifiers)

    return [res_svc, res_deploy]
def create_storage_secret(
    secret_name,
    account_name,
    account_key):
    metadata = {"name": secret_name}

    res_secret = K8Secret(metadata)

    input_data_dict = {}
    input_data_dict["azurestorageaccountname"] = account_name
    input_data_dict["azurestorageaccountkey"] = account_key

    res_secret.fill_data(input_data_dict)

    return res_secret
def write_res_to_file(file_path, input_resources_list):
    tag_strings = []
    tag_strings.append("!Service")
    tag_strings.append("!Deployment")
    tag_strings.append("!Job")
    tag_strings.append("!Secret")

    with open(file_path, "w") as f:
        # yaml.dump(resource, f)
        yml_string = yaml.dump_all(input_resources_list, None)
        for sss in tag_strings:
            yml_string = yml_string.replace(sss, "")
        if yml_string.startswith("\n"):
            yml_string = yml_string[1:]
        yml_string = yml_string.replace("\'\"", "\'")
        yml_string = yml_string.replace("\"\'", "\'")
        f.write(yml_string)

registry = ""
version = "1.0.0"

imgPullSecretName="acrregistry"

mounted_vol_name = "mountedvolume"
share_name = "servercardgame"

app_name = "tf_server"
image_name = "tf_server"
file_path = "deploy_{0}.yml".format(app_name)
mnt_volume_path = "/mnt/mounted_volume/permanentstorage/"
image_tag = version
connection_ports = [5000]

all_resources = []
all_resources.append(create_deploy(
                        app_name,
                        mounted_vol_name,
                        mnt_volume_path,
                        share_name,
                        registry,
                        image_name,
                        image_tag,
                        version,
                        connection_ports,
                        imgPullSecretName
                        ))
write_res_to_file(file_path, all_resources)

app_name = "nginx"
image_name = "tf_server"
image_tag = "nginx"
file_path = "deploy_{0}.yml".format(app_name)
mnt_volume_path = "/app/permanentstorage/"
connection_ports = [80, 443]

all_resources = []
all_resources.append(create_deploy(
                        app_name,
                        mounted_vol_name,
                        mnt_volume_path,
                        share_name,
                        registry,
                        image_name,
                        image_tag,
                        version,
                        connection_ports,
                        imgPullSecretName
                        ))
write_res_to_file(file_path, all_resources)

secret_name = "storage"
account_name = ""
account_key = ""
file_path = "secret_{0}.yml".format(secret_name)
all_resources = []
all_resources.append(create_storage_secret(
                        secret_name,
                        account_name,
                        account_key))
write_res_to_file(file_path, all_resources)
