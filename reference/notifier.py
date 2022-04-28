import requests


def telegram_notify(message):
    token, chatid = '5365356437:AAHxBDj7J4TjjK2Z4fQJyHPkRc8KME-5hrA', '-742341519'
    txtmsg = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatid + '&parse_mode=Markdown&text=' + message
    requests.get(txtmsg)
    print(f"NotifierBot delivered the following message: {message}")
    