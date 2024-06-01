import global_constants, os, re

from global_constants import *



# initialises an empty file if the specified file does not already exist
def initialise_file_if_empty(entity_type):
	if not os.path.exists(FILE_NAMES[entity_type]):
		open(FILE_NAMES[entity_type], 'w').close()


# converts HTML tags from API payload to bolded text
def convert_tags_to_bold(message):
	return re.sub(r'<\S*?>', '**', message)


# sends message following the standard format of header - indented message - footer
async def send_formed_message(message, header_voiceline_key):
	message = f"\n{message}".replace('\n', '\n> ')
	message = convert_tags_to_bold(message)

	header = STANDARD_VOICELINES[header_voiceline_key]
	await global_constants.MAIN_CHANNEL.send(f"{header}\n{message}\n\n{MESSAGE_FOOTER}")


# standard task error handler
async def error_handler(exception, entity_type, payload):
	await global_constants.MAIN_CHANNEL.send(f"Unexpected error in `check_{entity_type}()`: {exception}")
	await global_constants.MAIN_CHANNEL.send(f"Payload: ```{payload}```")

	# stop task from re-execution after one retry
	if global_constants.TASK_ERRORS[entity_type]:
		return True
	else:
		global_constants.TASK_ERRORS[entity_type] = True


# restores the task back to fully-functioning status
async def error_recovery(entity_type):
	if global_constants.TASK_ERRORS[entity_type]:
		global_constants.TASK_ERRORS[entity_type] = False
		await global_constants.MAIN_CHANNEL.send(f"`check_{entity_type}()` is functioning now.")
