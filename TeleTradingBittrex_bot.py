from bittrex import Bittrex, API_V2_0, API_V1_1, BUY_ORDERBOOK, TICKINTERVAL_ONEMIN
from configparser import ConfigParser
import time
import requests
import pprint
from APItelegram import telegram

def setSell(last_message ):
	# ставит лимитный ордер на прожажу заданной монеты	
	last_balance = my_bittrex.get_balance(last_message['text'])['result']
	xCoin = last_balance['Available'] # доступный для торговли баланс	
	bid = last_tiker = my_bittrex.get_ticker('BTC-'+ last_message['text'])['result']['Bid']			
	bid = bid / 100 * (100 + cfg.getfloat('Data', 'sellpercent'))
	text = str(my_bittrex.sell_limit('BTC-'+ last_message['text'], xCoin , bid ) )
	bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Ответ bittrex на продажу: \n\n" + text ) 
	bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Операция выполнена" ) 

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

# Читаем настройки из файла
cfg = ConfigParser()
cfg.read('TeleTradingBittrex_bot.ini')
#print(cfg.get('Data', 'telegram_token'))
#print(cfg.get('Data', 'api_key'))
#print(cfg.get('Data', 'api_secret'))
#print(cfg.getfloat('Data', 'deposit'))  # get "float" object
#print(cfg.get('Data', 'owner'))
update_id = 0

my_bittrex = Bittrex(cfg.get('Data', 'api_key'), cfg.get('Data', 'api_secret'), api_version=API_V1_1)
#url = "https://api.telegram.org/bot%(token)s/" %{"token" : cfg.get('Data', 'telegram_token')}

bot = telegram(cfg.get('Data', 'telegram_token'))
bot.delUpdates()

# Функция для Телеграм бота
#def bot(command = False, offset = '', chat_id = '', text = ''):  
#	if command == False : command = 'getUpdates?offset=' + offset
#	if chat_id != False : chat_id = '?chat_id=' + chat_id
#	if text    != False : text    = '&text='+ text
#	response = requests.get(url + command + chat_id + text)
#	return response.json()

print ("Set sell percent ->\t\t", cfg.getfloat('Data', 'sellPercent'),"%")
print ("Set commission ->\t\t", cfg.getfloat('Data', 'commission'),"%")
print ("Set bot owner ->\t\t", cfg.get('Data', 'owner'))

getMe = bot.getMe()
if getMe != True: 
	getMeStatus = 'OK!'
	userName = getMe['result']['username']
else:
	getMeStatus = 'FAIL!'
	userName = getMe
	time.sleep(30)
	quit()
print ("Init bot status ->\t\t", getMeStatus, '->\t' , userName )

balance = my_bittrex.get_balance('BTC')
balanceStatus = balance['success'] 
if balanceStatus == True:
	balanceStatus = 'OK!'
else:
	balanceStatus = 'FAIL!'
print ("Init bittrex status ->\t", balanceStatus, '->\t', "Available BTC for trading -> %(sum).8f" % {'sum' : balance['result']['Available']})

print ("TeleTradingBittrex_bot started\t OK!")
print()

# Цикл для проверки новых сообщений
while True:
	time.sleep(0.5)

	# проверка на новые сообщения
	last_message = bot.getMessage()

	if  last_message == False : continue	
	# Обнаружено новое сообщение, то ......
	
	# Является ли отправитель владельцем бота ?
	if cfg.get('Data', 'owner').lower() != last_message['from']['username'].lower(): 
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Ты не мой хозяин" )
		continue
	print ("Message from owner ->", last_message['text'])

	# Ответ на команду /stop
	if last_message['text'] == '/stop':
		bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "Бот отключен")
		quit()

	# Ответ на команду /start
	if last_message['text'] == '/start':
		bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "Приветсвую тебя хозян!\nЯ твой маленький, торговый бот помошник :)")
		bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "Можешь мне писать название монеты, а я её буду покупать за BTC. И оставлю ордер, на продажу этой же монеты, на " +str (cfg.getfloat('Data', 'sellPercent'))+ " % дороже.")
		continue
	# Ответ на команду ДЕПОЗИТ
	if last_message['text'].split(' ')[0] == "Депозит" and len (last_message['text'].split(' ')) == 2 : 
		if isfloat( last_message['text'].split(' ')[1]) \
		and float(last_message['text'].split(' ')[1]) <= 100 \
		and float(last_message['text'].split(' ')[1]) > 0 : 
			cfg['Data']['deposit'] = last_message['text'].split(' ')[1]
			bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "\u2757\ufe0f Депозит установлен на : " + last_message['text'].split(' ')[1] + "%")
			# сохраняем настройки в файл
			with open('TeleTradingBittrex_bot.ini', 'w') as configfile:
				cfg.write(configfile)
			continue	
		else:
			bot.sendMessage(chat_id =  str(last_message['from']['id']), text = "\u274c Депозит не установлен")
			continue

	# ответ бота на команду о покупке	
	# Существует ли такая монета ?	
	if my_bittrex.get_ticker('BTC-'+ last_message['text'])['success'] == False :
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u274c Mонета '" +last_message['text'] +"' не найдена ")
		continue
	
	# Подтверждение операции
	bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u2757\ufe0f 1. Купить '{0}' по текущей цене.\n\n\u2757\ufe0f 2. Поставить лимитный ордер на продажу '{0}' на {1}%  выше текуще стоимости. \n\nПодтверждаете ('Да'/'Нет') \u2753".format( last_message['text'], cfg.getfloat('Data', 'sellPercent') ) )
	print ("Waiting for confim (30 sek) ...")
	y=0
	while y in range(0,60) :		
		time.sleep(0.5)
		y = y + 1 		
		wait_message = bot.getMessage()
		if wait_message == False : continue
		if cfg.get('Data', 'owner').lower() == wait_message['from']['username'].lower(): 
			if wait_message['text'] in ['Да','да','ДА'] :
	 			bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u2b55\ufe0f Операция подтверждена ")
	 			print ("Сonfirmed")
	 			break
			else:
	 			#bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u274c Операция отменена ")
	 			y=-1
	else:
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u274c Операция отменена")
		print ("Cansel")
		continue
			
	# Выполняет операции на бирже
	bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "\u2757\ufe0f Закупаю... ")
	while True :		
		
		last_balance = my_bittrex.get_balance('BTC')['result']
		BTC = last_balance['Available'] # доступный для торговли баланс

		if BTC <= 0.00050000 : 
			bot.sendMessage(chat_id = str(last_message['from']['id']), text =  'Слишком маленький баланс: \nBTC : {:.8f} '.format(BTC) ) 
			break

		# покупает заданную монету
		while True:
			sellOrderBook = sorted ( my_bittrex.get_orderbook ("BTC-" + last_message['text'])['result']['sell'][0:10], key=lambda k: k['Quantity'], reverse=True )
			
			for x in range(0,10):			
				# баланс БТС выраженный в xCoin  <  количество монет из книги ордеров
				if BTC / sellOrderBook[x]['Rate'] < sellOrderBook[x]['Quantity']  : 
					text = my_bittrex.buy_limit('BTC-' + last_message['text'], BTC / sellOrderBook[x]['Rate'] * float(1 - cfg.getfloat('Data', 'commission') / 100), sellOrderBook[x]['Rate'] )
					print (text,BTC / sellOrderBook[x]['Rate'] * float(1 - cfg.getfloat('Data', 'commission') / 100), sellOrderBook[x]['Rate'])		
				else: 
					text = my_bittrex.buy_limit('BTC-' + last_message['text'], sellOrderBook[x]['Quantity'] * float(1 - cfg.getfloat('Data', 'commission') / 100), sellOrderBook[x]['Rate'] ) 						
					
				BTC = BTC - BTC / sellOrderBook[x]['Rate'] * float(1 - cfg.getfloat('Data', 'commission')/ 100)
				if BTC <= 0.00050000 : break			
			if BTC <= 0.00050000 : break		

		# проверяет исполнился ли ордер
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Проверяю покупку (2 сек)...") 
		time.sleep(1)
		get_open_orders = my_bittrex.get_open_orders('BTC-' + last_message['text'])			
		if len(get_open_orders['result']) == 0: 
			setSell(last_message)
			break

		# Если ордер на покупку не исполнился , то отменяет все открытые новые ордера
		bot.sendMessage(chat_id = str(last_message['from']['id']), text =  "Не удалось выкупить весь объем.\nПовторяю...") 
		for y in range(0,len(get_open_orders['result'])):						
			my_bittrex.cancel(get_open_orders['result'][y]['OrderUuid'])
			time.sleep(0.1)									
			
