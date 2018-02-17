# -*- coding: utf-8 -*-
import re
import json
import time
import pprint
import requests
import APItelegram
from configparser import ConfigParser

idban =0 # кого банить
countban = 0 # сколько сообщений получил юсер на бан

cfg = ConfigParser()
cfg.read('TelegramGroup_Bot.ini')

uset_exception = cfg.get('Telegram', 'User_exception')
token = cfg.get('Telegram', 'Token_bot')

bot = APItelegram.telegram(token)
regul = '(?:https?:\/\/)?(?:[\w\.]+)\.(?:[a-z]{2,6}\.?)(?:\/[\w\.]*)*\/?'

def message(update):
	###Запрет ССЫЛОК
	#Проверка на исключения пользователя	
	#replay_user =0
	#user = 0 
	
	# Вести логи
	pprint.pprint (update)	
	#with open('TelegramGroup_Bot.log', 'a', encoding='utf8') as outfile:
	#	json.dump(update, outfile, sort_keys = True, indent = 4 ,ensure_ascii=False)
	#return
	# ПРОВЕРКА НА ТЕКСТ ИЗ ЧЕРНОГО СПИСКА
	# БАН
	global idban, countban
	if 'text' in update :
		if update['text'].lower() == '/ban':
			if 'username' in update['from'] :
				user = uset_exception.lower().find(update['from']['username'].lower()) 
				# Если пользователь отправивший сообщение в исключениях то выполняем
				if user != -1  : 
					if 'reply_to_message' in update :
						#print ('Zabanit', update['reply_to_message']['from']['id'])
						if idban == update['reply_to_message']['from']['id']:
							countban = countban +1
							#print ('countban',countban)
						else:
							countban=0
							idban = update['reply_to_message']['from']['id']
					if countban >= 0:
						
						result = json.loads (bot.kickChatMember(update['chat']['id'], idban).text)
						print ('Посылаю команду на бан - >', result  )
						if 'result' in result :
							if result['result'] == True: 
								bot.sendMessage(update['chat']['id'], update['reply_to_message']['from']['first_name'] + ' забанен')
						countban = 0


	# ПОИСК ССЫЛОК
	if 'text' in update :
		text = re.findall (regul, update['text'].lower() )	
	else:
		text = []
	
	if 'caption' in update : 
		caption =  re.findall(regul, update['caption'].lower() )	
	else:
		caption = []

	if 'entities' in update:
		entities = str(update['entities']).lower()
		entities_mention = 	entities.find('mention') # проверка на @ссылки в группы например
		entities = re.findall(regul, entities )		
	else:
		entities = []
		entities_mention = -1

	if 'from' in update:
		from_ = str(update['from']).lower()
		from_ =  re.findall(regul, from_ )
	else:
		from_ = []

	
	#print ("SSILKI ", text, caption)
	#print()	
	
	
	if 'username' in update['from'] :
		user = uset_exception.lower().find(update['from']['username'].lower()) 
		# Если пользователь отправивший сообщение в исключениях то пропускает
		if user != -1  : return 
	
	# Если ссылок в сообщении не найдено то пропускает
	if len(text) + len(caption) + len(entities) + len(from_) == 0 and  entities_mention == -1 : return
	
	# Если есть реплей в сообщении
	if 'reply_to_message' in update :		
		if 'username' in update['reply_to_message']['from'] : 
			replay_user = uset_exception.lower().find(update['reply_to_message']['from']['username'].lower())	
			# Если реплеят сообщения, юзера из исключений то пропускает 
			if replay_user != -1 : return
	
	if  len(re.findall(regul, update['from']['first_name'] )) == 0: 
		name = update['from']['first_name'] 
	else: 
		name = 'Ссылочник'
	print ("[ЗАБЛОКИРОВАНО] ->", update['from']['first_name'], text , caption )
	bot.deletemessage(update['chat']['id'], update['message_id'])
	#bot.sendMessage(update['chat']['id'], name + ", размещение ссылок в данном чате запрещено!" )

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
	#	print ('update_id', update_id)
	#	pprint.pprint (update)
		continue

	for x in range(0,len(update)):
		#if 'channel_post' in update[x] : channel_post(update[x]['channel_post']) ; update_id = update[x]['update_id']	
		if 'message' in update[x] : message(update[x]['message']) ; update_id = update[x]['update_id']
	



