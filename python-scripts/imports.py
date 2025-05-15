
# external libraries
import io
import os
import re
import json
import time
import httpx
import random
import discord
import traceback
import subprocess

from discord.ext.tasks import loop


# internal scripts - order of import matters; load the scripts in order of lowest to highest dependency
import var_global
from var_global import *
from var_secret import *

from func_utils import *

from bot_tasks import *

from bot_methods import *
