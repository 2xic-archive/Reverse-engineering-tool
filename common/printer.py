



def bold_text(text):
	return '\033[1m' + text + '\033[0m'

def bold_print(text):
	print(bold_text(text))

