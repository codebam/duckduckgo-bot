#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic inline bot example. Applies different text transformations.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from uuid import uuid4

from telegram import InlineQueryResultArticle, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import logging
from urllib.parse import quote_plus
import configparser
from os import environ
import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='''Hello, I am an Inline bot, \
please use me by mentioning my username in a chat along with your query''')


def shorten_url(long_url):
    response = requests.post('https://ptpb.pw/u', data={'c': long_url})
    url = response.headers.get('Location')
    return url


def convert_to_url(query):
    # feel free to fork and change the base url
    base = "https://duckduckgo.com/?q="
    end = quote_plus(query)
    url = base + end
    return url


def inlinequery(bot, update):
    query = update.inline_query.query
    results = list()

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title='DuckDuckGo: ' + query,
                                            thumb_url='https://duckduckgo.com/assets/icons/meta/DDG-iOS-icon_60x60.png',
                                            url=convert_to_url(query),
                                            input_message_content=InputTextMessageContent(convert_to_url(query))))

    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title='Shortened: ' + query,
                                            thumb_url='https://avatars1.githubusercontent.com/u/12021773?v=3&s=200',
                                            url=shorten_url(convert_to_url(query)),
                                            input_message_content=InputTextMessageContent(shorten_url(convert_to_url(query)))))

    bot.answerInlineQuery(update.inline_query.id, results=results)


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def change_token():
    config = []
    config['config'] = {'token': input('API Key: ')}
    if input('Save? [Y/n]') not in ['n', 'N']:
        with open('config.mine.ini', 'w') as configfile:
            config.write(configfile)
        print('API Key Saved to config.mine.ini')
    return config['config']['token']


def main():
    try:
        token_ = environ['TELEGRAM_API_KEY']
        # tries to read the api key inside an environment var if it exists
    except KeyError:
        config = configparser.ConfigParser()
        config.read('config.mine.ini')
        try:
            token_ = config['config']['token']
        except KeyError:
            config.read('config.ini')
            try:
                token_ = config['config']['token']
            except:
                pass
            # if there's a keyerror the file probably doesn't exist
            # we fall back to config.ini (the template file)

    if token_ in ['','enter your token here']:
        token_ = change_token()
        # if both token files are empty we prompt the user to enter
        # their api key and optionally save it

    # Create the Updater and pass it your bot's token.
    updater = Updater(token_)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
