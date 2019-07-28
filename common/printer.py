



def bold_text(text):
	return '\033[1m' + text + '\033[0m'

def bold_print(text, end=None):
	if(end == None):
		print(bold_text(text))
	else:
		print(bold_text(text), end=end)
	