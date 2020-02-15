import sys
import os
import json

# configure PYTHONPATH
_projDir, _ = os.path.split(__file__)
_projDir = os.path.abspath(_projDir)
sys.path.insert(0, _projDir)

from src.correct_path import testDir, projectDir

if len(sys.argv) < 2:
    print('invalid number of arguments')
    exit(0)

targetFile = sys.argv[1]

configFile = os.path.join(projectDir, 'config.json')

try:
    cIndex = sys.argv.index('-c')
    configFile = os.path.join(projectDir, sys.argv[cIndex + 1])
except ValueError as e:
    pass
    
assert os.path.exists(configFile)
with open(configFile, 'r') as infile:
    config = json.load(infile)

from src.custom_server import CustomServer

if len(config['base_dir']) == 0:
    config['base_dir'] = testDir

# expand user
baseDir = os.path.expanduser(config['base_dir'])

server = CustomServer(config['ip'], config['port'], baseDir, targetFile, additionalHead=config['additional_head'])
server.run()