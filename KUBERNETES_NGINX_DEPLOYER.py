###############################################################################
#AUTHOR: SANGEETHA VENUGOPAL
#MAIL: sangeethafrwr@gmail.com
#
#                TOOL : KUBERNETES NGINX DEPLOYER
#
#Description: Tool can be used to create,update or delete an ngnix deployment
#
#USAGE: knd or KND
#Above command displays the synopsis
#
################################################################################

import datetime
import sys
import argparse
from tqdm import tqdm
import time

#Importing kubernetes python client to add deployment config

from kubernetes import client, config

def create_deployment_object(replicas):
    # Configure Pod template container
    container = client.V1Container(
        name="nginx",
        image="nginx:1.15.4",
        ports=[client.V1ContainerPort(container_port=80)],
        resources=client.V1ResourceRequirements(
            requests={"cpu": "100m", "memory": "200Mi"},
            limits={"cpu": "500m", "memory": "500Mi"},
        ),
    )

    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
        spec=client.V1PodSpec(containers=[container]),
    )

    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=replicas, template=template, selector={
            "matchLabels":
            {"app": "nginx"}})

    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
        spec=spec,
    )

    return deployment

#Func to Create deployment with default namespace & print the deployment details
def create_deployment(api, deployment):
    # Create deployement
    resp = api.create_namespaced_deployment(
        body=deployment, namespace="default"
    )

    print("\n[INFO] deployment `nginx-deployment` created.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )

#Func to update deployment with given ngnix version & print the deployment details
def update_deployment(api, ngnix_version, deployment):
    # Update container image
    deployment.spec.template.spec.containers[0].image = args.ngnix_version

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="default", body=deployment
    )

    print("\n[INFO] deployment's container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )

#Func to delete deployment with given ngnix deployment
def delete_deployment(api):
    # Delete deployment
    resp = api.delete_namespaced_deployment(
        name=DEPLOYMENT_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy="Foreground", grace_period_seconds=5
        ),
    )
    print("\n[INFO] deployment `nginx-deployment` deleted.")

#Func to check if arguments passed
def check_args():
    if len(sys.argv) < 3:
        f = open('/root/synopsis.txt', 'r')
        content = f.read()
        print(content)
        f.close()
        sys.exit(1)

#progress bar func
def progress_bar(i):
    for i in tqdm(range(i)):
        time.sleep(2)

#Main func call other functions based action given
def main():
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()
    deployment = create_deployment_object(3)
    if args.action == "create":
        print("CREATING NGINX DEPLOYMENT WITH DEFAULT VERSION : nginx:1.15.4 ")
        progress_bar(2)
        create_deployment(apps_v1, deployment)
    elif args.action == "update":
        print("UPDATING NGNIX DEPLOYMENT version : ", args.ngnix_version)
        progress_bar(2)
        update_deployment(apps_v1, args.ngnix_version, deployment)
    elif args.action == "delete":
        print("DELETING THE NGNIX DEPLOYMENT :", args.deployment_name)
        progress_bar(1)
        delete_deployment(apps_v1)
    else:
        print("GIVEN ACTION CANNOT BE PERFORMED!! KINDLY REFER SYNOPSIS")

#Prasing CLI arguments and calling main func
if __name__ == "__main__":
    check_args()
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", help="values: create/update/delete")
    parser.add_argument("-r", "--replicas", help="no_of_Replicas")
    parser.add_argument("-v", "--ngnix_version", help="ngnix_container_vers")
    parser.add_argument("-d", "--deployment_name", help="deployment_name")
    args = parser.parse_args()
    DEPLOYMENT_NAME = args.deployment_name
    main()
