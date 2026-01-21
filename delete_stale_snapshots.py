# This script will search for stale snapshots, where volumes are not attached to any running instances and delete them

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

    # Get all snapshots
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_snapshots.html
    snapshots_response = ec2.describe_snapshots(OwnerIds=['self'])
   
    for snapshot in snapshots_response['Snapshots']:
        # print(snapshot)
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot.get('VolumeId')
        print(f"Volume: {volume_id}, Snapshot:{snapshot_id}")

        # Check if volume exists
        try:
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_volumes.html
            volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
            volume = volume_response["Volumes"][0]

            attachments = volume.get("Attachments", [])

            # Check if volume is attached to any instance, if not delete it
            if not attachments:
                print(f"STALE SNAPSHOT (volume is detached from instance): {snapshot_id}")
                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/delete_snapshot.html
                ec2.delete_snapshot(SnapshotId=snapshot["SnapshotId"])
                continue

            attached_instance = attachments[0]["InstanceId"]

            # Check if instance is running, if not delete it
            if attached_instance not in running_instances_ids:
                print(f"STALE SNAPSHOT (instance stopped): {snapshot_id}")
                ec2.delete_snapshot(SnapshotId=snapshot["SnapshotId"])
            else:
                print(f"NOT STALE SNAPSHOT (instance not stopped): {snapshot_id}")
             
        except ec2.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidVolume.NotFound":
                print(f"STALE SNAPSHOT (volume deleted): {snapshot_id}")
                ec2.delete_snapshot(SnapshotId=snapshot["SnapshotId"])
            else:
                raise    

if __name__ == "__main__":
    main()