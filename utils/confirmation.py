def confirmation_prompt(text:str):
    answer = input(text + '[y/n]')
    if answer.lower() in ['y, yes']:
        return True
    elif answer.lower() in ['n', 'no']:
        return False
    else:
        return None