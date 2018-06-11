import os
os.environ['HTTP_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"
os.environ['HTTPS_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"

import boto3
import botocore
import click

session = boto3.Session(profile_name='personal')
ec2 = session.resource('ec2')

#------------------------------------------------------------------
"""
Helper functions
"""
def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name': 'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'
    
#------------------------------------------------------------------

#@ is a decorator (wrapper) for our functions
#define a group to contain other groups. One main group cli
#and inside it we have other groups

@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help='Only snapshots for project (tag Project:<name>)')
@click.option('--all', 'list_all', default=False, is_flag=True,
              help="List all snapshots for each volume, not just the most recent")

def list_snapshots(project, list_all):
    "List EC2 snapshots"
    instances = filter_instances(project)
    for i in instances:
        #each instance can have a collection of volumes
        for v in i.volumes.all():
            #each volume can have a collection of snapshots
            for s in v.snapshots.all():
                print(", ".join((s.id, v.id, i.id,
                                 s.state, s.progress,
                                 s.start_time.strftime("%c")))
                     )
                if s.state == 'completed' and not list_all:
                    break
                
    return
#-----------------------------------------------------------------------------


@cli.group('volumes')    #this is group in cli group (nested)
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project',default=None,help='Only volumes for project (tag Project:<name>)')
def list_volumes(project):
    "List EC2 volumes"
    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():   #each instance has a collection of volumes
            print(", ".join((
                v.id, i.id, v.state, str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return
#------------------------------------------------------------------------------

@cli.group()
def instances():
    """Commands for instances"""

@instances.command('snapshot', help="Create snapshots of all volumes")
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        
        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print("Skipping {0}, snapshot already in progress".format(v.id))
                continue
            
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by snapshot analyzer")
        
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()
    
    print("Job's done!")
    return
#------------------------------------------------------------------------------


@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    instances = filter_instances(project)
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
#-----------------------------------------------------------------

@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')
def stop_instances(project):
    "Stop EC2 instances"
    instances = filter_instances(project)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}.".format(i.id) + str(e))
            continue

    return
#------------------------------------------------------------------

@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')
def start_instances(project):
    "Start instacnes"
    instances = filter_instances(project)
    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}.".format(i.id) + str(e))
            continue

    return
#--------------------------------------------------------------------

if __name__ == '__main__':
    #list_instances()
    #accepts the list command to execute the code
    #shotty.py list --project=Valkyrie
    #instances()
    cli()
