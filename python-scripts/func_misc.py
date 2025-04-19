from import_lib import *


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
