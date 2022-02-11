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
    data = Getch("""With 
                us_list as (
                    (SELECT DISTINCT user_id, age, city, country, gender, os, source, exp_group FROM simulator_20211220.feed_actions)
                    union distinct 
                    (SELECT DISTINCT user_id, age, city, country, gender, os, source,  exp_group FROM simulator_20211220.message_actions)), \
                src as (
                    (SELECT DISTINCT toDate(time) as day, user_id as user
                        , 1 as feed, 0 as sent, 0 as recieved
                    FROM simulator_20211220.feed_actions)
                    union all
                    (SELECT DISTINCT toDate(time) as day, user_id as user
                        , 0 as feed, 1 as sent, 0 as recieved
                    FROM simulator_20211220.message_actions)
                    union all
                    (SELECT DISTINCT toDate(time) as day, reciever_id as user
                        , 0 as feed, 0 as sent, 1 as recieved
                    FROM simulator_20211220.message_actions)
                ) 
            Select DISTINCT day, user 
                , age, city, country, gender, os, source,  exp_group
                , sum(feed) over (partition by user, day) as feed_day
                , sum(sent) over (partition by user, day) as sent_day
                , sum(recieved) over (partition by user, day) as recieved_day
                , sum(feed) over (partition by user) as feed_ever
                , sum(sent) over (partition by user) as sent_ever
                , sum(recieved) over (partition by user) as recieved_ever
            FROM src
            LEFT JOIN us_list on src.user=us_list.user_id""").df
    
    DailyUsersUsedServices = data[['day','feed_day','sent_day', 'recieved_day']].groupby(['day'], as_index=True).sum()
    
    net_recievers =  data[(data["feed_ever"]==0) & (data["sent_ever"]==0)].groupby("day")["user"].count()
    net_senders =  data[(data["recieved_ever"]==0)].groupby("day")["sent_day"].sum()
    recievers =  data[(data["feed_ever"]>0) & (data["sent_ever"]==0)  & (data["recieved_ever"]>0)].groupby("day")["recieved_day"].sum()
    dialogs =  data[((data["sent_day"]>0) | (data["recieved_day"]>0)) & (data["sent_ever"]>0)  & (data["recieved_ever"]>0)].groupby("day")["user"].count()
    
    DailyUsersSplitByServices = pd.DataFrame({'чистые получатели': net_recievers, 
                                          'только отправляли сообщения': net_senders, 
                                          'только получали сообщения  (с опытом в ленте)': recievers,
                                          'участвовали в диалогах': dialogs,
                                         })
    
    SentOnlyAds = data[(data["feed_ever"]==0) & (data["source"]=="ads")].groupby("day")["sent_day"].sum() 
    FeedOnlyAds = data[(data["sent_ever"]==0) & (data["source"]=="ads")].groupby("day")["feed_day"].sum() 
    BothAds = data[((data["sent_day"]>0) | (data["feed_day"]>0)) & (data["sent_ever"]>0)  & (data["feed_ever"]>0) & (data["source"]=="ads")].groupby("day")["user"].count()
    SentOnlyOrganic = data[(data["feed_ever"]==0) & (data["source"]=="organic")].groupby("day")["sent_day"].sum() 
    FeedOnlyOrganic = data[(data["sent_ever"]==0) & (data["source"]=="organic")].groupby("day")["feed_day"].sum() 
    BothOrganic = data[((data["sent_day"]>0) & (data["feed_day"]>0)) & (data["sent_ever"]>0)  & (data["feed_ever"]>0) & (data["source"]=="organic")].groupby("day")["user"].count()    
    
    DAU_ads = pd.DataFrame({'только отправка сообщений': SentOnlyAds, 
                        'только новостная лента': FeedOnlyAds, 
                        'опыт в обоих сервисах': BothAds
                        })

    DAU_organic = pd.DataFrame({'только отправка сообщений': SentOnlyOrganic, 
                        'только новостная лента': FeedOnlyOrganic, 
                        'опыт в обоих сервисах': BothOrganic
                        })
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('Количество пользователей',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(data = DailyUsersUsedServices)
    ax.set_title("Ежедневное пользование сервисами", fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.legend(labels = ["новостной лентой", "отправка сообщений", "получение сообщений"])
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.name = 'dayily_service_plot.png'
    plot_object.seek(0)
    plt.close()
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('Количество пользователей',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(data = DailyUsersSplitByServices)
    ax.set_title("Пользователи мессенджера по группам имющегося опыта", fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plot_object2 = io.BytesIO()
    plt.savefig(plot_object2)
    plot_object2.name = 'UsersOfMessanger_plot.png'
    plot_object2.seek(0)
    plt.close()
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('Количество пользователей',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(data = DAU_ads)
    ax.set_title("DAU ads c разбивкой по опыту в приложении", fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plot_object3 = io.BytesIO()
    plt.savefig(plot_object3)
    plot_object3.name = 'DAU_ads_plot.png'
    plot_object3.seek(0)
    plt.close()
    
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_ylabel('Количество пользователей',  fontsize=15)
    ax.set_xlabel('Дата',  fontsize=15)
    sns.lineplot(data = DAU_organic)
    ax.set_title("DAU organic c разбивкой по опыту в приложении", fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=10)
    plot_object4 = io.BytesIO()
    plt.savefig(plot_object4)
    plot_object4.name = 'DAU_organic_plot.png'
    plot_object4.seek(0)
    plt.close()
    
    bot.send_media_group(chat_id=chat_id, media = [imp(plot_object),imp(plot_object2),imp(plot_object3),imp(plot_object4)])

try:
    FeedSending()
except Exception as er:
    print(er)
