error_messages = list[str]

def error(msg:str):
    error_messages.append(msg)

def error_clear():
    error_messages.clear()

def errors()->list[str]:
    return error_messages