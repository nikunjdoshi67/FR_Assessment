# -*- coding: utf-8 -*-
"""FR_Assessment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Og322n9EqeRgWZDiKGforMYKkVtQHnOr

# FR Assessment
I have created this ipynb file which can be used as a Google colab notebook to deploy an ec2 instance on cloud.

This notebook performs below steps
1. Run your program
2. Deploy the virtual machine
3. SSH into the instance as user1 and user2
4. Read from and write to each of two volumes

We have used AWS programmatic access for connecting with AWS and used libraries such as boto3, parimiko for ssh onto the environment
"""

# If deploying using Google Colan below code will be used, else comment this code. And deploy using python script
from google.colab import drive
drive.mount('/content/drive/')

#Set your project path 
project_path = '/content/drive/My Drive/FR_Assessment/'

pip install awscli boto3 ##Used to connect with awscli using boto3

pip install paramiko ## ssh client for python to connect with ec2

import boto3

## ACCESS_KEY and SECRET ACCESS_KEY for account where you need to deploy the code is to be added in below variables
aws_access_key_id = 'ACCESS_KEY'
aws_secret_access_key = 'SECRET_KEY'
region_name = 'us-east-1'

session = boto3.session.Session(aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=region_name)

ec2client = session.client('ec2')

# create an EBS volume, 10G size
ebs_vol = ec2client.create_volume(
        Size=10,
        AvailabilityZone='us-east-1a',
        VolumeType='gp2'

    )

volume_id = ebs_vol['VolumeId']

# check that the EBS volume has been created successfully
if ebs_vol['ResponseMetadata']['HTTPStatusCode'] == 200:
  print ("Successfully created Volume! " + volume_id)

import boto3

user_data = '''<script>
#!/bin/bash
echo 'test' > /tmp/hello
</script>'''

# create a new EC2 instance
ec2_instance = ec2client.run_instances(
     ImageId='ami-0742b4e673072066f', 
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.micro',
     KeyName='FRkeypair.pem',
     Placement={'AvailabilityZone': 'us-east-1a'},
     UserData=user_data
 )

# check if EC2 instance was created successfully
if ec2_instance['ResponseMetadata']['HTTPStatusCode'] == 200:
  print ("Successfully created instance! " + ec2_instance['Instances'][0]['InstanceId'])

# attaching EBS volume to our EC2 instance
attach_resp = ec2client.attach_volume(
  VolumeId=volume_id,
  InstanceId=ec2_instance['Instances'][0]['InstanceId'],
  Device='/dev/xvdb'
    )

def ssh_connect_with_retry(ssh, ip_address, retries):
    if retries > 3:
        return False
    privkey = paramiko.RSAKey.from_private_key_file(
        'FRkeypair.pem')
    interval = 5
    try:
        retries += 1
        print('SSH into the instance: {}'.format(ip_address))
        ssh.connect(hostname=ip_address,
                    username='ubuntu', pkey=privkey)
        return True
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(ip_address))
        ssh_connect_with_retry(ssh, ip_address, retries)

import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
## ssh onto ec2 instance
ip_address =  ec2_instance.get['PublicIpAddress']
ssh_connect_with_retry(ssh, ip_address, 0)

stdin, stdout, stderr = ssh.exec_command(commands)
print('stdout:', stdout.read())
print('stderr:', stderr.read())