from imports import *


# determines if user input contains any command
# if no command detected, returns None
# otherwise, returns a tuple containing:
# first, the name of the corresponding method of the bot command as a string to be called by eval()
# second, the user input stripped of command word
def check_command(user_input):
	# isolate first word
	keyword = user_input.split()[0].lower()

	if keyword in BOT_COMMAND_LIST:
		# remove command word from user input
		sliced_input = re.sub(keyword, '', user_input, flags=re.IGNORECASE).strip()
		return f"{keyword}_method", sliced_input


# checks for presence of any command flags in user input
# returns a tuple containing:
# first, a dictionary of booleans indicating presence of command flags
# second, the user input stripped of flags
def check_flags(user_input):
	# insert surrounding whitespace so leading and trailing flags can still be detected
	user_input = f" {user_input} "

	# generate flag presence dictionary
	flag_presence = {flag: True if f" -{letter} " in user_input.lower() else False for flag, letter in BOT_COMMAND_FLAGS.items()}

	# remove all 'flags', a dash followed by a single letter, even if they are not valid
	# each whitespace within input is duplicated so that all present flags can be matched by the regex properly
	user_input = re.sub(' -[a-z] ', ' ', ' ' + user_input.replace(' ', '  ') + ' ', flags=re.IGNORECASE)

	# remove excess whitespace
	user_input = ' '.join(user_input.split())

	return flag_presence, user_input


# returns a Discord File object
def generate_file(content, filename):
	return discord.File(io.StringIO(content), filename=filename)


# initialises an empty file if the specified file does not already exist
def initialise_file_if_empty(entity_type):
	if not os.path.exists(FILE_NAMES[entity_type]):
		open(FILE_NAMES[entity_type], 'w').close()


# converts HTML tags from API payload to bolded text
def convert_tags_to_bold(message):
	return re.sub(r'<\S*?>', '**', message)


# resets major order global variables
def reset_major_order_var():
	open(FILE_NAMES['major_order'], 'w').close()
	var_global.MAJOR_ORDER_ID = None
	var_global.MAJOR_ORDER_PAYLOAD = None
	var_global.MAJOR_ORDER_MESSAGE = None


# sends message following the standard format of header - indented message - footer
async def send_formed_message(message, header_voiceline_key):
	message = f"\n{message}".replace('\n', '\n> ')
	message = convert_tags_to_bold(message)

	header = STANDARD_VOICELINES[header_voiceline_key]
	await var_global.MAIN_CHANNEL.send(f"{header}\n{message}\n\n{MESSAGE_FOOTER}")


# standard task error handler
async def error_handler(e, entity_type, payload):
	full_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
	
	if "RemoteDisconnected" in full_trace:  # ignore sporadic connection issues
		return False
	elif "Expecting value: line 1 column 1 (char 0)" in full_trace:  # ignore JSONDecodeError
		return False

	error_string = f"Unexpected error in `check_{entity_type}()`:"
	await var_global.MAIN_CHANNEL.send(error_string, file=generate_file(full_trace, 'traceback.txt'))
	
	if 'NO RESPONSE' not in payload:
		await var_global.MAIN_CHANNEL.send("Payload:", file=generate_file(json.dumps(payload), f"{entity_type}.json"))

	# stop task from re-execution after one retry
	if var_global.TASK_ERRORS[entity_type]:
		await var_global.MAIN_CHANNEL.send(f"`check_{entity_type}()` has failed twice. Disabling task pending further investigation.")
		return True
	else:
		var_global.TASK_ERRORS[entity_type] = True


# restores the task back to fully-functioning status
async def error_recovery(entity_type):
	if var_global.TASK_ERRORS[entity_type]:
		var_global.TASK_ERRORS[entity_type] = False
		await var_global.MAIN_CHANNEL.send(f"`check_{entity_type}()` is functioning now.")
