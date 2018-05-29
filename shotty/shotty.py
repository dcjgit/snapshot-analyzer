
import os
os.environ['HTTP_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"
os.environ['HTTPS_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"

import boto3
import click
session = boto3.Session(profile_name='personal')
ec2 = session.resource('ec2')

#The @ is a decorator (wrapper) for our functions
@click.command()
def list_instances():
    "List EC2 instances"
    for i in ec2.instances.all():
        print(', '.join( (i.id,
                          i.instance_type,
                          i.placement['AvailabilityZone'],
                          i.state['Name'],
                          i.public_dns_name))
             )
    return

if __name__ == '__main__':
    list_instances()
