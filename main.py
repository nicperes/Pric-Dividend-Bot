#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import json
import urllib
from urllib.request import urlopen
import requests
import certifi
import telebot
from datetime import datetime
import re

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
/consultar nome da crypto USD (ethusd) \n
/div para consultar os dividendos""")

@bot.message_handler(commands=['consultar'])
def consultar(message):
    ticker = message.text.replace("/consultar ", "")
    resultado = valor_acao(message, ticker)
    bot.send_message(message.chat.id, resultado)

@bot.message_handler(commands=['div'])
def consultar(message):
    ticker = message.text.replace("/div ", "")
    resultado = valor_dividendos(message, ticker)
    bot.send_message(message.chat.id, resultado)


@bot.message_handler(commands=['alertar_porcentagem'])
def inserir_monitoracao(message):
    alerta = message.text.replace("/alertar ", "")
    array = alerta.split(" ")

    if len(array) == 3:
        ticker = array[0]
        operador = array[1]
        porcentagem = array[2]

def valor_acao(message, ticker):
    url = ("https://financialmodelingprep.com/api/v3/quote/"+ticker.upper()+"?apikey=f879a413f4827a4931d073de76847af9")
    response = requests.get(url)
    data = response.json()
    try:
        symbol = data[0]['symbol']
        name = data[0]['name']
        price = data[0]['price']
        price = str(price)
        percentage = float("{:.2f}".format(data[0]['changesPercentage']))
        percentage = str(percentage)
        texto = "Sigla: "+symbol+"\n"+"Ação: "+name+"\n"+"Preço: "+price+"\n"+"Variação até o momento: "+percentage+"%"
        return texto
    except IndexError:
        return "Ativo digitado incorretamente"+"\n"+"Para ativos do brasil coloque '.SA' (azul4.sa)"+"\n"+"Para criptomoedas coloque 'USD' (ethusd)"

def valor_dividendos(message, ticker):
    url = ("https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/" + ticker.upper() + "?apikey=f879a413f4827a4931d073de76847af9")
    response = requests.get(url)
    data = response.json()
    try:
        ultimaData = str(data['historical'][0]['date'])
        penultimaData = str(data['historical'][1]['date'])
        d1 = datetime.strptime(ultimaData, '%Y-%m-%d')
        d2 = datetime.strptime(penultimaData, '%Y-%m-%d')
        tempoPagamento = abs((d2-d1))
        tempoDias = str(tempoPagamento).replace(" days, 0:00:00", "")
        valorUltimo = str(data['historical'][0]['dividend'])
        valorPenultimo = str(data['historical'][1]['dividend'])
        strDataPagamento = data['historical'][0]['paymentDate']
        strDataDeclaracao = data['historical'][0]['declarationDate']
        dataPagamento = converter_data(strDataPagamento)
        dataDeclaracao = converter_data(strDataDeclaracao)

        texto = "Sigla: "+ticker.upper()+"\n"+"Tempo de pagamento: "+tempoDias+" dias"+"\n"+"Valor ultimo pagamento: " \
                 ""+valorUltimo+"\n"+"Valor penultimo pagamento: "+valorPenultimo+"\n"+"Data do ultimo pagamento: "+dataPagamento+"\n" \
                 ""+"Data da ultima declaração: "+dataDeclaracao


        return texto
    except KeyError:
        return "Ativo digitado incorretamente ou não existe dividendos para esta ação"

def converter_data(date):
    return re.sub(r'(\d{4})-(\d{1,2})-(\d{1,2})', '\\3-\\2-\\1', date)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()