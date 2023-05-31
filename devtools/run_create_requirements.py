import os
import sys

SOURCE_DIR = os.path.abspath(os.path.dirname(__file__) + "/../")
sys.path.append(SOURCE_DIR)

from utils.create_requirements import create_requirements

create_requirements(folder=SOURCE_DIR)
