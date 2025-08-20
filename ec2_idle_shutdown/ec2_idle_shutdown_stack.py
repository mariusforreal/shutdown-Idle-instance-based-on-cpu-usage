from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
)
from constructs import Construct

class Ec2IdleShutdownStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function that will stop idle EC2 instances
        shutdown_lambda = _lambda.Function(
            self, "Ec2IdleShutdownLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.minutes(5),
        )

        # Permissions for EC2 and CloudWatch
        shutdown_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "ec2:DescribeInstances",
                "ec2:StopInstances",
                "cloudwatch:GetMetricStatistics"
            ],
            resources=["*"]
        ))

        # EventBridge rule to trigger Lambda every 5 minutes
        rule = events.Rule(
            self, "Ec2IdleShutdownRule",
            schedule=events.Schedule.rate(Duration.minutes(5))
        )
        rule.add_target(targets.LambdaFunction(shutdown_lambda))

