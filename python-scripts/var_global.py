import sys


### LINUX ###

# absolute path to the project folder on the Linux cloud instance
# cannot use os.getcwd() because systemd service runs the script from root directory
LINUX_ABSOLUTE_PATH = '/home/ubuntu/democracy-bot/python-scripts'

# name of the bot service running on the Linux cloud instance
LINUX_SERVICE_NAME = 'democracy-bot.service'



### INIT ###

MAIN_CHANNEL = None

ASYNC_CLIENT = None



### DISCORD ###

# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 1205579694913626142



### MAIN ###

# symbol to signify bot commands
BOT_COMMAND_PREFIX = '.'

# list of bot commands
BOT_COMMAND_LIST = ['status', 'update']

# dictionary of command flags
# each flag can only be a single letter
BOT_COMMAND_FLAGS = {}


# dictionary of the available Discord statuses for the bot
# if activity (key) is meant to be a 'Streaming' activity, then corresponding value is a string URL
# otherwise corresponding value is the respective ActivityType
# available ActivityTypes: 0 is gaming (Playing), 1 is streaming (Streaming), 2 is listening (Listening to),
# 3 is watching (Watching), 4 is custom, 5 is competing (Competing in)
BOT_ACTIVITY_STATUSES = {
	"Strohmann News": 2,
	"the Galactic War unfold": 3,
}



### API ###

# base URL for the API
BASE_API_URL = 'https://api.live.prod.thehelldiversgame.com/api'

# standard headers for HTTP requests
STANDARD_HEADERS = {'Accept-Language': 'en-US'}

# ID of the current War Season
WAR_ID = 801


# list of names for the different entity types
ENTITY_TYPES = ['major_order', 'global_event', 'dispatch']

# dictionary of booleans indicating if errors have occurred for the loop tasks
TASK_ERRORS = {}
for entity_type in ENTITY_TYPES:
	TASK_ERRORS[entity_type] = False



### DISPATCH ###

# timestamp of latest dispatch sent
LATEST_DISPATCH_TIMESTAMP = 0



### EVENTS ###

# list of latest global event IDs
LATEST_GLOBAL_EVENT_IDS = []

# string of the latest event
LATEST_EVENT_STRING = None



### MAJOR ORDER ###

# ID of latest major order
MAJOR_ORDER_ID = None

# entire JSON payload of latest major order
MAJOR_ORDER_PAYLOAD = None

# variable to store Discord message object so that major order expiry time can constantly updated since it usually doesn't count down consistently
# i.e. the expiry time given when the major order is issued is almost always slightly off from the time it actually ends up expiring at
MAJOR_ORDER_MESSAGE = None



### MESSAGES ###

# standard emoji prepended and appended to most voicelines
ATTENTION_EMOJI = '🚨'

# standard footer to end off messages
MESSAGE_FOOTER = '*----------END OF TRANSMISSION----------*'


# dictionary of messages used by the bot
STANDARD_VOICELINES = {
	'major_order_new': 'NEW MAJOR ORDER RECEIVED',
	'global_event_new': 'NEW EVENT DETECTED',
	'dispatch_new': 'DISPATCH RECEIVED',
}
for key, value in STANDARD_VOICELINES.items():
	STANDARD_VOICELINES[key] = f'**{ATTENTION_EMOJI}   {value}   {ATTENTION_EMOJI}**'



### FILES ###

# dictionary of names of storage files used
FILE_NAMES = {
	'major_order': 'current_major_order.txt',
	'global_event': 'latest_global_event.json',
	'dispatch': 'latest_dispatch.txt',
}

# name of folder storing the .txt and .json files
FILE_FOLDER_NAME = 'data-files/'

# automatically prepend folder name to file names
for key, value in FILE_NAMES.items():
	FILE_NAMES[key] = FILE_FOLDER_NAME + value

# automatically prepend home directory to file paths if on Linux
if sys.platform == 'linux':
	parent_directory = '/home/ubuntu/democracy-bot/'
else:
	parent_directory = '../'
for key, value in FILE_NAMES.items():
	FILE_NAMES[key] = parent_directory + value
