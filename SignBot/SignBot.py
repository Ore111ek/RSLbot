
import telebot

bot = telebot.TeleBot('5744274566:AAHRaYf-jV2o0ibwQWlL92Bh3jpLh3CTEcg')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Ti Lox, {message.from_user.id}")

@bot.message_handler(commands=['videoNote'])
def testVN(message):
    videonote = open('VideoNoteTest.mp4', 'rb')
    bot.send_video_note(message.chat.id, videonote)

bot.polling(none_stop=True)