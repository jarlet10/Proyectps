import sys
import requests

token = '1862504006:AAEr91Gc0keP4lJkNE59qwK3wAMXrz1CLqU'
chat_id = '678557081'


def mandar_mensaje_bot(mensaje, token=token, chat_id=chat_id):
    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + mensaje
    response = requests.get(send_text)

def mandar_mensaje_bot_post(mensaje, token=token, chat_id=chat_id):
    datos = {'chat_id': chat_id, 'text': mensaje}
    url = 'https://api.telegram.org/bot'+ token +'/sendMessage'
    response = requests.post(url = url, data = datos)

if __name__ == '__main__':
    mensaje = sys.argv[1]
    mandar_mensaje_bot_post(mensaje)