import global_constants, json

from secrets import *
from bot_tasks import *
from global_constants import *
from helper_functions import *

from discord import Activity, Client, Intents


# declare bot intents
# all() enables everything, including the privileged intents: presences, members and message_content
intents = Intents.all()

# initialise client
bot = Client(intents=intents)
global_constants.BOT_INSTANCE = bot


@loop(minutes=1)
async def task_check_major_order():
	endpoint = f"{BASE_API_URL}/v2/Assignment/War/{WAR_ID}"

	order_details = 'NO RESPONSE'
	try:
		order_details = requests.get(endpoint, headers=STANDARD_HEADERS).json()
		await check_major_order(order_details)
		await error_recovery('major_order')

	except Exception as error:
		if await error_handler(error, 'major_order', order_details):
			task_check_major_order.stop()


@loop(minutes=1)
async def task_check_global_event():
	endpoint = f"{BASE_API_URL}/WarSeason/{WAR_ID}/Status"

	war_status = 'NO RESPONSE'
	try:
		war_status = requests.get(endpoint, headers=STANDARD_HEADERS).json()
		await check_global_event(war_status)
		await error_recovery('global_event')

	except Exception as error:
		if await error_handler(error, 'global_event', war_status):
			task_check_global_event.stop()


@loop(minutes=1)
async def task_check_dispatch():
	endpoint = f"{BASE_API_URL}/NewsFeed/{WAR_ID}?fromTimeStamp={global_constants.LATEST_DISPATCH_TIMESTAMP}"

	dispatches = 'NO RESPONSE'
	try:
		dispatches = requests.get(endpoint, headers=STANDARD_HEADERS).json()
		await check_dispatch(dispatches)
		await error_recovery('dispatch')

	except Exception as error:
		if await error_handler(error, 'dispatch', dispatches):
			task_check_dispatch.stop()


@bot.event
async def on_ready():
	# on_ready() may be called more than once, typically whenever the bot momentarily loses connection to Discord 
	# check if this is first time bot is calling on_ready()
	if global_constants.MAIN_CHANNEL:
		return

	print(f"{bot.user} is online.\n")

	# initialise global main channel object
	global_constants.MAIN_CHANNEL = bot.get_channel(MAIN_CHANNEL_ID)

	# initialise empty files if they do not already exist
	for entity_type in ENTITY_TYPES:
		initialise_file_if_empty(entity_type)

	# read in variables from files
	with open(FILE_NAMES['major_order']) as infile:
		data = infile.readline().strip().split(',')
		global_constants.MAJOR_ORDER_ID = data[0]

		# attempt to retrieve major order message, and if it cannot be retrieved, wipe the major order ID so that the bot will output another message
		try:
			global_constants.MAJOR_ORDER_MESSAGE = await global_constants.MAIN_CHANNEL.fetch_message(data[-1])
		except:
			global_constants.MAJOR_ORDER_ID = None

	with open(FILE_NAMES['global_event']) as infile:
		data = infile.readline().strip()
		if data:
			global_constants.LATEST_GLOBAL_EVENT_IDS = json.loads(data)

	with open(FILE_NAMES['dispatch']) as infile:
		data = infile.readline().strip()
		if not data:
			data = '0'
		global_constants.LATEST_DISPATCH_TIMESTAMP = data

	# start tasks
	task_check_dispatch.start()
	task_check_global_event.start()
	task_check_major_order.start()

	# set activity status
	# available ActivityTypes: 0 is gaming (Playing), 1 is streaming (Streaming), 2 is listening (Listening to),
	# 3 is watching (Watching), 4 is custom, 5 is competing (Competing in)
	activity_status = Activity(type=3, name='the Galactic War unfold')
	await global_constants.BOT_INSTANCE.change_presence(activity=activity_status)


# start bot
bot.run(DISCORD_BOT_TOKEN)
