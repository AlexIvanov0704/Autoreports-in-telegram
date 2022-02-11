import telegram
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os
import pandas as pd
from read_db.CH import Getch
from telegram import InputMediaPhoto as imp

def FeedSending():    
    bot = telegram.Bot(token=os.environ.get("ivanov_kc_bot_token"))
    chat_id = -674009613
    data = Getch("""SELECT toDate(time) AS "Дата",
                 count(DISTINCT user_id) AS "DAU",
                 countIf(user_id, action = 'view') AS "Просмотры",
                 countIf(user_id, action = 'like') AS "Лайки"
             FROM simulator_20211220.feed_actions
             WHERE toDate(time) between (today() - 7) and (today() - 1)
             GROUP BY toDate(time)
             ORDER BY toDate(time)""").df
    data["CTR"]=np.where(data["Просмотры"]==0,0,data["Лайки"]/data["Просмотры"])
    
    Msg_DailyReport_feed = ("Ежедневный отчет по ленте новостей\nОсновные метрики за {input[0]:%d.%m.%Y}:"
                            "\n - DAU: {input[1]:,}\n - Просмотры: {input[2]:,}"
                            "\n - Лайки: {input[3]:,}"
                            "\n - CTR: {input[4]:.2%}").format(input=data.loc[6])
    bot.send_message(chat_id=chat_id, text=Msg_DailyReport_feed)
    
    period = "c {input[0]:%d.%m.%Y} по {input[6]:%d.%m.%Y}".format(input=data["Дата"])
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('Количество пользователей',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(x = "Дата", y = "DAU", data = data)
    plt.suptitle("DAU {}".format(period), fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=10)
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.name = 'DAU_plot.png'
    plot_object.seek(0)
    plt.close()
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('CTR',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(x = "Дата", y = "CTR", data = data)
    plt.suptitle("CTR {}".format(period), fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=10)
    plot_object2 = io.BytesIO()
    plt.savefig(plot_object2)
    plot_object2.name = 'CTR_plot.png'
    plot_object2.seek(0)
    plt.close()
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('Количество событий',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(x = "Дата", y = "Лайки", data = data)
    sns.lineplot(x = "Дата", y = "Просмотры", data = data)
    plt.legend(labels=["лайки","просмотры"])
    plt.suptitle("Просмотры и лайки {}".format(period), fontsize=20)
    plt.tick_params(axis='both', which='major', labelsize=10)
    plot_object3 = io.BytesIO()
    plt.savefig(plot_object3)
    plot_object3.name = 'View_like_plot.png'
    plot_object3.seek(0)
    plt.close()
    
    bot.send_media_group(chat_id=chat_id, media = [imp(plot_object),imp(plot_object3), imp(plot_object2)])

try:
    FeedSending()
except Exception as er:
    print(er)
