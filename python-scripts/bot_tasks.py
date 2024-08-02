import global_constants, json, requests, time

from global_constants import *
from helper_functions import *

from discord.ext.tasks import loop


# outputs new major orders, updates expiry time of existing major orders, and sends results of expired major orders
async def check_major_order(order_details):
	if order_details:
		order_details = order_details[0]
		order_id = str(order_details['id32'])

		# update major order progress
		order_progress = order_details['progress']
		global_constants.MAJOR_ORDER_ACHIEVED = True
		for subobjective in order_progress:
			if subobjective != 1:
				global_constants.MAJOR_ORDER_ACHIEVED = False
				break

		# update major order payload
		global_constants.MAJOR_ORDER_PAYLOAD = order_details

		# form major order string
		expiry_timestamp = int(time.time()) + order_details['expiresIn']
		discord_timestamp = f"<t:{expiry_timestamp}:F>"

		# the overrideBrief and taskDescription values are somehow not returned in the response every now and then
		brief = ''
		if 'overrideBrief' in order_details['setting']:
			brief = order_details['setting']['overrideBrief']

		task_description = ''
		if 'taskDescription' in order_details['setting']:
			task_description = order_details['setting']['taskDescription']
			if task_description:  # in case the description is empty, do not add the extra lines
				task_description += '\n\n'

		message = f"\n{brief}\n\n{task_description}".replace('\n', '\n> ')
		message = convert_tags_to_bold(message)
		message += f"Order Expiry: {discord_timestamp}"  # append timestamp only after checking for HTML tags

		header = STANDARD_VOICELINES['major_order_new']
		major_order_string = f"{header}\n{message}\n\n{MESSAGE_FOOTER}"

		# if major order message was sent before, edit message with the updated expiry time
		if order_id == global_constants.MAJOR_ORDER_ID and global_constants.MAJOR_ORDER_MESSAGE:
			await global_constants.MAJOR_ORDER_MESSAGE.edit(content=major_order_string)

		else:  # otherwise, output new major order
			sent_message = await global_constants.MAIN_CHANNEL.send(major_order_string)

			# update variables
			global_constants.MAJOR_ORDER_ID = order_id
			global_constants.MAJOR_ORDER_MESSAGE = sent_message

			with open(FILE_NAMES['major_order'], 'w') as outfile:
				outfile.write(f"{order_id}, {sent_message.id}")
		return

	# if not order_details (no major order active), then code below executes
	if not global_constants.MAJOR_ORDER_ID:
		return

	# major order just expired; print results
	order_expiry = global_constants.MAJOR_ORDER_PAYLOAD['expiresIn']

	if order_expiry < 60 and not global_constants.MAJOR_ORDER_ACHIEVED:
		result = 'FAILURE'
	else:
		result = 'SUCCESS'

	description = global_constants.MAJOR_ORDER_PAYLOAD['setting']['taskDescription']
	result = f"Status: **{result}**"

	header = f"{STANDARD_VOICELINES['major_order_end']}\n"
	await global_constants.MAIN_CHANNEL.send(f"{header}\n{description}\n\n{result}\n\n{MESSAGE_FOOTER}")

	# archive payload
	with open(FILE_NAMES['major_order_archive'], 'a') as outfile:
		outfile.write(f"{json.dumps(global_constants.MAJOR_ORDER_PAYLOAD)}\n\n")

	# reset global variables
	open(FILE_NAMES['major_order'], 'w').close()
	global_constants.MAJOR_ORDER_ID = None
	global_constants.MAJOR_ORDER_ACHIEVED = True
	global_constants.MAJOR_ORDER_PAYLOAD = None
	global_constants.MAJOR_ORDER_MESSAGE = None


# outputs new global events
async def check_global_event(war_status):
	if not war_status['globalEvents']:
		return

	for event_details in war_status['globalEvents']:
		event_id = str(event_details['eventId'])

		# ignore events that were already covered
		if event_id in global_constants.LATEST_GLOBAL_EVENT_IDS:
			continue

		global_constants.LATEST_GLOBAL_EVENT_IDS.append(event_id)

		with open(FILE_NAMES['global_event'], 'w') as outfile:
			outfile.write(json.dumps(global_constants.LATEST_GLOBAL_EVENT_IDS))

		message = event_details['title']
		if '**' not in message:  # bold the title only if does not already contain bold tags
			message = f"**{message}**"

		# check if message field is empty
		if event_details['message']:
			message += f"\n\n{event_details['message']}"

		# check if current event message is exactly the same as the previous one, and ignore it if so
		# this is because free stratagem events tend to come in pairs for some reason
		if message != global_constants.LATEST_EVENT_STRING:
			global_constants.LATEST_EVENT_STRING = message
			await send_formed_message(message, 'global_event_new')


# outputs new dispatches
async def check_dispatch(dispatches):
	if not dispatches:
		return

	for dispatch in dispatches:
		if 'message' not in dispatch or not dispatch['message']:
			continue

		timestamp = dispatch['published']
		message = dispatch['message']

		await send_formed_message(message, 'dispatch_new')

	global_constants.LATEST_DISPATCH_TIMESTAMP = str(timestamp + 1)
	with open(FILE_NAMES['dispatch'], 'w') as outfile:
		outfile.write(str(timestamp + 1))
