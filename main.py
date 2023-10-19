from whatsapp_manager import account_manager
import json
import telebot
import threading
import queue

with open("bot_token.json", "r") as f:
    data = json.load(f)
    token = data["token"]
    password = data["password"]

bot = telebot.TeleBot(token)

correct_password = password

# İşlem sırasını takip etmek için bir işlem kuyruğu oluşturun
task_queue = queue.Queue()

@bot.message_handler(func=lambda message: True)
def handle_start(message):
    message_text = message.text
    message_splitted = message.text.split()

    if len(message_splitted) == 3:
        url, phone_number, password = message_splitted[0], message_splitted[1], message_splitted[2]
        if password == correct_password:
            bot.reply_to(message, "Password is correct, processes are added to the queue.")
            task_queue.put((url, phone_number))
        else:
            bot.reply_to(message, "Wrong password.")
    else:
        bot.reply_to(message, "Wrong format")

def process_task():
    while True:
        url, phone_number = task_queue.get()  # İşlemi sıradan al
        # İşlemi gerçekleştir
        app.download_youtube_video(url, phone_number)
        # İşlem tamamlandığında işlem sırasından çıkartılabilir, ancak işleme yöntemini kendi ihtiyaçlarınıza göre uyarlamalısınız
        task_queue.task_done()

if __name__ == "__main__":
    app = account_manager()
    app.prepare_driver(headless=False, data_dir="src\\chrome_log")
    if app.login_whatsapp():
        # İşlem sırasını işleyen bir iş parçacığı başlatın
        task_thread = threading.Thread(target=process_task)
        task_thread.daemon = True  # Ana program sona erdiğinde bu iş parçacığı da sona ersin
        task_thread.start()

        bot.polling()