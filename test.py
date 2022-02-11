import telegram
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import os

def testSending(chat=None):    
    bot = telegram.Bot(token=os.environ.get("ivanov_kc_bot_token"))
    chat_id = -674009613
    bot.send_message(chat_id=chat_id, text="I'm a bot, please talk to me!")
    x = np.arange(1,10,1)
    y = np.random.choice(5, len(x))
    sns.set()
    sns.lineplot(x,y)
    plt.title('test plot')
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.name = 'test_plot.png'
    plot_object.seek(0)
    plt.close()
    bot.send_photo(chat_id=chat_id, photo = plot_object)

try:
    testSending()
except Exception as er:
    print(er)
