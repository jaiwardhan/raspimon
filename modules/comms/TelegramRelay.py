"""
jaiwardhan/Raspimon

@author: Jaiwardhan Swarnakar, 2021
Copyright 2021-present
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import telegram
import os

class PiMonBot:
	"""Uses Telegram bot service recognized by the BOT TOKEN 
	to post alerts to a channel identified by the CHANNEL ID.
	
	To crete and obtain your BOT TOKEN, contact BotFather at
	https://web.telegram.org/#/im?p=@BotFather

	To obtain your channel id, simply create a channel and add
	the bot. Open your channel in Telegram web and follow these
	instructions: https://gist.github.com/mraaroncruz/e76d19f7d61d59419002db54030ebe35

	Expose your bot credentials via environment variables PI_BOT_TOKEN
	and PI_CHANNEL_ID
	"""
	
	bot = None
	BOT_TOKEN=os.getenv('PI_BOT_TOKEN')
	CHANNEL_ID=os.getenv('PI_CHANNEL_ID')

	@staticmethod
	def init(reinit=False):
		"""Initialize the telegram bot with credentials. Once
		created it can only be overridden with a True reinit

		Args:
			reinit (bool, optional): Set to True to force reinitialize
			the bot instance. Defaults to False.
		"""
		if not reinit and PiMonBot.bot is not None:
			return
		PiMonBot.bot = telegram.Bot(token=PiMonBot.BOT_TOKEN)

	@staticmethod
	def send(msg=''):
		"""Send a message string to a channel using HTML parse mode

		Args:
			msg (str, optional): The message to post in plain text or
			supported HTML format. Defaults to ''.
		"""
		if msg is None or len(str(msg)) == 0:
			return
		msg = str(msg)
		if PiMonBot.bot is None:
			PiMonBot.init()
		PiMonBot.bot.sendMessage(parse_mode='html', chat_id=PiMonBot.CHANNEL_ID, text=msg)
