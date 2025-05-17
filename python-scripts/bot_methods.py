from imports import *


# all bot methods below have to correspond to an item in BOT_COMMAND_LIST
# and must share the same name, followed by '_method'


# display current state of article feeds
async def status_method(message, user_input, flag_presence):
	status_list = [
		'MAJOR_ORDER_ID',
		'LATEST_DISPATCH_TIMESTAMP',
		'LATEST_GLOBAL_EVENT_IDS',
	]

	status_log = '\n\n'.join(f"{name}: {getattr(var_global, name)}" for name in status_list)
	await message.channel.send(file=discord.File(io.StringIO(status_log), filename="status_log.txt"))


# trigger bot self-update
async def update_method(message, user_input, flag_presence):
	if sys.platform != 'linux':
		return

	await message.channel.send('Popping into the tent for a bit!')

	# reset any potential changes to project folder, then pull latest code
	subprocess.run(f"cd {LINUX_ABSOLUTE_PATH} && git reset --hard HEAD && git clean -d -f && git pull", shell=True)

	# restart service
	subprocess.run(['sudo', 'systemctl', 'restart', LINUX_SERVICE_NAME])
