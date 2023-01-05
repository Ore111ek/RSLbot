from aiogram import types
from dispatcher import dp, bot

from bot import BotDB
# Personal actions goes here (bot direct messages)
# Here is some example !ping command ...
isRunning = 0

@dp.message_handler(commands="start")
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id,message.from_user.username,message.from_user.first_name,message.from_user.last_name,1)
    await bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")

@dp.message_handler(is_owner=True, commands="ping")
async def cmd_ping_bot(message: types.Message):
    await message.reply("<b>👊 Up & Running!</b>\n\n")


@dp.message_handler(commands='add_sign')
async def start_handler(message):
    global isRunning
    if not isRunning:
        isRunning = True
        chat_id = message.chat.id
        text = message.text
        msg = bot.send_message(chat_id, 'Отправьте видео жеста')
        await dp.register_next_step_handler(msg, ask_sign_video) #askSource

@dp.message_handler(content_types=['video','video_note'])
async def ask_sign_video(message):
    chat_id = message.chat.id
    if not message.video_note:
        msg = bot.send_message(chat_id, 'Жест должен быть в формате видео, отправьте ещё раз')
        await dp.register_next_step_handler(msg, ask_sign_video) #askSource
        return

    file_name = message.json['video']['file_name']
    file_info = bot.get_file(message.video.file_id)
    global file_content
    with open(file_name, "wb") as f:
        file_content = bot.download_file(file_info.file_path)
        f.write(file_content)

    msg = bot.send_message(chat_id, 'Напишите название жеста')
    await dp.register_next_step_handler(msg, ask_sign_name)

async def ask_sign_name(message):
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        await dp.register_next_step_handler(msg, ask_sign_name) #askSource
        return
    BotDB.add_sign(message.from_user.id,1,text,"",file_content,None,None)
    isRunning = False
    await bot.send_message(chat_id, 'Спасибо за вклад, жест "' + text + '" добавлен в базу данных)')

    """
def askAge(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(chat_id, 'Возраст должен быть числом, введите ещё раз.')
        bot.register_next_step_handler(msg, askAge) #askSource
        return
    msg = bot.send_message(chat_id, 'Спасибо, я запомнил что вам ' + text + ' лет.')
    isRunning = False
    """
