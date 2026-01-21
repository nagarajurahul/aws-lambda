# This script will search and delete stale volumes, where volumes are not attached to any running instances

import boto3

# def lambda_handler(event,context):
def main():
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
    ec2=boto3.client('ec2')

    # Get all running instances
    running_instances_response=ec2.describe_instances(Filters=[{'Name':"instance-state-name",'Values': ["running"]}])
    running_instances_ids=set()

    # Add ids of running instances to set
    for reservation in running_instances_response["Reservations"]:
        for instance in reservation["Instances"]:
            running_instances_ids.add(instance["InstanceId"])

    print(f"Running instance IDs : {running_instances_ids}")

    # Get all volumes
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_volumes.html
    volumes_response = ec2.describe_volumes()
   
    for volume in volumes_response['Volumes']:
        # print(volume)
        volume_id = volume['VolumeId']
        print(f"Volume: {volume_id}")

        # Delete if not attached
        try:
            attachments = volume.get("Attachments", [])

            # Check if volume is attached to any instance, if not delete it
            if not attachments:
                print(f"STALE VOLUME (volume is detached from instance): {volume_id}")
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/delete_volume.html
                ec2.delete_volume(VolumeId=volume_id)
                continue

            attached_instance = attachments[0]["InstanceId"]

            # Check if instance is running, if not delete it
            if attached_instance not in running_instances_ids:
                print(f"STALE VOLUME (instance stopped): {volume_id}")
                # We cannot delete it, as it is still attached to instance (even though instance is not running)
                # We need to first detach it and then delete it
                # ec2.delete_volume(VolumeId=volume_id)
                print("Cannot be deleted even though instance is stopped, as it is still attached")
            else:
                print(f"NOT STALE VOLUME (instance not stopped): {volume_id}")
  
        except ec2.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidVolume.NotFound":
                pass
            else:
                raise    

if __name__ == "__main__":
    main()