import os
import sys
sys.path.append(os.path.dirname(__file__))

from hook_entry import api_hooker, multi_hooker
from presets.hook_flask import flask_hookers
from injections import *

sys.path.pop()
