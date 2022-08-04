#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import json
import urllib
from urllib.request import urlopen
import requests
import certifi
import telebot

API_TOKEN = '5458735640:AAE86OI_nKO3rgIjHXliFd4KBYcBFUrZXAQ'

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
Bem vindo ao Price/Dividend Bot \n
Comandos: \n
/consultar nome do ativo nos EUA (tsla) \n
/consultar nome do ativo brasilerio .SA (azul4.sa) \n
/consultar nome da crypto USD (ethusd)""")

@bot.message_handler(commands=['consultar'])
def consultar(message):
    ticker = message.text.replace("/consultar ", "")
    resultado = valor_acao(message, ticker)
    bot.send_message(message.chat.id, resultado)

def valor_acao(message, ticker):
    url = ("https://financialmodelingprep.com/api/v3/quote/"+ticker.upper()+"?apikey=f879a413f4827a4931d073de76847af9")
    response = requests.get(url)
    data = response.json()
    symbol = data[0]['symbol']
    name = data[0]['name']
    price = data[0]['price']
    price = str(price)
    percentage = float("{:.2f}".format(data[0]['changesPercentage']))
    percentage = str(percentage)
    texto = "Sigla: "+symbol+"\n"+"Ação: "+name+"\n"+"Preço: "+price+"\n"+"Variação até o momento: "+percentage+"%"
    return texto


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()