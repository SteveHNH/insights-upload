import argparse
import json
import yaml
import subprocess
import sys
import logging

logger = logging.getLogger('podman-ctl')

parser = argparse.ArgumentParser()
parser.add_argument('state',
                    help='Set the state of the stack',
                    choices=['up', 'down'])
parser.add_argument('--build', '-b',
                    action='store_true',
                    help='build images')
parser.add_argument('--compose_file',
                    default='./docker-compose.yml',
                    help='docker compose file')
args = parser.parse_args()
running = []
revisit = []

with open(args.compose_file, 'r') as f:
    compose = yaml.safe_load(f.read())

# if --build is called, build the images first
if args.build or args.b:
    for i in compose['services']:
        for service, params in i.items():
            if 'build' in params:
                logger.info('Building Service: {}'.format(service))
                builder = subprocess.Popen(['buildah', 'bud', params['build']],
                                           stderr=subprocess.STDOUT, 
                                           stdout=subprocess.PIPE,
                                           universal_newlines=True)
                for line in iter(builder.stdout.readline, ''):
                    sys.stdout.write(line)
        

for i in compose['services']:
    for service, params in i.items():
        if 'depends_on' in params and any(params['depends_on']) not in running:
            revisit.append(service)
    