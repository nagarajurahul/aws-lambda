# This script will search for stale snapshots, where volumes are not attached to any running instances and delete them

import boto3

# def lambda_handler(event,context):
def main():
    ec2=boto3.client('ec2')
    running_instances_response=ec2.describe_instances(Filters=[{'Name':"instance-state-name",'Values': ["running"]}])
    running_instances=set()


    for reservation in running_instances_response["Reservations"]:
        for instance in reservation["Instances"]:
            running_instances.add(instance["InstanceId"])

    print(running_instances)

    snapshots_response = ec2.describe_snapshots()
    print(snapshots_response)

if __name__ == "__main__":
    main()