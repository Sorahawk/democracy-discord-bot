import global_constants, json, requests, time

from global_constants import *
from helper_functions import *

from discord.ext.tasks import loop


# outputs new major orders, updates expiry time of existing major orders, and sends results of expired major orders
async def check_major_order(order_details):
	if order_details:
		order_details = order_details[0]
		order_id = str(order_details['id32'])

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
		if 'taskDescription' in order_details['setting'] and order_details['setting']['taskDescription'] != order_details['setting']['overrideBrief']:
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
			try:
				await global_constants.MAJOR_ORDER_MESSAGE.edit(content=major_order_string)
			except:
				# reset global variables if Discord message cannot be located
				reset_major_order_var()
				raise Exception('Discord message for current Major Order cannot be found.')

		else:  # otherwise, output new major order
			sent_message = await global_constants.MAIN_CHANNEL.send(major_order_string)

			# update variables
			global_constants.MAJOR_ORDER_ID = order_id
			global_constants.MAJOR_ORDER_MESSAGE = sent_message

			with open(FILE_NAMES['major_order'], 'w') as outfile:
				outfile.write(f"{order_id}, {sent_message.id}")
		return

	if global_constants.MAJOR_ORDER_ID:
		# archive payload
		with open(FILE_NAMES['major_order_archive'], 'a') as outfile:
			outfile.write(f"{json.dumps(global_constants.MAJOR_ORDER_PAYLOAD)}\n\n")

		# reset global variables
		reset_major_order_var()


# outputs new global events
async def check_global_event(war_status):
	if not war_status or not war_status['globalEvents']:
		return

	for event_details in war_status['globalEvents']:
		event_id = str(event_details['eventId'])

		# ignore events that were already covered
		if event_id in global_constants.LATEST_GLOBAL_EVENT_IDS:
			continue

		global_constants.LATEST_GLOBAL_EVENT_IDS.append(event_id)

		with open(FILE_NAMES['global_event'], 'w') as outfile:
			outfile.write(json.dumps(global_constants.LATEST_GLOBAL_EVENT_IDS))

		message = ''
		if 'title' in event_details:
			message = convert_tags_to_bold(event_details['title'])

			# add on MO prefix to subheader for MO events
			# flag 1 is briefing, 2 is success and 3 is failed
			if event_details['flag'] in [1, 2, 3]:
				message = f"MAJOR ORDER {message}"

			if '**' not in message:  # bold the title only if does not already contain bold tags
				message = f"**{message}**"

		# check if message field is empty
		if 'message' in event_details and event_details['message']:
			message += f"\n\n{event_details['message']}"

		if not message.strip():
			continue

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
		timestamp = dispatch['published']

		if 'message' not in dispatch or not dispatch['message']:
			continue

		message = dispatch['message']
		await send_formed_message(message, 'dispatch_new')

	global_constants.LATEST_DISPATCH_TIMESTAMP = str(timestamp + 1)
	with open(FILE_NAMES['dispatch'], 'w') as outfile:
		outfile.write(str(timestamp + 1))
