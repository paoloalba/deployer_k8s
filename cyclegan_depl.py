import json
import yaml

from copy import deepcopy

from k8syaml.k8s_yaml_obj import ConversionType, K8BaseResource
from k8syaml.k8s_yaml_obj import K8Deployment, K8Job, K8Selector, K8ResourceHandling, K8Container, K8Volume
from k8syaml.k8s_yaml_obj import K8Template, K8Service, K8Port
from k8syaml.k8s_yaml_obj import K8Secret, K8SecretName

def create_job(
    app_name,
    version,
    registry,
    image_name,
    mounted_vol_name,
    share_name,
    sel_nodepool,
    imgPullSecretName,
    status_frq,
    chckp_frq,
    summary_frq,
    batch_size,
    max_num_steps
    ):

    metadata = {"name": app_name}

    res_job = K8Job(metadata)

    identifiers = {"app": app_name, "env": "dev"}

    k8s_sel = K8Selector(identifiers)

    env_var_list = []
    ##### Generic Env Vars
    env_var_list.append(["MY_VERSION", version, ConversionType.quoted_string])
    env_var_list.append(["MY_ENVIRONMENT", "dev", ConversionType.normal])
    env_var_list.append(["TFGAN_REPO", "/mnt/tf_gan/", ConversionType.quoted_string])

    env_var_list.append(["STATUS_FRQ", status_frq, ConversionType.integer_string])
    env_var_list.append(["CHCKP_FRQ", chckp_frq, ConversionType.integer_string])
    env_var_list.append(["SUMMARY_FRQ", summary_frq, ConversionType.integer_string])
    env_var_list.append(["BATCH_SIZE", batch_size, ConversionType.integer_string])
    env_var_list.append(["MAX_NUM_STEPS", max_num_steps, ConversionType.integer_string])

    env_var_list_runtime = []
    env_var_list_runtime.append(["MY_NODE_NAME", "spec.nodeName"])
    env_var_list_runtime.append(["MY_POD_NAME", "metadata.name"])

    vol_mounts_list = []
    vol_mounts_list.append([mounted_vol_name, "/mnt/permanentstorage"])

    volume_list = []
    volume_list.append(K8Volume(mounted_vol_name, "storage", share_name))

    container_list = [
        K8Container(
            app_name, 
            registry,
            image_name,
            version,
            env_var_list,
            env_var_list_runtime,
            [],
            vol_mounts_list,
            None)
        ]

    if imgPullSecretName:
        res_imgPullSecret = K8SecretName(imgPullSecretName)
    else:
        res_imgPullSecret = None

    tmpl_spec = res_job.get_template_spec(
        container_list,
        volume_list,
        node_selector=sel_nodepool,
        imgPullSecretName=res_imgPullSecret)
    k8s_template = K8Template(None, tmpl_spec)

    res_job.fill_specification(0, k8s_template)

    return res_job
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
    pmt_storage_secret_name,
    postgres_secret_name,
    imgPullSecretName,
    svc_type,
    static_ip,
    static_ip_rg,
    ip_whitelist
    ):

    metadata = {"name": app_name}

    res_deploy = K8Deployment(metadata)

    identifiers = {"app": app_name, "env": "dev"}
    k8s_sel = K8Selector(identifiers)

    env_var_list = []
    env_var_list.append(["MY_VERSION", version, ConversionType.quoted_string])
    env_var_list.append(["MY_ENVIRONMENT", "dev", ConversionType.normal])
    env_var_list.append(["EVENTS_DIR", "/mnt/permanentstorage/cyclegan", ConversionType.quoted_string])

    env_var_list_runtime = []
    env_var_list_runtime.append(["MY_NODE_NAME", "spec.nodeName"])
    env_var_list_runtime.append(["MY_POD_NAME", "metadata.name"])

    env_var_list_fromsecrets = []

    vol_mounts_list = []
    vol_mounts_list.append([mounted_vol_name, mnt_volume_path])
    volume_list = [K8Volume(mounted_vol_name, pmt_storage_secret_name, share_name)]

    container_list = [
        K8Container(
            app_name, 
            registry,
            image_name,
            image_tag,
            env_var_list,
            env_var_list_runtime,
            env_var_list_fromsecrets,
            vol_mounts_list,
            None)
        ]

    if imgPullSecretName:
        res_imgPullSecret = K8SecretName(imgPullSecretName)
    else:
        res_imgPullSecret = None

    tmpl_spec = res_deploy.get_template_spec(
        container_list,
        volume_list,
        imgPullSecretName=res_imgPullSecret)
    k8s_template = K8Template(identifiers, tmpl_spec)

    res_deploy.fill_specification(1, 1, k8s_sel, k8s_template)

    svc_metadata = deepcopy(metadata)
    if svc_type and svc_type.lower() == "loadbalancer":
        svc_metadata["annotations"] = {"service.beta.kubernetes.io/azure-load-balancer-resource-group": static_ip_rg}

    res_svc = K8Service(svc_metadata)

    port_list = []
    for ppp, target_ppp in connection_ports:
        port_list.append(K8Port("{0}{1}".format(app_name, ppp), ppp, target_ppp))
    res_svc.fill_specification(port_list,
                                identifiers,
                                svc_type,
                                static_ip,
                                ip_whitelist)

    return [res_svc, res_deploy]

registry = ""
version = "1.0.0"

status_frq = 100
chckp_frq = 18000
summary_frq = 1000
batch_size = 3
max_num_steps = 500000

imgPullSecretName="acrregistry"
pmt_storage_secret_name="storage"

mounted_vol_name = "mountedvolume"
share_name = "cloudcyclegan"

specifier = "cyclegan"
app_name = "tfgan{0}".format(specifier)
image_name = "tfgan{0}".format(specifier)
file_path = "job_{0}.yml".format(specifier)
sel_nodepool = "agentpool"

all_resources = []
all_resources.append(create_job(
                        app_name,
                        version,
                        registry,
                        image_name,
                        mounted_vol_name,
                        share_name,
                        sel_nodepool,
                        imgPullSecretName,
                        status_frq,
                        chckp_frq,
                        summary_frq,
                        batch_size,
                        max_num_steps
                        ))
K8BaseResource.write_to_file(file_path, all_resources)

secret_name = pmt_storage_secret_name
account_name = ""
account_key = ""
file_path = "secret_{0}.yml".format(secret_name)
all_resources = []
all_resources.append(create_storage_secret(
                        secret_name,
                        account_name,
                        account_key))
K8BaseResource.write_to_file(file_path, all_resources)

app_name = "tensorboard"
image_name = "tensorboard"
file_path = "deploy_{0}.yml".format(app_name)
mnt_volume_path = "/mnt/permanentstorage/"
image_tag = "1.0.0"
connection_ports = [[80, 6006]]

svc_type = "LoadBalancer"
static_ip_rg = ""
static_ip = ""
ip_whitelist = []
ip_whitelist.append("")

all_resources = []
all_resources.extend(create_deploy(
                        app_name,
                        mounted_vol_name,
                        mnt_volume_path,
                        share_name,
                        registry,
                        image_name,
                        image_tag,
                        version,
                        connection_ports,
                        pmt_storage_secret_name,
                        None,
                        imgPullSecretName,
                        svc_type,
                        static_ip,
                        static_ip_rg,
                        ip_whitelist
                        ))
K8BaseResource.write_to_file(file_path, all_resources)
