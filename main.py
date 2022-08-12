#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import json
import urllib
from urllib.request import urlopen
import requests
import certifi
import dbConfig
import telebot
from datetime import datetime
import re
import numpy as np
import array as arr

#Token do Telegram
API_TOKEN = '5458735640:AAE86OI_nKO3rgIjHXliFd4KBYcBFUrZXAQ'

bot = telebot.TeleBot(API_TOKEN)

#database = (r"./monitoramento.db")


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
Bem vindo ao Price/Dividend Bot \n
Comandos: \n
/consultar nome do ativo nos EUA (tsla) \n
/consultar nome do ativo brasilerio .SA (azul4.sa) \n
/consultar nome da crypto USD (ethusd) \n
/div para consultar os dividendos \n
/alertar para criar alerta de alteração de preço dos ativos \n
/alertas para exibir seus alertas ativos \n
/alerta_excluir para excluir o alerta que preferir """)

#'/consultar'
@bot.message_handler(commands=['consultar'])
def consultar(message):
    ticker = message.text.replace("/consultar ", "")
    resultado = valor_acao(message, ticker)
    bot.send_message(message.chat.id, resultado)

#'/div'
@bot.message_handler(commands=['div'])
def dividendos(message):
    ticker = message.text.replace("/div ", "")
    resultado = valor_dividendos(message, ticker)
    bot.send_message(message.chat.id, resultado)

#'/alertar'
@bot.message_handler(commands=['alertar'])
def inserir_monitoracao(message):
    alerta = message.text.replace("/alertar ", "")
    array = alerta.split(" ")

    if len(array) == 3:
        ticker = array[0]
        operador = array[1]
        porcentagem = array[2]
    else:
        texto = ("Favor preencher corretamente (/alertar ativo > 5)")
        bot.send_message(message.chat.id, texto)

    if registrar_monitoracao(message.chat.id, ticker, operador, porcentagem):
        if operador == ">":
            operador = "maior"
        else:
            operador = "menor"
        texto = ("Monitoração incluída com sucesso: "+"\n"+"Ativo: "+ticker+"\n"+"Operador: "+operador+"\n"+"Porcentagem: "+porcentagem+"%")
        bot.send_message(message.chat.id, texto)
    else:
        texto = ("Erro ao incluir a monitoração")
        bot.send_message(message.chat.id, texto)

@bot.message_handler(commands=['alertas'])
def alertas (message):

    id, data_loads, text = consultar_monitoracao(message.chat.id)

    if len(data_loads) == 0:
        bot.send_message(message.chat.id, "Não existem alertas configurados")
    else:
        for i in range(len(data_loads)):
            bot.send_message(str(id), text[i])

@bot.message_handler(commands=['alerta_excluir'])
def alerta_excluir(message):
    alerta = message.text.replace("/alerta_excluir ", "")
    array = alerta.split(" ")

    if len(array) == 1:
        id = array[0]
    else:
        texto = ("Favor preencher corretamente (/alerta_excluir id do alerta)")
        bot.send_message(message.chat.id, texto)

    conn = dbConfig.create_connection()
    dbConfig.create_table_monitoracao(conn)
    with conn:
        excluirAlerta = dbConfig.excluir_monitoracao(conn, id)
        if excluirAlerta:
            texto = ("Alerta excluido com sucesso")
            bot.send_message(message.chat.id, texto)
        else:
            texto = ("Favor validar se o ID está correto (/alerta_excluir id do alerta)")
            bot.send_message(message.chat.id, texto)


def enviarMensagem(id, texto):
    bot.send_message(id, texto)
    return true

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

def registrar_monitoracao(message, ticker, operador, porcentagem):
    conn = dbConfig.create_connection()
    dbConfig.create_table_monitoracao(conn)
    with conn:
        monitoracao = (message, ticker, operador, porcentagem)
        monitoracaoid = dbConfig.insert_monitoracao(conn, monitoracao)
        if monitoracaoid:
            return True
        else:
            return False

class Monitoracao(object):
    def __init__(self, id, name, operator, variation):
        self.id = id
        self.name = name
        self.operator = operator
        self.variation = variation



def consultar_monitoracao(message):
    conn = dbConfig.create_connection()
    dbConfig.create_table_monitoracao(conn)

    id = []
    text = []

    with conn:
        id, consultar = dbConfig.consult_table_monitor(conn, message)

    data_loads = json.loads(consultar)

    print(data_loads)

    for i in range(len(data_loads)):
        ids = data_loads[i]['ID']
        name = data_loads[i]['Name']
        operator = data_loads[i]['Operator']
        variation = data_loads[i]['Variation_number']
        texto = "Id: " + str(ids) +"\n"+"Ativo: " + name.upper() +"\n"+"Operador: "+operator+"\n"+"Variação: "+str(variation)
        print(id)
        #id += [i.id]
        text += [texto]


    return id, data_loads, text


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.send_message(message.chat.id, """\
        Bem vindo ao Price/Dividend Bot \n
        Comandos: \n
        /consultar nome do ativo nos EUA (tsla) \n
        /consultar nome do ativo brasilerio .SA (azul4.sa) \n
        /consultar nome da crypto USD (ethusd) \n
        /div para consultar os dividendos \n
        /alertar para criar alerta de alteração de preço dos ativos \n
        /alertas para exibir seus alertas ativos \n
        /alerta_excluir para excluir o alerta que preferir """)


bot.infinity_polling()