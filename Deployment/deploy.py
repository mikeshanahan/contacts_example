import json
import logging
import os
import time
from decimal import Decimal
import boto3

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


def wait_for_stack_update(stack_name):
    client = boto3.client("cloudformation")
    response = client.describe_stacks(
        StackName=stack_name,
    )

    for retry in range(500):
        stack_status = response["Stacks"][0]["StackStatus"]
        logging.info(f"{stack_name} Current Status: {stack_status}...")
        if "ROLLBACK" in stack_status:
            logging.info(f"Update Failed! See Cloudformation for more details.")
            exit(1)

        if stack_status not in ["UPDATE_IN_PROGRESS", "CREATE_IN_PROGRESS"]:
            if "COMPLETE" in stack_status:
                return
            logging.info(f"Update Failed! See Cloudformation for more details.")
            exit(1)

        time.sleep(5)
        response = client.describe_stacks(
            StackName=stack_name,
        )
    logging.info(f"Stack Timeout Occurred.")
    exit(1)


def deploy_stack(stack_name):
    with open("Templates/cloudformation.yml", "r") as file:
        template = file.read()

    client = boto3.client("cloudformation")
    response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template,
        OnFailure='DELETE',
        Capabilities=[
            "CAPABILITY_IAM",
            "CAPABILITY_NAMED_IAM",
            "CAPABILITY_AUTO_EXPAND",
        ]
    )


def update_stack(stack_name):
    with open("Templates/cloudformation.yml", "r") as file:
        template = file.read()
    
    client = boto3.client("cloudformation")
    response = client.update_stack(
        StackName=stack_name,
        TemplateBody=template,
        Capabilities=[
            "CAPABILITY_IAM",
            "CAPABILITY_NAMED_IAM",
            "CAPABILITY_AUTO_EXPAND",
        ],
    )
    logging.info(response)


def check_if_stack_exists(stack_name):
    client = boto3.client("cloudformation")
    all_stacks = client.list_stacks(
        StackStatusFilter=[
            "CREATE_IN_PROGRESS",
            "CREATE_FAILED",
            "CREATE_COMPLETE",
            "ROLLBACK_IN_PROGRESS",
            "ROLLBACK_FAILED",
            "ROLLBACK_COMPLETE",
            "DELETE_IN_PROGRESS",
            "DELETE_FAILED",
            "UPDATE_IN_PROGRESS",
            "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
            "UPDATE_COMPLETE",
            "UPDATE_FAILED",
            "UPDATE_ROLLBACK_IN_PROGRESS",
            "UPDATE_ROLLBACK_FAILED",
            "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
            "UPDATE_ROLLBACK_COMPLETE",
            "REVIEW_IN_PROGRESS",
            "IMPORT_IN_PROGRESS",
            "IMPORT_COMPLETE",
            "IMPORT_ROLLBACK_IN_PROGRESS",
            "IMPORT_ROLLBACK_FAILED",
            "IMPORT_ROLLBACK_COMPLETE",
        ]
    )
    for created_stack in all_stacks["StackSummaries"]:
        if stack_name == created_stack["StackName"]:
            return True
    return False


def main():
    stack_name = 'contacts-example'

    # Create or update the stack
    logging.info(f"Checking for stack {stack_name}")
    if check_if_stack_exists(stack_name):
        logging.info(f"Stack: {stack_name} Already Exists")
        update_stack(stack_name)
    else:
        logging.info(f"Creating Stack: {stack_name}")
        deploy_stack(stack_name)
    time.sleep(5)  # Buffer to make sure stack creation is started
    wait_for_stack_update(stack_name)
    time.sleep(5)  # Buffer to make sure stack creation is completed
    exit(0)


if __name__ == "__main__":
    main()
