import boto3

# def lambda_handler(event,context):
def main():
    ec2=boto3.client('ec2')
    instances_response=ec2.describe_instances(Filters=[{'Name':"instance-state-name",'Values': ["running"]}])
    running_instances=set()


    for reservation in instances_response["Reservations"]:
        for instance in reservation["Instances"]:
            running_instances.add(instance["InstanceId"])

    print(running_instances)

    volumes_response = ec2.describe_volumes()
    print(volumes_response)

if __name__ == "__main__":
    main()