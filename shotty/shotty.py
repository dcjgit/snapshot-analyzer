
import os
os.environ['HTTP_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"
os.environ['HTTPS_PROXY']="http://nibr-proxy.global.nibr.novartis.net:2011"

import boto3

if __name__ == '__main__':
    session = boto3.Session(profile_name='personal')
    ec2 = session.resource('ec2')

    print('The following are the instances in my Personal acccount dev-dj')
    for i in ec2.instances.all():
        print(i)
