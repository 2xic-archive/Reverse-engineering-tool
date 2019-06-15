
def should_continue(message):
	response = input(message + "\n")
	if(response.lower() == "y" or len(response) == 0):
		return True
	elif(response.lower() == "n"):
		return False
	else:
		return should_continue("reply with Y/n")
