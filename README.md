# Architecture

This repo contains the full source code of the `time` service, and infrastructure code to package it as container and deploy to HA ECS cluster. This solution archtitecture is inspired by the AWS ECS Reference Architecture. Infrastructure components deployed are:

* VPC, subnets, and security groups (only port 80 publicly exposed)
* 2 x Public subnets (in 2 AZs) with NAT gateways
* 2 x Private subnets (in 2 AZs) with an auto-scaling ECS cluster
* Application Load Balancer

# Provisioning

First time setup instructions

## First Time Only

Note In the below instructions, the name `et-ecs-cfn` is used to create an S3 bucket. This name is assumed to be globally unique in the AWS cloud. You can use any other name throughout the instructions but will need to edit the `TemplateURL` parameter in `master.yaml` file accordingly

```bash
git clone https://github.com/kim0/devops-coding-challenge
cd devops-coding-challenge
aws s3 mb s3://et-ecs-cfn --region eu-west-1
aws s3 sync . s3://et-ecs-cfn

aws cloudformation create-stack --stack-name ettrial02 --template-body file://master.yaml --on-failure DO_NOTHING --capabilities CAPABILITY_NAMED_IAM
```

Monitor stack deployment progress through the AWS console web UI till it is completed. Now we setup your docker to authenticate to ECR registry, then build and push docker image.

Note: In the below instructions, you need to replace `$AWSACCTNUM` with your AWS account number. Also, you may need to change the AWS region if needed.

```bash
$(aws ecr get-login --no-include-email --region eu-west-1)
cd services/website-service/src
docker build -t etrepo .

docker tag etrepo:1.0.0 $AWSACCTNUM.dkr.ecr.eu-west-1.amazonaws.com/etrepo:1.0.0

docker push $AWSACCTNUM.dkr.ecr.eu-west-1.amazonaws.com/etrepo:1.0.0
```

## Continuous Deployment

This section is used both in the cases of continuing the first-time deployment, or for further deployment in readily existing infrastructure

* Edit services/website-service/service.yaml, adjust the `Image` property under the `TaskDefinition` to point to the correct code/docker image version you just built and pushed

```bash
aws s3 sync . s3://et-ecs-cfn

aws cloudformation update-stack --stack-name ettrial02 --template-body file://master.yaml --capabilities CAPABILITY_NAMED_IAM
```

Monitor stack updates through the web UI. Eventually you can get the URL endpoint of the service through the outputs section of the main cloudformation stack. The below command can also be used

```bash
aws cloudformation describe-stacks --stack-name ettrial02
```

# Health Check

This repo provides a python based external health checker. It connects to the time service, retrieves the service response, unmarshalls that into a python datetime object. Then it computes the difference between the local clock and the time object from the service. If the absolute value of the time difference is more than one second, the service health is assumed UNHEALTHY. Exit status is non-zero for any error case. The script should be called with the URL of the time service as the first argument. Here is a sample usage:

```bash
chmod +x ./healthcheck.py
./healthcheck.py http://ettrial02-40370729.eu-west-1.elb.amazonaws.com/now
```

For monitoring purposes, you need to only depend on the exit status. Anything but zero means unhealthy or something went wrong!
