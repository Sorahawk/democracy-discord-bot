from sys import platform


### DISCORD ###

# ID of default Discord server channel that will receive notifications
MAIN_CHANNEL_ID = 1205579694913626142

# main channel object, to be initialised when the bot calls on_ready()
MAIN_CHANNEL = None

# Discord server role name to ping for notifications
NOTIFY_ROLE_NAME = '<@&1218425149821550682>'


### MAIN ###

BOT_INSTANCE = None

# symbol to signify bot commands
BOT_COMMAND_PREFIX = '.'

# list of bot commands
BOT_COMMAND_LIST = []

# base URL for the API
BASE_API_URL = 'https://api.live.prod.thehelldiversgame.com/api'

# standard headers for HTTP requests
STANDARD_HEADERS = {'Accept-Language': 'en-US'}

# ID of the current War Season
WAR_ID = 801

# timestamp of latest dispatch sent
LATEST_DISPATCH_TIMESTAMP = 0

# list of latest global event IDs
LATEST_GLOBAL_EVENT_IDS = []

# ID of latest major order
MAJOR_ORDER_ID = None

# boolean to track if latest major order objective has been achieved
MAJOR_ORDER_ACHIEVED = True

# entire JSON payload of latest major order
MAJOR_ORDER_PAYLOAD = None

# variable to store Discord message object so that major order expiry time can constantly updated since it usually doesn't count down consistently
# i.e. the expiry time given when the major order is issued is almost always slightly off from the time it actually ends up expiring at
MAJOR_ORDER_MESSAGE = None

# list of names for the different entity types
ENTITY_TYPES = ['major_order', 'global_event', 'dispatch']

# dictionary of booleans indicating if errors have occurred for the loop tasks
TASK_ERRORS = {}
for entity_type in ENTITY_TYPES:
	TASK_ERRORS[entity_type] = False

# dictionary of names of storage files used
FILE_NAMES = {
	'major_order': 'current_major_order.txt',
	'major_order_archive': 'major_order_archive.json',
	'global_event': 'latest_global_event.json',
	'dispatch': 'latest_dispatch.txt',
}

# name of folder storing the .txt and .json files
FILE_FOLDER_NAME = 'data-files/'

# automatically prepend folder name to file names
for key, value in FILE_NAMES.items():
	FILE_NAMES[key] = FILE_FOLDER_NAME + value

# automatically prepend home directory to file paths if on Linux
if platform == 'linux':
	parent_directory = '/home/ubuntu/democracy-bot/'
else:
	parent_directory = '../'
for key, value in FILE_NAMES.items():
	FILE_NAMES[key] = parent_directory + value


# standard emoji prepended and appended to most voicelines
ATTENTION_EMOJI = '🚨'

# standard footer to end off messages
MESSAGE_FOOTER = '*----------END OF TRANSMISSION----------*'

# dictionary of messages used by the bot
STANDARD_VOICELINES = {
	'major_order_new': 'NEW MAJOR ORDER RECEIVED',
	'major_order_end': 'MAJOR ORDER CONCLUDED',
	'global_event_new': 'NEW EVENT DETECTED',
	'dispatch_new': 'DISPATCH RECEIVED',
}
for key, value in STANDARD_VOICELINES.items():
	STANDARD_VOICELINES[key] = f'**{ATTENTION_EMOJI}   {value}   {ATTENTION_EMOJI}**'
