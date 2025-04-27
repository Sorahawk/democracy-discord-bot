from imports import *


# declare bot intents
# all() enables everything, including the privileged intents: presences, members and message_content
intents = discord.Intents.all()

# initialise client
bot = discord.Client(intents=intents)
var_global.BOT_INSTANCE = bot


# standard function for the polling tasks that includes standard error handling
async def polling(func, task, endpoint, keyword):
	response = 'NO RESPONSE'
	try:
		response = requests.get(endpoint, headers=STANDARD_HEADERS).json()
		await func(response)
		await error_recovery(keyword)

	except Exception as error:
		if await error_handler(error, keyword, response):
			task.stop()


@loop(minutes=1)
async def task_check_major_order():
	endpoint = f"{BASE_API_URL}/v2/Assignment/War/{WAR_ID}"
	keyword = 'major_order'
	await polling(check_major_order, task_check_major_order, endpoint, keyword)


@loop(minutes=1)
async def task_check_global_event():
	endpoint = f"{BASE_API_URL}/WarSeason/{WAR_ID}/Status"
	keyword = 'global_event'
	await polling(check_global_event, task_check_global_event, endpoint, keyword)


@loop(minutes=1)
async def task_check_dispatch():
	endpoint = f"{BASE_API_URL}/NewsFeed/{WAR_ID}?fromTimeStamp={var_global.LATEST_DISPATCH_TIMESTAMP}"
	keyword = 'dispatch'
	await polling(check_dispatch, task_check_dispatch, endpoint, keyword)


# automatically rotate bot's Discord status every 10 minutes
@loop(minutes=10)
async def task_rotate_status():
	activity, activity_type = random.choice(list(BOT_ACTIVITY_STATUSES.items()))

	if isinstance(activity_type, str):
		activity_status = discord.Streaming(url=activity_type, name=activity)
	else:
		activity_status = discord.Activity(type=activity_type, name=activity)

	await var_global.BOT_INSTANCE.change_presence(activity=activity_status)


@bot.event
async def on_ready():
	# on_ready() may be called more than once, typically whenever the bot momentarily loses connection to Discord 
	# check if this is first time bot is calling on_ready()
	if var_global.MAIN_CHANNEL:
		return

	print(f"{bot.user} is online.\n")

	# initialise global main channel object
	var_global.MAIN_CHANNEL = bot.get_channel(MAIN_CHANNEL_ID)

	# initialise empty files if they do not already exist
	for entity_type in ENTITY_TYPES:
		initialise_file_if_empty(entity_type)

	# read in variables from files
	with open(FILE_NAMES['major_order']) as infile:
		data = infile.readline().strip().split(',')
		var_global.MAJOR_ORDER_ID = data[0]

		# attempt to retrieve major order message, and if it cannot be retrieved, wipe the major order ID so that the bot will output another message
		try:
			var_global.MAJOR_ORDER_MESSAGE = await var_global.MAIN_CHANNEL.fetch_message(data[-1])
		except:
			var_global.MAJOR_ORDER_ID = None

	with open(FILE_NAMES['global_event']) as infile:
		if (data := infile.readline().strip()):
			var_global.LATEST_GLOBAL_EVENT_IDS = json.loads(data)

	with open(FILE_NAMES['dispatch']) as infile:
		if not (data := infile.readline().strip()):
			data = '0'
		var_global.LATEST_DISPATCH_TIMESTAMP = data

	# start tasks
	task_check_dispatch.start()
	task_check_global_event.start()
	task_check_major_order.start()
	task_rotate_status.start()


@bot.event
async def on_message(message):
	prefix_length = len(BOT_COMMAND_PREFIX)  # prefix might not always be single character

	# ignore any messages if bot is not ready, messages sent from the bot itself and messages that don't start with the command prefix
	if not bot.is_ready() or message.author == bot.user or message.content[:prefix_length] != BOT_COMMAND_PREFIX:
		return

	# process commands
	contents = message.content[prefix_length:].lower().split()

	# update command
	if contents[0] in ['update'] and sys.platform == 'linux':
		await message.channel.send('Receiving updates from the Ministry of Truth.')

		# reset any changes that could have been made to the project folder and pull latest code
		subprocess.run(f"cd {LINUX_ABSOLUTE_PATH} && git reset --hard HEAD && git clean -d -f && git pull", shell=True)

		# restart service
		subprocess.run(f"sudo systemctl restart {LINUX_SERVICE_NAME}", shell=True)


# start bot
bot.run(DISCORD_BOT_TOKEN)
