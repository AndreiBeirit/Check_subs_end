import paramiko
import emoji
import mysql.connector
from datetime import datetime
import os
import requests
from db_creds import db_host, db_port, db_user, db_password, db_name, ssh_ip, ssh_port, ssh_username, ssh_password

# Настройки бд
mysql_config = {
    'host': db_host,
    'port': db_port,
    'user': db_user,
    'password': db_password,
    'database': db_name
}

# Настройки SSH-сервера
ssh_config = {
    'hostname': ssh_ip,
    'port': ssh_port,
    'username': ssh_username,
    'password': ssh_password
}

# параметры Telegram бота
telegram_config = {
    'bot_token': '6203912655:AAEgBi',
    'chat_id': '9'
}

# пишем SQL-запрос
sql = "SELECT Email, CreateDate FROM Accounts WHERE DATE(CreateDate) = DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND `Status` IN (1,2,5,9,15,20,21)"

# подключаемся к серверу по SSH
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(**ssh_config)

# выполняем запрос
mysql_connection = mysql.connector.connect(**mysql_config)
cursor = mysql_connection.cursor()
cursor.execute(sql)
result = cursor.fetchall()

# сохраняем результат в файл
filename = 'sub_end.txt'
now = datetime.now()
file_path = f'D:\\{filename}'
with open(file_path, 'w') as f:
    for row in result:
        f.write(f'{row[0]}\n{row[1]}\n')

# отправляем сообщение в Telegram
if os.path.getsize(file_path) > 0:
    with open(file_path, 'r') as f:
        text = f.read()
    message = (emoji.emojize(f':skull::skull::skull:Есть аккаунты с завершающейся подпиской!:skull::skull::skull:\n{text}'))
    url = f'https://api.telegram.org/bot{telegram_config["bot_token"]}/sendMessage'
    payload = {'chat_id': telegram_config['chat_id'], 'text': message}
    requests.post(url, data=payload)
else:
    message = (emoji.emojize(f':sparkle::sparkle::sparkle:Сегодня подписки актуальны.:sparkle::sparkle::sparkle:'))
    url = f'https://api.telegram.org/bot{telegram_config["bot_token"]}/sendMessage'
    payload = {'chat_id': telegram_config['chat_id'], 'text': message}
    requests.post(url, data=payload)
