import boto3
import datetime

ec2 = boto3.client("ec2")
cloudwatch = boto3.client("cloudwatch")

def handler(event, context):
    print("Checking for idle EC2 instances...")

    # Find instances with Shutdown: yes
    instances = ec2.describe_instances(
        Filters=[
            {"Name": "tag:Shutdown", "Values": ["yes"]},
            {"Name": "instance-state-name", "Values": ["running"]}
        ]
    )

    now = datetime.datetime.utcnow()
    start_time = now - datetime.timedelta(minutes=30)

    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]

            # Get average CPU utilization over last 30 minutes
            metrics = cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_time,
                EndTime=now,
                Period=300,  # 5 min period
                Statistics=["Average"]
            )

            datapoints = metrics.get("Datapoints", [])
            if not datapoints:
                print(f"No CPU data for {instance_id}, skipping.")
                continue

            avg_cpu = sum([dp["Average"] for dp in datapoints]) / len(datapoints)

            print(f"Instance {instance_id} average CPU: {avg_cpu:.2f}%")

            if avg_cpu < 5.0:  # threshold for idle
                print(f"Stopping idle instance {instance_id}")
                ec2.stop_instances(InstanceIds=[instance_id])
            else:
                print(f"Instance {instance_id} is active, skipping.")

