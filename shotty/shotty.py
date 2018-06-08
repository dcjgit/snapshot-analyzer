
import os
os.environ['HTTP_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"
os.environ['HTTPS_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"

import boto3
import click
session = boto3.Session(profile_name='personal')
ec2 = session.resource('ec2')

#The @ is a decorator (wrapper) for our functions
@click.group()
def instances():
    """Commands for instances"""
@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = []

    if project:
        filters = [ {'Name':'tag:Project', 'Values':[project]} ]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    for i in instances:  #ec2.instances is a collection
        if i.public_dns_name:
            dns=i.public_dns_name + " --public"
        else:
            dns= i.private_dns_name + " --private"
        print(', '.join( (i.id,
                          i.instance_type,
                          i.placement['AvailabilityZone'],
                          i.state['Name'],
                          dns))
             )
    return

if __name__ == '__main__':
    #list_instances()
    instances()
    
