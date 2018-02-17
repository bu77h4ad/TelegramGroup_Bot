import requests
import pprint
import json
import sys

class telegram():
	"""
	Class for API Telegram
	"""
	def __init__(self, token):
		self.token = token
		self.url = 'https://api.telegram.org/bot' + self.token + '/'
	
	def getMe(self):
		try: 
			return requests.post(self.url + 'getMe').json()
		except:
			print ("Error: ", sys.exc_info()[1])
			return False 		

	def getUpdates(self, offset = 0):  	
		params = { 'offset': offset }
		try:
			return  requests.post (self.url  + 'getUpdates', params  ).json()
		except:
		 	print ("Error: ", sys.exc_info()[1])
		 	return False
		 

	def delUpdates(self):
		"""
		Удаляет все обновления на сервере
		"""
		update = telegram.getUpdates(self)
		if update == False or len(update['result']) == 0: return True
		update_id = update['result'][-1]['update_id']
		telegram.getUpdates(self, offset = update_id + 1)
		return  True

	def getMessage(self,offset = 0):
		"""
		Возвращает 1ое ПМ найденное сообщение в хронологическом порядке, все другие записи стирает до 1ого сообщения
		"""
		# получаем список обновлений
		telegram_update = telegram.getUpdates(self, offset)

		if telegram_update == False : return False
		telegram_update = telegram_update['result'] 
		# проходимся по всему списку в хронологическом порядке, пока не найдем певое сообщение
		for x in range(0,len(telegram_update)):
						
			if 'message' in telegram_update[x] and 'text' in  telegram_update[x]['message']	:
				telegram.getUpdates(self, offset = int(telegram_update[0]['update_id']) + 1 + x )
				return telegram_update[x]['message']
		#Если сообщения не найдены, но возможно в апдейте что то хранится, то удаляем
		else: 
			if len(telegram_update) == 0: return False
			telegram.getUpdates(self, offset = int(telegram_update[0]['update_id']) + 1 + x )
		# Если записей нет
		return False		
	
	def sendMessage(self, chat_id, text = 'Привет'):
		"""
		Отправляет сообщение
		"""
		params = {'chat_id': chat_id, 'text': text}
		method = 'sendMessage'
		try:
			return requests.post(self.url + method, params).json()
		except:
			print ("Error: ", sys.exc_info()[1])
			return False 

	def deletemessage(self, chat_id, message_id):
		"""
		Удаляет сообщения
		"""
		params = {'chat_id': chat_id, 'message_id': message_id}
		method = 'deletemessage'
		return requests.post(self.url + method, params)

	def kickChatMember(self, chat_id, user_id):
		"""
		Разбанить юзера
		"""
		params = {'chat_id': chat_id, 'user_id': user_id}
		method = 'kickChatMember'
		return requests.post(self.url + method, params)

	def unbanChatMember(self, chat_id, user_id):
		"""
		Разбанить юзера
		"""
		params = {'chat_id': chat_id, 'user_id': user_id}
		method = 'unbanChatMember'
		return requests.post(self.url + method, params)
	

	def getChannelPost(self):
		pass
		
#for x in range(0,0):
#	print ("telo")
#else:
#	print ("else")