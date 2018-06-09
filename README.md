# snapshot-analyzer
Demo project to manage AWS EC2 instance snapshots

## About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

shotty uses the configuration file created by the AWS CLI. Example, 'personal' profile

`aws configure --profile personal`

## Running
python shotty/shotty.py <command> < --project=<name of project> >
*command* is list, start, or stop
*project* is optional

Example:
python shotty/shotty.py list --project=Valkyrie
python shotty/shotty.py start --project=Valkyrie
python shotty/shotty.py stop --project=Valkyrie

## Help
Each command has its own help
Example:
python shotty/python.py list --help
