import os
import logging
import yaml
import boto3

from boto3 import s3
from botocore.exceptions import ClientError
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

s3 = boto3.resource('s3')

try:
    object_raw = s3.Object(os.environ.get('S3_BUCKET'), os.environ.get('CONFIGMAP_PATH')).get()['Body'].read()
    object_yaml = yaml.safe_load(object_raw)
    logging.info("Successfully retrieved configmap data from S3: " + str(object_yaml['data']))
except ClientError as e:
    error_code = e.response["Error"]["Code"]
    if error_code == "AccessDenied":
         logging.error("Exception when retrieving S3 object: Access Denied %s\n" % e)
    elif error_code == "InvalidLocationConstraint":
         logging.error("Exception when retrieving S3 object: InvalidLocationConstraint %s\n" % e)

config.load_incluster_config()
api_instance = client.CoreV1Api()
name = 'app-config'
namespace = 'default'

try:
    api_response = api_instance.read_namespaced_config_map(name, namespace)
    configmap_data = api_response.data
    logging.info("Successfully retrieved configmap data from master node: " + str(configmap_data))
except ApiException as e:
    logging.error("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)

if configmap_data != object_yaml['data']:
    try:
        configmap_request = client.V1ConfigMap(
            api_version=object_yaml['apiVersion'],
            data=object_yaml['data'], 
            kind=object_yaml['kind'], 
            metadata= client.V1ObjectMeta(
                name=object_yaml['metadata']['name'],
                namespace=object_yaml['metadata']['namespace']
            )
        )
        api_response = api_instance.replace_namespaced_config_map(name, namespace, configmap_request)
        logging.info(api_response)
    except ApiException as e:
        logging.error("Exception when calling CoreV1Api->create_namespaced_config_map: %s\n" % e)
else:
    logging.info("No configmap changes detected")