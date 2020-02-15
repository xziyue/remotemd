from src.custom_server import CustomServer
from src.correct_path import testDir
import os

server = CustomServer('127.0.0.1', 8088, testDir, os.path.abspath('sample.md'))
server.run()