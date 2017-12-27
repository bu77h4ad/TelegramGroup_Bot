# -*- coding: utf-8 -*-
import re
import json
import time
import pprint
import requests
import APItelegram
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('TelegramGroup_Bot.ini')

uset_exception = cfg.get('Telegram', 'User_exception')
token = cfg.get('Telegram', 'Token_bot')

bot = APItelegram.telegram(token)

def message(update):
	###Запрет ССЫЛОК
	#Проверка на исключения пользователя	
	#replay_user =0
	#user = 0 
	#with open('TelegramGroup_Bot.log', 'a', encoding='utf8') as outfile:
	#	json.dump(update, outfile, sort_keys = True, indent = 4 ,ensure_ascii=False)
	
	if 'text' in update :
		text = re.findall (r'(?:https?:\/\/)?(?:[\w\.]+)\.(?:[a-z]{2,6}\.?)(?:\/[\w\.]*)*\/?', update['text'].lower() )	
	else:
		text = []
	
	if 'caption' in update : 
		caption =  re.findall(r'(?:https?:\/\/)?(?:[\w\.]+)\.(?:[a-z]{2,6}\.?)(?:\/[\w\.]*)*\/?', update['caption'].lower() )	
	else:
		caption = []

	#pprint.pprint (update)	
	#print ("SSILKI ", text, caption)
	#print()	
	
	
	if 'username' in update['from'] :
		user = uset_exception.lower().find(update['from']['username'].lower()) 
		# Если пользователь отправивший сообщение в исключениях то пропускает
		if user != -1  : return 
	
	# Если ссылок в сообщении не найдено то пропускает
	if len(text) + len(caption) == 0 : return
	
	# Если есть реплей в сообщении
	if 'reply_to_message' in update :		
		if 'username' in update['reply_to_message']['from'] : 
			replay_user = uset_exception.lower().find(update['reply_to_message']['from']['username'].lower())	
			# Если реплеят сообщения, юзера из исключений то пропускает 
			if replay_user != -1 : return
	
	print ("[ЗАБЛОКИРОВАНО] ->", update['from']['first_name'], text , caption )
	bot.deletemessage(update['chat']['id'], update['message_id'])
	bot.sendMessage(update['chat']['id'], update['from']['first_name'] + ", размещение ссылок в данном чате запрещено!" )

def channel_post(update):	
	pass

pprint.pprint (bot.getMe())	
print ('\n', "TelegramGroup_Bot Запущен ... ")

update_id = 0
bot.delUpdates()

while True :
	
	try:		
		update = bot.getUpdates(update_id + 1)['result']
	except:
		print ('update_id', update_id)
		pprint.pprint (update)
		continue

	for x in range(0,len(update)):
		#if 'channel_post' in update[x] : channel_post(update[x]['channel_post']) ; update_id = update[x]['update_id']	
		if 'message' in update[x] : message(update[x]['message']) ; update_id = update[x]['update_id']
	



