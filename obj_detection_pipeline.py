import json
import yaml

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
    model_output_dir,
    model_base_name,
    batch_size
    ):

    metadata = {"name": app_name}


    res_job = K8Job(metadata)

    identifiers = {"app": app_name, "env": "dev"}

    k8s_sel = K8Selector(identifiers)

    env_var_list = []
    ##### Generic Env Vars
    env_var_list.append(["MY_VERSION", version, ConversionType.quoted_string])
    env_var_list.append(["MY_ENVIRONMENT", "dev", ConversionType.normal])
    env_var_list.append(["IS_DOCKER", "y", ConversionType.quoted_string])
    env_var_list.append(["PIPELINE_CONFIG_PATH", "/mnt/mounted_volume/permanent_storage/patched_config/pipeline.config",    ConversionType.quoted_string])
    env_var_list.append(["MODEL_DIR", "/mnt/mounted_volume/permanent_storage/{0}/".format(model_output_dir),    ConversionType.quoted_string])
    ##### Training Env Vars
    env_var_list.append(["BATCH_SIZE", batch_size,     ConversionType.integer_string])
    env_var_list.append(["NUM_CLASSES", 40,    ConversionType.integer_string])
    # env_var_list.append(["CHECKPOINT_EVERY_N", 10,    ConversionType.integer_string])
    # env_var_list.append(["CHECKPOINT_MAX_TO_KEEP", 25,    ConversionType.integer_string])
    env_var_list.append(["SAMPLE_DIR", "/mnt/mounted_volume/sicilian_cards_sample/card_full_model/",    ConversionType.quoted_string])
    env_var_list.append(["MODEL_BASE_NAME", model_base_name,    ConversionType.quoted_string])
    ##### Evaluation Env Vars
    # env_var_list.append(["EVAL_TIMEOUT", 10000,    ConversionType.integer_string])

    env_var_list_runtime = []
    env_var_list_runtime.append(["MY_NODE_NAME", "spec.nodeName"])
    env_var_list_runtime.append(["MY_POD_NAME", "metadata.name"])

    vol_mounts_list = []
    vol_mounts_list.append([mounted_vol_name, "/mnt/mounted_volume"])

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
            vol_mounts_list,
            None)
        ]

    res_imgPullSecret = K8SecretName(imgPullSecretName)

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

registry = ""
version = ""

batch_size = 8

model_output_dir = "card_full_model_efficientdet_d2"
model_base_name = "efficientdet_d2"

imgPullSecretName="acrregistry"

mounted_vol_name = "mountedvolume"
share_name = "siciliancards"

specifier = "training"
app_name = "siciliancards{0}".format(specifier)
image_name = "sicilian_cards_{0}".format(specifier)
file_path = "job_{0}.yml".format(specifier)
sel_nodepool = "gpupool"

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
                        model_output_dir,
                        model_base_name,
                        batch_size))
K8BaseResource.write_to_file(file_path, all_resources)

# with open("my_first.yml", "r") as f:
#     allo = yaml.load(f)
#     print(allo.metadata)

specifier = "evaluation"
app_name = "siciliancards{0}".format(specifier)
image_name = "sicilian_cards_{0}".format(specifier)
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
                        model_output_dir,
                        model_base_name,
                        batch_size))
K8BaseResource.write_to_file(file_path, all_resources)

secret_name = "storage"
account_name = ""
account_key = ""
file_path = "secret_{0}.yml".format(secret_name)
all_resources = []
all_resources.append(create_storage_secret(
                        secret_name,
                        account_name,
                        account_key))
K8BaseResource.write_to_file(file_path, all_resources)
