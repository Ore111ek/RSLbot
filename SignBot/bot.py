import telebot
from telebot import types
import re

from db import BotDB
BotDB = BotDB('RSLbot.db')

bot = telebot.TeleBot('5744274566:AAHRaYf-jV2o0ibwQWlL92Bh3jpLh3CTEcg')
ADMIN_id = 923048680

isRunning = 0
isRunningSearch = 0
isRunningAddCat = 0

def form_text_num_signs(num):
    text = 'Найден ' if num==1 else 'Найдено '
    text += str(num)
    if num==1:
        text += ' жест:\n' 
    elif num%10>4 or num%10==0 or (num>10 and num<15):
        text += ' жестов:\n' 
    else:
        text += ' жеста:\n'
    return text

def form_text_num_cats(num):
    text = 'Найдена ' if num==1 else 'Найдено '
    text += str(num)
    if num==1:
        text += ' категория:\n' 
    elif num%10>4 or num%10==0 or (num>10 and num<15):
        text += ' категорий:\n' 
    else:
        text += ' категории:\n'
    return text

def form_text_num_sens(num):
    text = 'Найдено ' if num==1 else 'Найдено '
    text += str(num)
    if num==1:
        text += ' предложение:\n' 
    elif num%10>4 or num%10==0 or (num>10 and num<15):
        text += ' предложений:\n' 
    else:
        text += ' предложения:\n'
    return text

def form_sign_keyboard(chat_id,sign_id):
    user = BotDB.get_user_by_user_id(chat_id)        
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    btns = []
    if BotDB.search_sign_fav(chat_id,sign_id):
        btn = types.InlineKeyboardButton("✔️ "+user[9], callback_data = '/signFoldCh_fav_f'+str(sign_id))
    else:
        btn = types.InlineKeyboardButton("❌ "+user[9], callback_data = '/signFoldCh_fav_t'+str(sign_id))
    btns.append(btn)
    if BotDB.search_sign_learn(chat_id,sign_id):
        btn = types.InlineKeyboardButton("✔️ "+user[10], callback_data = '/signFoldCh_learn_f'+str(sign_id))
    else:
        btn = types.InlineKeyboardButton("❌ "+user[10], callback_data = '/signFoldCh_learn_t'+str(sign_id))
    btns.append(btn)
    markup.row(*btns)
    return markup

def form_list_msg_key(objects,pg_num,pg_attr,obj_ref = '/show_sign',pg_ref = '/search_pg'):
    objects.sort(key=lambda x: x[1])
    objects.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)

    if obj_ref.startswith("/show_sign"):
        msg = '<b>'+form_text_num_signs(len(objects))+'</b>'
    elif obj_ref.startswith("/show_cat"):
        msg = '<b>'+form_text_num_cats(len(objects))+'</b>'
    else:
        msg = '<b>'+form_text_num_sens(len(objects))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    pg_num -= 1
    first_objects = objects[pg_num*9:(pg_num+1)*9] if len(objects)-pg_num*9 > 8 else objects[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in first_objects:
        i += 1
        msg += s[1]
        if obj_ref.startswith("/show_sign"):
            msg += f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        else:
            msg += '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = obj_ref +"_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(objects)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница '+str(pg_num)+' из '+str(num_of_pages)+'</b>'
        prev_pg = pg_num-1 if pg_num != 1 else num_of_pages
        next_pg = pg_num+1 if pg_num != num_of_pages else 1
        btn = types.InlineKeyboardButton("⬅️", callback_data = pg_ref+'_'+str(prev_pg)+'_'+str(pg_attr))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = pg_ref+'_'+str(next_pg)+'_'+str(pg_attr))
        btns.append(btn)
        markup.row(*btns)
    return msg, markup

@bot.message_handler(commands="start")
def start(message):
    print(message.text)
    if message.text == "/start":
        if(not BotDB.user_exists(message.from_user.id)):
            BotDB.add_user(message.from_user.id,message.from_user.username,message.from_user.first_name,message.from_user.last_name,1)
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")
    else:
        if re.findall("show_sign",message.text):
            show_sign_handler(message)

@bot.message_handler(is_owner=True, commands="ping")
def cmd_ping_bot(message):
    message.reply("<b>👊 Up & Running!</b>\n\n")


@bot.message_handler(commands='add_sign')
def add_sign_handler(message):
    chat_id = message.chat.id
    text = message.text
    msg = bot.send_message(chat_id, 'Отправьте видео жеста')
        #bot.register_next_step_handler(msg, ask_sign_video) #askSource

@bot.message_handler(content_types=['video','animation','video_note'])
def ask_sign_video(message):
    global isRunning
    if not isRunning:
        isRunning = True
        chat_id = message.chat.id
        """
        if not message.video:
            msg = bot.send_message(chat_id, 'Жест должен быть в формате видео, отправьте ещё раз')
            bot.register_next_step_handler(msg, ask_sign_video) #askSource
            return
        """
        if message.video:
            file_name = message.json['video']['file_name']
            file_info = bot.get_file(message.video.file_id)
            #bot.send_message(chat_id, 'Распознано video')
        elif message.animation:
            file_name = message.json['animation']['file_name']
            file_info = bot.get_file(message.animation.file_id)
            #bot.send_message(chat_id, 'Распознано animation')
        elif message.video_note:
            file_name = message.json['video_note']['file_id']
            file_info = bot.get_file(message.video_note.file_id)
            #bot.send_message(chat_id, 'Распознано video_note')
        else:
            bot.send_message(chat_id, 'Неизвестный тип файла')
        global file_content
        with open(file_name, "wb") as f:
            file_content = bot.download_file(file_info.file_path)
            f.write(file_content)

        msg = bot.send_message(chat_id, 'Напишите название жеста')
        bot.register_next_step_handler(msg, add_ask_sign_name)

def add_ask_sign_name(message):
    chat_id = message.chat.id
    global sign_name
    sign_name = message.text
    if not sign_name:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
    markup.add(types.KeyboardButton('Существительное'),types.KeyboardButton('Глагол'))
    markup.add(types.KeyboardButton('Наречие'),types.KeyboardButton('Прилагательное'))
    msg = bot.send_message(chat_id, 'Выберите часть речи', reply_markup = markup)
    bot.register_next_step_handler(msg, add_ask_sign_part)

def add_ask_sign_part(message):
    global isRunning
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_ask_sign_part) #askSource
        return
    BotDB.add_sign(message.from_user.id,1,sign_name,text,"",file_content,None,None,None,BotDB.get_user_by_user_id(chat_id)[8])
    isRunning = False
    bot.send_message(chat_id, 'Спасибо за вклад, жест "' + sign_name + '" добавлен)', reply_markup=types.ReplyKeyboardRemove())
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

@bot.message_handler(commands='search_sign')
def search_handler(message):
    global isRunning
    if not isRunning:
        isRunning = True
        chat_id = message.chat.id
        text = message.text
        msg = bot.send_message(chat_id, 'Напишите имя искомого жеста')
        bot.register_next_step_handler(msg, search_ask_sign_name) #askSource

def search_ask_sign_name(message):
    global isRunning
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, search_ask_sign_name) #askSource
        return
    
    signs = BotDB.search_signs(text,chat_id);

    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    msg = '<b>'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    first_signs = signs[0:9] if len(signs) > 8 else signs
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница 1 из '+str(num_of_pages)+'</b>'
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/search_pg_'+str(num_of_pages)+'_'+text)
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/search_pg_2_'+text)
        btns.append(btn)
        markup.row(*btns)
    """

    msg, markup = form_list_msg_key(signs,1,text,obj_ref = '/show_sign',pg_ref = '/search_pg')

    isRunning = False
    #markup.add(types.InlineKeyboardButton(":arrow_right:", url=""))
    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/search_pg",c.data))
def process_callback_search_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])
    text = re.split("_", callback_query.data)[3]

    signs = BotDB.search_signs(text,chat_id);
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    msg = '<b>'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    pg_num -= 1
    first_signs = signs[pg_num*9:(pg_num+1)*9] if len(signs)-pg_num*9 > 8 else signs[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница '+str(pg_num)+' из '+str(num_of_pages)+'</b>'
        prev_pg = pg_num-1 if pg_num != 1 else num_of_pages
        next_pg = pg_num+1 if pg_num != num_of_pages else 1
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/search_pg_'+str(prev_pg)+'_'+text)
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/search_pg_'+str(next_pg)+'_'+text)
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,pg_num,text,obj_ref = '/show_sign',pg_ref = '/search_pg')

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_sign",c.data))
def process_callback_show_sign(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sign_id = int(re.findall("\d+", callback_query.data)[0])
    sign = BotDB.search_sign(sign_id);
    msg = f'<b>{sign[0]}</b> (<i>{sign[1]}</i>)\n{sign[2]}'
    #videonote = open('VideoNoteTest.mp4', 'rb')
    #bot.send_video(chat_id, sign[3])
    
    markup = form_sign_keyboard(chat_id,sign_id)
    #bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup=markup)
    bot.send_video(chat_id, sign[3], caption = msg, parse_mode = 'html', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: re.findall("/signFoldCh",c.data))
def process_callback_change_sign_folder(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sign_id = int(re.findall("\d+", callback_query.data)[0])
    if re.split("_", callback_query.data)[1] == 'fav':
        if re.split("_", callback_query.data)[2].startswith('t'):
            BotDB.make_sign_fav(chat_id,sign_id)
        else:
            BotDB.make_sign_nfav(chat_id,sign_id)
    else:
        if re.split("_", callback_query.data)[2].startswith('t'):
            BotDB.make_sign_learn(chat_id,sign_id)
        else:
            BotDB.make_sign_nlearn(chat_id,sign_id)

    markup = form_sign_keyboard(chat_id,sign_id)
    bot.edit_message_reply_markup(chat_id = chat_id, message_id = callback_query.message.message_id, reply_markup=markup)

@bot.message_handler(commands='print_dict')
def print_dict_handler(message):
    chat_id = message.chat.id
    signs = BotDB.search_signs('', chat_id);
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    #msg = 'Найдены жесты:\n'
    msg = form_text_num_signs(len(signs))
    for s in signs:
        msg += s[1]
        msg +=  f' ({s[2]})\n' if len(s[2]) > 0 else '\n'
    bot.send_message(chat_id, msg)

@bot.message_handler(commands='show_sign')
def show_sign_handler(message):
    chat_id = message.chat.id
    sign_id = int(re.findall("\d+", message.text)[0])
    sign = BotDB.search_sign(sign_id);
    msg = f'<b>{sign[0]}</b> (<i>{sign[1]}</i>)\n{sign[2]}'
    #videonote = open('VideoNoteTest.mp4', 'rb')
    bot.send_video(message.chat.id, sign[3], caption = msg, parse_mode = 'html')
    

   # bot.send_message(chat_id, msg, parse_mode = 'html')

@bot.message_handler(commands='send_all')
def send_all_handler(message):
    if message.from_user.id == ADMIN_id:
        text = re.split("send_all", message.text)[1]
        users = BotDB.get_users_by_name('')
        for user in users:
            msg = f'Привет, <b>{user[3]}'
            msg += f' {user[4]}!</b>' if not user[4] is None else '!</b>'
            msg += text
            bot.send_message(user[1], msg, parse_mode = 'html')
        
@bot.message_handler(commands='show_fav')
def show_fav_handler(message):
    chat_id = message.chat.id

    signs = BotDB.search_signs_fav(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    
    msg = '<b>'+user[9]+'\n'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    first_signs = signs[0:9] if len(signs) > 8 else signs
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница 1 из '+str(num_of_pages)+'</b>'
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_fav_pg_'+str(num_of_pages))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_fav_pg_2_')
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,1,'',obj_ref = '/show_sign',pg_ref = '/show_fav_pg')
    msg = '<b>'+user[9]+'</b>\n'+msg

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_fav_pg",c.data))
def process_callback_search_other_pg_fav(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    signs = BotDB.search_signs_fav(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    
    msg = '<b>'+user[9]+'\n'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    pg_num -= 1
    first_signs = signs[pg_num*9:(pg_num+1)*9] if len(signs)-pg_num*9 > 8 else signs[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница '+str(pg_num)+' из '+str(num_of_pages)+'</b>'
        prev_pg = pg_num-1 if pg_num != 1 else num_of_pages
        next_pg = pg_num+1 if pg_num != num_of_pages else 1
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_fav_pg_'+str(prev_pg))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_fav_pg_'+str(next_pg))
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,pg_num,'',obj_ref = '/show_sign',pg_ref = '/show_fav_pg')
    msg = '<b>'+user[9]+'</b>\n'+msg

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.message_handler(commands='show_learn')
def show_learn_handler(message):
    chat_id = message.chat.id

    signs = BotDB.search_signs_learn(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    
    msg = '<b>'+user[10]+'\n'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    first_signs = signs[0:9] if len(signs) > 8 else signs
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница 1 из '+str(num_of_pages)+'</b>'
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_learn_pg_'+str(num_of_pages))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_learn_pg_2_')
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,1,'',obj_ref = '/show_sign',pg_ref = '/show_learn_pg')
    msg = '<b>'+user[10]+'</b>\n'+msg

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_learn_pg",c.data))
def process_callback_search_other_pg_learn(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    signs = BotDB.search_signs_learn(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    
    msg = '<b>'+user[10]+'\n'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    pg_num -= 1
    first_signs = signs[pg_num*9:(pg_num+1)*9] if len(signs)-pg_num*9 > 8 else signs[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница '+str(pg_num)+' из '+str(num_of_pages)+'</b>'
        prev_pg = pg_num-1 if pg_num != 1 else num_of_pages
        next_pg = pg_num+1 if pg_num != num_of_pages else 1
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_learn_pg_'+str(prev_pg))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_learn_pg_'+str(next_pg))
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,pg_num,'',obj_ref = '/show_sign',pg_ref = '/show_learn_pg')
    msg = '<b>'+user[10]+'</b>\n'+msg

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.message_handler(commands='add_cat')
def add_cat_ask_name(message):
    global isRunning
    if not isRunning:
        isRunning = True
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, 'Напишите название категории')
        bot.register_next_step_handler(msg, add_cat_with_name)

def add_cat_with_name(message):
    global isRunning
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_cat_with_name) #askSource
        return
    BotDB.add_cat(text,"")
    isRunning = False
    bot.send_message(chat_id, 'Создана категория "' + text + '"', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands='show_cats')
def show_cats_handler(message):
    chat_id = message.chat.id

    cats = BotDB.search_all_cats();
    """
    cats.sort(key=lambda x: x[1])
    cats.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)
    
    msg = '<b>'+form_text_num_cats(len(cats))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    first_cats = cats[0:9] if len(cats) > 8 else cats
    btns = []
    i = 0
    for s in first_cats:
        i += 1
        msg += s[1]+'\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_cat_f_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(cats)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница 1 из '+str(num_of_pages)+'</b>'
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_cats_pg_'+str(num_of_pages))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_cats_pg_2_')
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(cats,1,'',obj_ref = '/show_cat_f',pg_ref = '/show_cats_pg')

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cats_pg",c.data))
def process_callback_show_cats_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    cats = BotDB.search_all_cats(chat_id);
    """
    cats.sort(key=lambda x: x[1])
    cats.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)

    msg = '<b>'+form_text_num_cats(len(cats))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    pg_num -= 1
    first_cats = cats[pg_num*9:(pg_num+1)*9] if len(cats)-pg_num*9 > 8 else cats[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in first_cats:
        i += 1
        msg += s[1]+'\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_cat_f_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(cats)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница '+str(pg_num)+' из '+str(num_of_pages)+'</b>'
        prev_pg = pg_num-1 if pg_num != 1 else num_of_pages
        next_pg = pg_num+1 if pg_num != num_of_pages else 1
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_cats_pg_'+str(prev_pg))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_cats_pg_'+str(next_pg))
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(cats,pg_num,'',obj_ref = '/show_cat_f',pg_ref = '/show_cats_pg')

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cat_f_",c.data))
def process_callback_show_cat_first_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    cat_id = int(re.findall("\d+", callback_query.data)[0])

    signs = BotDB.search_signs_in_cat(cat_id,chat_id);
    category = BotDB.get_cat_by_cat_id(cat_id)
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)

    
    msg = '<b>'+category[1]+'\n'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    first_signs = signs[0:9] if len(signs) > 8 else signs
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница 1 из '+str(num_of_pages)+'</b>'
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_cat_pg_'+str(num_of_pages)+'_'+str(cat_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_cat_pg_2_'+str(cat_id))
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,1,cat_id,obj_ref = '/show_sign',pg_ref = '/show_cat_pg')
    msg = '<b>'+category[1]+'</b>\n'+msg

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cat_pg_",c.data))
def process_callback_show_cat_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("_", callback_query.data)[3])
    cat_id = int(re.findall("_", callback_query.data)[4])

    signs = BotDB.search_signs_in_cat(cat_id,chat_id);
    category = BotDB.get_cat_by_cat_id(cat_id)
    """
    signs.sort(key=lambda x: x[1])
    signs.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)

    
    msg = '<b>'+category[1]+'\n'+form_text_num_signs(len(signs))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    pg_num -= 1
    first_signs = signs[pg_num*9:(pg_num+1)*9] if len(signs)-pg_num*9 > 8 else signs[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in first_signs:
        i += 1
        msg += s[1]
        msg +=  f' (<i>{s[2]}</i>)\n' if len(s[2]) > 0 else '\n'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = "/show_sign_" + str(s[0]))
        btns.append(btn)
        if i == 3:
            markup.row(*btns)
            btns = []
            i = 0
    if i != 0:
        markup.row(*btns)
        btns = []
    num_of_pages = ((len(signs)-1)//9)+1
    if num_of_pages > 1:
        msg += '<b>Страница 1 из '+str(num_of_pages)+'</b>'
        prev_pg = pg_num-1 if pg_num != 1 else num_of_pages
        next_pg = pg_num+1 if pg_num != num_of_pages else 1
        btn = types.InlineKeyboardButton("⬅️", callback_data = '/show_cat_pg_'+str(prev_pg)+'_'+str(cat_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("➡️", callback_data = '/show_cat_pg_'+str(next_pg)+'_'+str(cat_id))
        btns.append(btn)
        markup.row(*btns)
    """
    msg, markup = form_list_msg_key(signs,pg_num,cat_id,obj_ref = '/show_sign',pg_ref = '/show_cat_pg')
    msg = '<b>'+category[1]+'</b>\n'+msg

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

bot.polling(none_stop=True)