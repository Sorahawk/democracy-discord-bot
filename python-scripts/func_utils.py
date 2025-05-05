from imports import *


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
	error_string = f"Unexpected error in `check_{entity_type}()`: {full_trace}"

	if "RemoteDisconnected" in error_string:  # ignore sporadic connection issues
		return False
	elif "Expecting value: line 1 column 1 (char 0)" in error_string:  # ignore JSONDecodeError
		return False

	await var_global.MAIN_CHANNEL.send(error_string)
	await var_global.MAIN_CHANNEL.send(f"Payload: ```{payload}```")

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
