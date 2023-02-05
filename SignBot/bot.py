import telebot
from telebot import types
import re

from db import BotDB
BotDB = BotDB('RSLbot.db')

bot = telebot.TeleBot('5661572549:AAGDgWFtN-b-p-0aj4Vljs0Tbl353HWjFP8')
ADMIN_id = 923048680

isRunning = {}
sim_video_id = {}
sim_video2_id = {}
comp_video_id = {}
comp_sen_video_id = {}
files = {}
Sign_Sen_Flag = {}
Sign_Sen_search_Flag = {}
Sign_Sen_comm_Flag = {}

comm_text = {}
dialect_name = {}
sign_name = {}
video_id = {}
sign_id = {}
sen_id = {}
comm_id = {}
delete_flag = {}

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

def form_sign_text(sign,ver_num):
    msg = f'<b>{sign[1]}</b> (<i>{sign[2]}</i>)'
    if ver_num:
        msg += f', {ver_num} вариант'
    msg += f'\n{sign[3]}'
    return msg

def form_sen_text(sen,ver_num):
    msg = f'<b>{sen[1]}</b>'
    if ver_num:
        msg += f', {ver_num} вариант'

    msg += f'\n{sen[5]}'
    return msg

def get_video_from_msg(msg):
    if msg.document:
        file_name = msg.json['document']['file_name']
        file_info = bot.get_file(msg.document.file_id)
    elif msg.video:
        #file_name = message.json['video']['file_name']
        file_name = 'sign_'+str(msg.video.file_id)
        file_info = bot.get_file(msg.video.file_id)
        #bot.send_message(chat_id, 'Распознано video')
    elif msg.animation:
        file_name = msg.json['animation']['file_name']
        file_info = bot.get_file(msg.animation.file_id)
        #bot.send_message(chat_id, 'Распознано animation')
    elif msg.video_note:
        file_name = msg.json['video_note']['file_id']
        file_info = bot.get_file(msg.video_note.file_id)
        #bot.send_message(chat_id, 'Распознано video_note')
    else:
        file_name = None
        file_info = None
    return file_name,file_info

def form_sen_keyboard(chat_id,sen_id,video_id = 0):
    user = BotDB.get_user_by_user_id(chat_id)
    if sen_id == 0:
        sen = BotDB.search_sen_by_video(video_id)
        sen_id = sen[0]
    else:
        sen = BotDB.search_sen(sen_id,chat_id)

    videos = BotDB.search_sen_videos(sen_id,chat_id)
    if video_id == 0:
        video_id = videos[0][0]
        author_id = videos[0][3]
        ver_num = 1
        video_privacy = videos[0][4]
    else:
        i = 1
        for v in videos:
            if video_id == v[0]:
                ver_num = i
                author_id = v[3]
                video_privacy = v[4]
            i += 1
    if len(videos) < 2:
        ver_num = 0
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    btns = []
    #more_videos = BotDB.search_sign_more_video(sign_id, chat_id)

    num = len(videos)
    if num>1:
        num_of_rows = (num-1)//8+1
        i=1
        for v in videos:
            btn = types.InlineKeyboardButton(str(i), callback_data = '/show_ver_sen_'+str(videos[i-1][0])+'_'+str(sen_id))
            btns.append(btn)
            if (num_of_rows > 1) and (i%((num+num%2)//num_of_rows) == 0):
                markup.row(*btns)
                btns = []
            i += 1
        markup.row(*btns)
        btns = []

    categories = BotDB.get_cat_by_sen_id(sen_id)
    if len(categories):
        for cat in categories:
            btn = types.InlineKeyboardButton(cat[1], callback_data = '/show_cat_sens_f_1_'+str(cat[0]))
            btns.append(btn)
    if len(BotDB.search_comp_signs_by_sen(video_id,chat_id)):
        btn = types.InlineKeyboardButton("Жесты", callback_data = '/show_comp_sign_f_1_'+str(video_id))
        btns.append(btn)
    comments = BotDB.get_comms_by_sen_video_id(video_id,chat_id)
    if len(comments):
        btn = types.InlineKeyboardButton("Комментарии", callback_data = '/show_comms_sen_'+str(video_id))
        btns.append(btn)
    if user[7]%10 == 1 and ((len(categories) == 0) or (author_id == chat_id) or (user[7]//10 == 1)):
        btn = types.InlineKeyboardButton("Изм.категорию", callback_data = '/change_sen_cat_f_1_'+str(sen_id))
        btns.append(btn)
    if user[7]%10 == 1:
        btn = types.InlineKeyboardButton("+ Вариант", callback_data = '/add_sen_video_'+str(sen_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("Доб/Уд. Жесты", callback_data = '/add_comp_sen_'+str(video_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("+ Коммент", callback_data = '/add_comm_sen_'+str(video_id))
        btns.append(btn)
    if user[7]%10 == 1 and ((sen[3] == chat_id) or (user[7]//10 == 1)):
        btn = types.InlineKeyboardButton("✏️ Ред.", callback_data = '/ch_sen_info_'+str(sen_id))
        btns.append(btn)
    if user[7]%10 == 1 and ((author_id == chat_id) or (user[7]//10 == 1)):
        if video_privacy == 0:
            btn = types.InlineKeyboardButton("Публичный", callback_data = '/ch_video_priv_sen_f_'+str(video_id))
        else:
            btn = types.InlineKeyboardButton("Скрытый", callback_data = '/ch_video_priv_sen_t_'+str(video_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("❌ Удалить", callback_data = '/del_video_sen_'+str(video_id))
        btns.append(btn)
    if len(btns):
        markup.add(*btns)
    """
    btns = []
    if BotDB.search_sign_video_fav(chat_id,video_id):
        btn = types.InlineKeyboardButton("✔️ "+user[9], callback_data = '/signFoldCh_fav_f'+str(video_id))
    else:
        btn = types.InlineKeyboardButton("❌ "+user[9], callback_data = '/signFoldCh_fav_t'+str(video_id))
    btns.append(btn)
    if BotDB.search_sign_video_learn(chat_id,video_id):
        btn = types.InlineKeyboardButton("✔️ "+user[10], callback_data = '/signFoldCh_learn_f'+str(video_id))
    else:
        btn = types.InlineKeyboardButton("❌ "+user[10], callback_data = '/signFoldCh_learn_t'+str(video_id))
    btns.append(btn)
    markup.row(*btns)
    """
    return markup,ver_num

def form_sign_keyboard(chat_id,sign_id,video_id = 0):
    user = BotDB.get_user_by_user_id(chat_id)
    if sign_id == 0:
        sign = BotDB.search_sign_by_video(video_id)
        sign_id = sign[0]
    else:
        sign = BotDB.search_sign(sign_id,chat_id)

    videos = BotDB.search_sign_videos(sign_id,chat_id)
    if video_id == 0:
        video_id = videos[0][0]
        author_id = videos[0][3]
        ver_num = 1
        video_privacy = videos[0][4]
    else:
        i = 1
        for v in videos:
            if video_id == v[0]:
                ver_num = i
                author_id = v[3]
                video_privacy = v[4]
            i += 1
    if len(videos) < 2:
        ver_num = 0
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    btns = []
    #more_videos = BotDB.search_sign_more_video(sign_id, chat_id)

    num = len(videos)
    if num>1:
        num_of_rows = (num-1)//8+1
        i=1
        for v in videos:
            btn = types.InlineKeyboardButton(str(i), callback_data = '/show_ver_sign_'+str(videos[i-1][0])+'_'+str(sign_id))
            btns.append(btn)
            if (num_of_rows > 1) and (i%((num+num%2)//num_of_rows) == 0):
                markup.row(*btns)
                btns = []
            i += 1
        markup.row(*btns)
        btns = []

    categories = BotDB.get_cat_by_sign_id(sign_id)
    if len(categories):
        for cat in categories:
            btn = types.InlineKeyboardButton(cat[1], callback_data = '/show_cat_signs_f_1_'+str(cat[0]))
            btns.append(btn)
    comments = BotDB.get_comms_by_sign_video_id(video_id,chat_id)
    if len(comments):
        btn = types.InlineKeyboardButton("Комментарии", callback_data = '/show_comms_sign_'+str(video_id))
        btns.append(btn)
    if len(BotDB.search_sim_sign_videos(video_id,chat_id)):
        btn = types.InlineKeyboardButton("Похожие жесты", callback_data = '/show_sim_f_1_'+str(video_id))
        btns.append(btn)
    if len(BotDB.search_sens_by_comp_sign(video_id,chat_id)):
        btn = types.InlineKeyboardButton("Предложения", callback_data = '/show_comp_sen_f_1_'+str(video_id))
        btns.append(btn)
    if user[7]%10 == 1 and ((len(categories) == 0) or (author_id == chat_id) or (user[7]//10 == 1)):
        btn = types.InlineKeyboardButton("Изм.категорию", callback_data = '/change_sign_cat_f_1_'+str(sign_id))
        btns.append(btn)
    if user[7]%10 == 1:
        btn = types.InlineKeyboardButton("+ Вариант", callback_data = '/add_sign_video_'+str(sign_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("Доб/Уд.похожие", callback_data = '/add_sim_sign_'+str(video_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("Указ.предлож.", callback_data = '/add_comp_sign_'+str(video_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("+ Коммент", callback_data = '/add_comm_sign_'+str(video_id))
        btns.append(btn)
    if user[7]%10 == 1 and ((sign[4] == chat_id) or (user[7]//10 == 1)):
        btn = types.InlineKeyboardButton("✏️ Ред.", callback_data = '/ch_sign_info_'+str(sign_id))
        btns.append(btn)
    if user[7]%10 == 1 and ((author_id == chat_id) or (user[7]//10 == 1)):
        if video_privacy == 0:
            btn = types.InlineKeyboardButton("Публичный", callback_data = '/ch_video_priv_sign_f_'+str(video_id))
        else:
            btn = types.InlineKeyboardButton("Скрытый", callback_data = '/ch_video_priv_sign_t_'+str(video_id))
        btns.append(btn)
        btn = types.InlineKeyboardButton("❌ Удалить", callback_data = '/del_video_sign_'+str(video_id))
        btns.append(btn)
    if len(btns):
        markup.add(*btns)
    btns = []
    if BotDB.search_sign_video_fav(chat_id,video_id):
        btn = types.InlineKeyboardButton("✔️ "+user[9], callback_data = '/signFoldCh_fav_f'+str(video_id))
    else:
        btn = types.InlineKeyboardButton("❌ "+user[9], callback_data = '/signFoldCh_fav_t'+str(video_id))
    btns.append(btn)
    if BotDB.search_sign_video_learn(chat_id,video_id):
        btn = types.InlineKeyboardButton("✔️ "+user[10], callback_data = '/signFoldCh_learn_f'+str(video_id))
    else:
        btn = types.InlineKeyboardButton("❌ "+user[10], callback_data = '/signFoldCh_learn_t'+str(video_id))
    btns.append(btn)
    markup.row(*btns)
    return markup,ver_num

def form_list_msg_key(objects,pg_num,pg_attr,obj_ref = '/show_sign',pg_ref = '/search_pg',video_flag = 0):
    if not pg_ref.startswith('/show_comp_sign'):
        objects.sort(key=lambda x: x[1])
        objects.sort(key=lambda x: ord(x[1][0]) if x[1][0]!='Ё' else ord('Е')+0.5)

    if obj_ref.startswith("/show_sign"):
        msg = '<b>'+form_text_num_signs(len(objects))+'</b>'
    elif obj_ref.startswith("/show_cat") or obj_ref.startswith("/ch_sign_cat") or obj_ref.startswith("/ch_sen_cat"):
        msg = '<b>'+form_text_num_cats(len(objects))+'</b>'
    else:
        msg = '<b>'+form_text_num_sens(len(objects))+'</b>'
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 3
    
    pg_num -= 1
    pg_objects = objects[pg_num*9:(pg_num+1)*9] if len(objects)-pg_num*9 > 8 else objects[pg_num*9:]
    pg_num += 1
    btns = []
    i = 0
    for s in pg_objects:
        i += 1
        if pg_ref.startswith("/show_sim"):
            msg += f'<b>{s[1]}</b>'
        else:
            msg += s[1]
        if obj_ref.startswith("/show_sign"):
            msg += f' (<i>{s[2]}</i>)' if len(s[2]) > 0 else ''
            if pg_ref.startswith("/show_sim") and len(s[4]):
                if s[4]=='антонимы':
                    msg += ' - Антонимы\n'
                elif s[4]=='один жест - часть другого':
                    msg += f' - Один жест входит в состав другого\n'
                elif s[4]!='не знаю':
                    msg += f' - Отличаются по {s[4]}\n'
                else:
                    msg += '\n'
            else:
                msg += '\n'
        else:
            msg += '\n'
        callback_str = obj_ref +"_" + str(s[0])
        if video_flag == 1:
            if obj_ref.startswith("/show_sen"):
                callback_str += '_' + str(s[2])
            else:
                callback_str += '_' + str(s[3])
        else:
            callback_str += '_0'
        btn = types.InlineKeyboardButton(str(s[1]), callback_data = callback_str)
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

@bot.message_handler(func = lambda msg: not msg.text.startswith('/'), content_types=['text'])
def process_any_text(message):
    global isRunning
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
    #if (isRunning==False):
        search_ask_sign_name(message)

@bot.message_handler(commands=["start"])
def start(message):
    global isRunning
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        if(not BotDB.user_exists(message.from_user.id)):
            #BotDB.add_user(message.from_user.id,message.from_user.username,message.from_user.first_name,message.from_user.last_name,1)
            isRunning[chat_id] = True
            dialects = BotDB.get_dialects()
            btns = []
            if dialects:
                for d in dialects:
                    btn = types.KeyboardButton(d[1])
                    btns.append(btn)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
            markup.add(*btns)
            photo = open('RussiaMap.png', 'rb')
            msg = bot.send_photo(chat_id, photo, 'Выберите город (диалект) или напишите его название', reply_markup = markup)
            #msg = bot.send_message(chat_id, 'Выберите город (диалект) или напишите его название', reply_markup = markup)
            bot.register_next_step_handler(msg, registration_ask_city)
        else:
            bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")

@bot.message_handler(commands=["upd_user"])
def start(message):
    global isRunning
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        isRunning[chat_id] = True
        dialects = BotDB.get_dialects()
        btns = []
        for d in dialects:
            btn = types.KeyboardButton(d[1])
            btns.append(btn)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(*btns)
        photo = open('RussiaMap.png', 'rb')
        msg = bot.send_photo(chat_id, photo, 'Выберите город (диалект) или напишите его название', reply_markup = markup)
        bot.register_next_step_handler(msg, registration_ask_city)

def registration_ask_city(message):
    global dialect_name
    chat_id = message.chat.id
    dialect_name[chat_id] = message.text
    if not dialect_name[chat_id]:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, registration_ask_city) #askSource
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
    markup.add(types.KeyboardButton('Приватные'),types.KeyboardButton('Публичные'))
    msg = bot.send_message(chat_id, 'Выберите видимость ваших жестов <b>по умолчанию</b>. Если хотите, чтобы загружаемые вами жесты были видны только вам, '\
       'то выберите "Приватные". Если хотите участвовать в создании общего словаря, то выберите "Публичные". При необходимости <b>каждому жесту '\
       'можно указывать его личную видимость.</b>', parse_mode = 'html', reply_markup = markup)
    bot.register_next_step_handler(msg, registration_ask_privacy)

def registration_ask_privacy(message):
    global isRunning
    global dialect_name
    chat_id = message.chat.id
    privacy_type = message.text
    if privacy_type == 'Приватные':
        privacy = 1
    elif privacy_type == 'Публичные':
        privacy = 0
    else:
        msg = bot.send_message(chat_id, 'Выберите видимость ещё раз')
        bot.register_next_step_handler(msg, registration_ask_privacy) #askSource
        return
    dialect = BotDB.search_dialect(dialect_name[chat_id])
    if bool(dialect):
        dialect_id = dialect[0]
    else:
        dialect_id = BotDB.add_dialect(dialect_name[chat_id])
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id,message.from_user.username,message.from_user.first_name,message.from_user.last_name,dialect_id,privacy)
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Спасибо за регистрацию!",reply_markup=types.ReplyKeyboardRemove())
    else:
        BotDB.upd_user_dial_priv(chat_id,dialect_id,privacy)
        bot.send_message(message.chat.id, f"Данные пользователя изменены",reply_markup=types.ReplyKeyboardRemove())
    isRunning[chat_id] = False
    

@bot.message_handler(commands=["upd_folders"])
def upd_folders(message):
    global isRunning
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        if(not BotDB.user_exists(message.from_user.id)):
            #BotDB.add_user(message.from_user.id,message.from_user.username,message.from_user.first_name,message.from_user.last_name,1)
            start(message)
        else:
            isRunning[chat_id] = True
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
            markup.add(types.KeyboardButton('Мой словарь'),types.KeyboardButton('Изучаемое'))
            markup.add(types.KeyboardButton('Любимые'),types.KeyboardButton('Избранное'))
            msg = bot.send_message(chat_id, 'Выберите или напишите название 1-й папки с жестами', reply_markup = markup)
            bot.register_next_step_handler(msg, upd_folders_ask_fav)

def upd_folders_ask_fav(message):
    chat_id = message.chat.id
    fav_name = message.text
    if not fav_name:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, upd_folders_ask_fav) #askSource
        return
    BotDB.upd_user_fav(chat_id,fav_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
    markup.add(types.KeyboardButton('Мой словарь'),types.KeyboardButton('Изучаемое'))
    markup.add(types.KeyboardButton('Любимые'),types.KeyboardButton('Избранное'))
    msg = bot.send_message(chat_id, 'Выберите или напишите название 2-й папки с жестами', reply_markup = markup)
    bot.register_next_step_handler(msg, upd_folders_ask_learn)

def upd_folders_ask_learn(message):
    global isRunning
    chat_id = message.chat.id
    learn_name = message.text
    if not learn_name:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, upd_folders_ask_learn) #askSource
        return
    BotDB.upd_user_learn(chat_id,learn_name)
    isRunning[chat_id] = False
    bot.send_message(message.chat.id, f"Названия папок с жестами изменены",reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=["turn_mode"])
def turn_user_mode(message):
    chat_id = message.chat.id
    user = BotDB.get_user_by_user_id(chat_id)
    admin = user[7]
    text = ''
    if admin%10 == 1:
        BotDB.upd_user_admin(chat_id,admin-1)
        text = 'Включён режим просмотра'
    elif admin%10 == 0:
        BotDB.upd_user_admin(chat_id,admin+1)
        text = 'Включён режим редактирования'
    bot.send_message(chat_id, text)

@bot.callback_query_handler(func=lambda c: re.findall("/del_video",c.data))
def process_callback_del_video_sign(callback_query: types.CallbackQuery):
    global isRunning
    global delete_flag
    global video_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        chat_id = callback_query.from_user.id
        delete_flag[chat_id] = re.split('_', callback_query.data)[2]
        video_id[chat_id] = int(re.split('_', callback_query.data)[3])
        isRunning[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Удалить'),types.KeyboardButton('Отмена'))
        msg = bot.send_message(chat_id, 'Подтвердите удаление видео', reply_markup = markup)
        bot.register_next_step_handler(msg, del_video_ack)

def del_video_ack(message):
    global isRunning
    global delete_flag
    global video_id
    chat_id = message.chat.id
    text = message.text
    if text == 'Удалить':
        if chat_id not in delete_flag or delete_flag[chat_id] == 'sign':
            BotDB.del_sign_video(video_id[chat_id])
        else:
            BotDB.del_sen_video(video_id[chat_id])
        bot.send_message(chat_id, 'Видео удалено',reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, 'Удаление отменено',reply_markup=types.ReplyKeyboardRemove())
    isRunning[chat_id] = False
    del video_id[chat_id]

@bot.message_handler(is_owner=True, commands=["ping"])
def cmd_ping_bot(message):
    message.reply("<b>👊 Up & Running!</b>\n\n")


@bot.message_handler(commands=['add_sign'])
def add_sign_handler(message):
    #global files
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Отправьте видео жеста')
    global Sign_Sen_Flag
    Sign_Sen_Flag[chat_id] = True
    #files = []
        #bot.register_next_step_handler(msg, ask_sign_video) #askSource

@bot.message_handler(content_types=['document','video','animation','video_note'])
def ask_sign_video(message):
    global isRunning
    global Sign_Sen_Flag
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        file_name, file_info = get_video_from_msg(message)
        if file_info == None:
            bot.send_message(chat_id, 'Неизвестный тип файла или он отсутствует')
            return
        #global file_content
        global files
        with open(file_name, "wb") as f:
            file_content = bot.download_file(file_info.file_path)
            f.write(file_content)
            if chat_id not in files:
                files[chat_id] = []
            files[chat_id].append(file_content)
        if chat_id not in Sign_Sen_Flag or Sign_Sen_Flag[chat_id] == True:
            msg = bot.send_message(chat_id, 'Отправьте видео с другим вариантом жеста или напишите название жеста')
            bot.register_next_step_handler(msg, add_ask_sign_name)
        else:
            msg = bot.send_message(chat_id, 'Отправьте видео с другим вариантом предложения или напишите текст предложения')
            bot.register_next_step_handler(msg, add_ask_sen_name)

def add_ask_sign_name(message):
    global sign_name
    chat_id = message.chat.id

    if message.video or message.animation or message.video_note:
        #bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
        ask_sign_video(message)
    else:
        sign_name[chat_id] = message.text
        if not sign_name[chat_id]:
            msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
            bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
            return
        global isRunning
        isRunning[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Существительное'),types.KeyboardButton('Глагол'))
        markup.add(types.KeyboardButton('Наречие'),types.KeyboardButton('Прилагательное'))
        msg = bot.send_message(chat_id, 'Выберите или напишите свою часть речи', reply_markup = markup)
        bot.register_next_step_handler(msg, add_ask_sign_part)

def add_ask_sign_part(message):
    global isRunning
    global sign_name
    global files
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_ask_sign_part) #askSource
        return
    user = BotDB.get_user_by_user_id(chat_id)
    privacy = user[8]
    dialect = user[5]
    sign_id = BotDB.add_sign(chat_id,dialect,sign_name[chat_id],text,"",None,privacy)
    #sign = BotDB.search_sign_by_name_auth(sign_name, text, chat_id)
    if len(files[chat_id]):
        for f in files[chat_id]:
            video_id = BotDB.add_sign_video(chat_id, dialect, sign_id, f, privacy)
    del files[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Спасибо за вклад, жест "' + sign_name[chat_id] + '" добавлен', reply_markup=types.ReplyKeyboardRemove())
    """
    ВЫЗЫВАТЬ ФУНКЦИЮ ДЛЯ ПОКАЗА ДОБАВЛЕННОГО ЖЕСТА ПО ПОСЛЕДНЕМУ video_id!!!!!!!!!!!!!!
    """
    sign = BotDB.search_sign(sign_id,chat_id);
    video = BotDB.search_sign_videos(sign_id, chat_id)[0]
    markup,ver_num = form_sign_keyboard(chat_id,sign_id,0)
    msg = form_sign_text(sign,ver_num)
    bot.send_video(chat_id, video[2], caption = msg, parse_mode = 'html', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: re.findall("/add_comm",c.data))
def process_callback_add_comm(callback_query: types.CallbackQuery):
    global isRunning
    global video_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        Sign_Sen_comm_Flag[chat_id] = 1 if re.split('_', callback_query.data)[2] == 'sign' else 0
        video_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите текст комментария')
        bot.register_next_step_handler(msg, get_comm_text)

def get_comm_text(message):
    global comm_text
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, get_comm_text) #askSource
        return
    comm_text[chat_id] = text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
    markup.add(types.KeyboardButton('Приватный'),types.KeyboardButton('Публичный'))
    msg = bot.send_message(chat_id, 'Выберите видимость комментария', reply_markup = markup)
    bot.register_next_step_handler(msg, get_comm_privacy)

def get_comm_privacy(message):
    global isRunning
    global video_id
    global comm_text
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, get_comm_privacy) #askSource
        return
    privacy = 0 if text=="Публичный" else 1
    if Sign_Sen_comm_Flag[chat_id] == 1:
        BotDB.add_comm_sign(comm_text[chat_id], chat_id, video_id[chat_id], privacy)
    else:
        BotDB.add_comm_sen(comm_text[chat_id], chat_id, video_id[chat_id], privacy)
    del Sign_Sen_comm_Flag[chat_id]
    del video_id[chat_id]
    del comm_text[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Комментарий добавлен', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda c: re.findall("/show_comms_sign",c.data))
def process_callback_show_comms_sign(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    user = BotDB.get_user_by_user_id(chat_id)
    video_id = int(re.findall("\d+", callback_query.data)[0])
    comments = BotDB.get_comms_by_sign_video_id(video_id,chat_id)
    sign = BotDB.search_sign_by_video(video_id)

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 8
    btns = []

    msg = 'Комментарии к видео жеста <b>"'+ sign[1] +'"</b>:\n'
    for com in comments:
        if user[7]%10 == 1 and ((com[2] == chat_id) or (user[7]//10 == 1)):
            msg = msg + "<b>" + com[3] + "</b>("+str(com[0])+"): " + com[1] + "\n"
            btn = types.InlineKeyboardButton(str(com[0])+" ✏️", callback_data = '/ch_comm_sign'+str(com[0]))
            btns.append(btn)
            btn = types.InlineKeyboardButton(str(com[0])+" ❌", callback_data = '/del_comm_sign'+str(com[0]))
            btns.append(btn)
        else:
            msg = msg + "<b>" + com[3] + "</b>: " + com[1] + "\n"
        #msg = msg + com[0] + "\n"
        #msg = msg + "<b>" + com[1] + "</b>\n"
    markup.add(*btns)
    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/ch_comm_sign",c.data))
def process_callback_ch_comm_sign(callback_query: types.CallbackQuery):
    global isRunning
    global comm_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        comm_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новый текст комментария')
        bot.register_next_step_handler(msg, ch_comm_sign_text)

def ch_comm_sign_text(message):
    global isRunning
    global comm_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_comm_sign_text) #askSource
        return
    BotDB.ch_comm_sign_text(comm_id[chat_id],text)
    del comm_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Текст комментария изменён', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda c: re.findall("/ch_comm_sen",c.data))
def process_callback_ch_comm_sen(callback_query: types.CallbackQuery):
    global isRunning
    global comm_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        comm_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новый текст комментария')
        bot.register_next_step_handler(msg, ch_comm_sen_text)

def ch_comm_sen_text(message):
    global isRunning
    global comm_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_comm_sen_text) #askSource
        return
    BotDB.ch_comm_sen_text(comm_id[chat_id],text)
    del comm_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Текст комментария изменён', reply_markup=types.ReplyKeyboardRemove())
    """
    @bot.callback_query_handler(func=lambda c: re.findall("/del_video",c.data))
def process_callback_del_video_sign(callback_query: types.CallbackQuery):
    global isRunning
    global delete_flag
    global video_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        chat_id = callback_query.from_user.id
        delete_flag[chat_id] = re.split('_', callback_query.data)[2]
        video_id[chat_id] = int(re.split('_', callback_query.data)[3])
        isRunning[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Удалить'),types.KeyboardButton('Отмена'))
        msg = bot.send_message(chat_id, 'Подтвердите удаление видео', reply_markup = markup)
        bot.register_next_step_handler(msg, del_video_ack)

def del_video_ack(message):
    global isRunning
    global delete_flag
    global video_id
    chat_id = message.chat.id
    text = message.text
    if text == 'Удалить':
        if chat_id not in delete_flag or delete_flag[chat_id] == 'sign':
            BotDB.del_sign_video(video_id[chat_id])
        else:
            BotDB.del_sen_video(video_id[chat_id])
        bot.send_message(chat_id, 'Видео удалено',reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, 'Удаление отменено',reply_markup=types.ReplyKeyboardRemove())
    isRunning[chat_id] = False
    """

@bot.callback_query_handler(func=lambda c: re.findall("/del_comm_sign",c.data))
def process_callback_del_comm_sign(callback_query: types.CallbackQuery):
    global isRunning
    global comm_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        comm_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Удалить'),types.KeyboardButton('Отмена'))
        msg = bot.send_message(chat_id, 'Подтвердите удаление комментария', reply_markup = markup)
        bot.register_next_step_handler(msg, del_comm_sign)

def del_comm_sign(message):
    global isRunning
    global comm_id
    chat_id = message.chat.id
    text = message.text
    if text == 'Удалить':
        BotDB.del_comm_sign(comm_id[chat_id])
        bot.send_message(chat_id, 'Комментарий удалён',reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, 'Удаление отменено',reply_markup=types.ReplyKeyboardRemove())
    del comm_id[chat_id]
    isRunning[chat_id] = False

@bot.callback_query_handler(func=lambda c: re.findall("/del_comm_sen",c.data))
def process_callback_del_comm_sen(callback_query: types.CallbackQuery):
    global isRunning
    global comm_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        comm_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Удалить'),types.KeyboardButton('Отмена'))
        msg = bot.send_message(chat_id, 'Подтвердите удаление комментария', reply_markup = markup)
        bot.register_next_step_handler(msg, del_comm_sen)

def del_comm_sen(message):
    global isRunning
    global comm_id
    chat_id = message.chat.id
    text = message.text
    if text == 'Удалить':
        BotDB.del_comm_sen(comm_id[chat_id])
        bot.send_message(chat_id, 'Комментарий удалён',reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, 'Удаление отменено',reply_markup=types.ReplyKeyboardRemove())
    del comm_id[chat_id]
    isRunning[chat_id] = False

@bot.callback_query_handler(func=lambda c: re.findall("/show_comms_sen",c.data))
def process_callback_show_comms_sign(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    user = BotDB.get_user_by_user_id(chat_id)
    video_id = int(re.findall("\d+", callback_query.data)[0])
    comments = BotDB.get_comms_by_sen_video_id(video_id,chat_id)
    sen = BotDB.search_sen_by_video(video_id)

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 8
    btns = []

    msg = 'Комментарии к видео предложения <b>"'+ sen[1] +'"</b>:\n'
    for com in comments:
        if user[7]%10 == 1 and ((com[2] == chat_id) or (user[7]//10 == 1)):
            msg = msg + "<b>" + com[3] + "</b>("+str(com[0])+"): " + com[1] + "\n"
            btn = types.InlineKeyboardButton(str(com[0])+" ✏️", callback_data = '/ch_comm_sen'+str(com[0]))
            btns.append(btn)
            btn = types.InlineKeyboardButton(str(com[0])+" ❌", callback_data = '/del_comm_sen'+str(com[0]))
            btns.append(btn)
        else:
            msg = msg + "<b>" + com[3] + "</b>: " + com[1] + "\n"
        #msg = msg + com[0] + "\n"
        #msg = msg + "<b>" + com[1] + "</b>\n"
    markup.add(*btns)
    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)


@bot.callback_query_handler(func=lambda c: re.findall("/ch_sign_info",c.data))
def process_callback_ch_sign_info(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sign_id = int(re.findall("\d+", callback_query.data)[0])

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    btns = []
    btn = types.InlineKeyboardButton("Название", callback_data = '/ch_sign_name'+str(sign_id))
    btns.append(btn)
    btn = types.InlineKeyboardButton("Часть речи", callback_data = '/ch_sign_part'+str(sign_id))
    btns.append(btn)
    btn = types.InlineKeyboardButton("Описание", callback_data = '/ch_sign_desc'+str(sign_id))
    btns.append(btn)
    #btn = types.InlineKeyboardButton("Диалект", callback_data = '/ch_sign_dialect'+str(sign_id))
    #btns.append(btn)

    markup.add(*btns)
    sign = BotDB.search_sign(sign_id, chat_id)
    msg = "Изменить для жеста <b>" + sign[1] + "</b>"
    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sign_name",c.data))
def process_callback_ch_sign_name(callback_query: types.CallbackQuery):
    global isRunning
    global sign_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sign_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новое название жеста')
        bot.register_next_step_handler(msg, ch_sign_name)

def ch_sign_name(message):
    global isRunning
    global sign_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_sign_name) #askSource
        return
    BotDB.ch_sign_name(sign_id[chat_id],text)
    del sign_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Название жеста "' + text + '" установлено', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sign_part",c.data))
def process_callback_ch_sign_part(callback_query: types.CallbackQuery):
    global isRunning
    global sign_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sign_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Существительное'),types.KeyboardButton('Глагол'))
        markup.add(types.KeyboardButton('Наречие'),types.KeyboardButton('Прилагательное'))
        msg = bot.send_message(chat_id, 'Выберите или напишите свою часть речи', reply_markup = markup)
        bot.register_next_step_handler(msg, ch_sign_part)

def ch_sign_part(message):
    global isRunning
    global sign_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_sign_part) #askSource
        return
    BotDB.ch_sign_part(sign_id[chat_id],text)
    del sign_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Часть речи изменена на "' + text + '"', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sign_desc",c.data))
def process_callback_ch_sign_desc(callback_query: types.CallbackQuery):
    global isRunning
    global sign_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sign_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новое описание жеста')
        bot.register_next_step_handler(msg, ch_sign_desc)

def ch_sign_desc(message):
    global isRunning
    global sign_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_sign_desc) #askSource
        return
    BotDB.ch_sign_desc(sign_id[chat_id],text)
    del sign_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Описание жеста изменено', reply_markup=types.ReplyKeyboardRemove())

    """
    ДИАЛЕКТ НЕ У ЖЕСТА, ДИАЛЕКТ У ВИДЕО жеста
@bot.callback_query_handler(func=lambda c: re.findall("/ch_sign_dialect",c.data))
def process_callback_ch_sign_dialect(callback_query: types.CallbackQuery):
    global isRunning
    global sign_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sign_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новое описание жеста')
        bot.register_next_step_handler(msg, ch_sign_dialect)

def ch_sign_dialect(message):
    global isRunning
    global sign_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_sign_dialect) #askSource
        return
    BotDB.ch_sign_desc(sign_id[chat_id],text)
    del sign_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Диалект жеста изменён', reply_markup=types.ReplyKeyboardRemove())
    """

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sen_info",c.data))
def process_callback_ch_sign_info(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sen_id = int(re.findall("\d+", callback_query.data)[0])

    markup = types.InlineKeyboardMarkup()
    markup.row_width = 1
    btns = []
    btn = types.InlineKeyboardButton("Текст предложения", callback_data = '/ch_sen_name'+str(sen_id))
    btns.append(btn)
    btn = types.InlineKeyboardButton("Описание", callback_data = '/ch_sen_desc'+str(sen_id))
    btns.append(btn)
    #btn = types.InlineKeyboardButton("Диалект", callback_data = '/ch_sign_dialect'+str(sign_id))
    #btns.append(btn)

    markup.add(*btns)
    sen = BotDB.search_sen(sen_id, chat_id)
    msg = 'Изменить для предложения <b>"' + sen[1] + '"</b>'
    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sen_name",c.data))
def process_callback_ch_sen_name(callback_query: types.CallbackQuery):
    global isRunning
    global sen_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sen_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новый текст предложения')
        bot.register_next_step_handler(msg, ch_sen_name)

def ch_sen_name(message):
    global isRunning
    global sen_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_sen_name) #askSource
        return
    BotDB.ch_sen_name(sen_id[chat_id],text)
    del sen_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Текст предложения изменён', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sen_desc",c.data))
def process_callback_ch_sen_desc(callback_query: types.CallbackQuery):
    global isRunning
    global sen_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sen_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        isRunning[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите новое описание для предложения')
        bot.register_next_step_handler(msg, ch_sen_desc)

def ch_sen_desc(message):
    global isRunning
    global sen_id
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, ch_sen_desc) #askSource
        return
    BotDB.ch_sen_desc(sen_id[chat_id],text)
    del sen_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Описание предложения изменено', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['add_sen'])
def add_sign_handler(message):
    chat_id = message.chat.id
    global Sign_Sen_Flag
    Sign_Sen_Flag[chat_id] = False
    global isRunning
    if chat_id not in isRunning or isRunning[chat_id] == False:
        msg = bot.send_message(chat_id, 'Отправьте видео предложения на жестовом языке')
        bot.register_next_step_handler(msg, ask_sign_video) #askSource

def add_ask_sen_name(message):
    chat_id = message.chat.id
    global files
    if message.video or message.animation or message.video_note:
        #bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
        ask_sign_video(message)
    else:
        sen_name = message.text
        if not sen_name:
            msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
            bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
            return
        user = BotDB.get_user_by_user_id(chat_id)
        privacy = user[8]
        dialect = user[5]
        sen_id = BotDB.add_sen(chat_id, dialect, sen_name, privacy, '')
        if len(files[chat_id]):
            for f in files[chat_id]:
                video_id = BotDB.add_sen_video(chat_id, dialect, sen_id, f, privacy)
        del files[chat_id]
        bot.send_message(chat_id, 'Спасибо за вклад, предложение "' + sen_name + '" добавлено)')

@bot.message_handler(commands=['search_sign'])
def search_handler(message):
    global isRunning
    global Sign_Sen_search_Flag
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        isRunning[chat_id] = True
        text = message.text
        Sign_Sen_search_Flag[chat_id] = True
        msg = bot.send_message(chat_id, 'Напишите имя искомого жеста')
        bot.register_next_step_handler(msg, search_ask_sign_name) #askSource

@bot.message_handler(commands=['search_sen'])
def search_handler(message):
    global isRunning
    global Sign_Sen_search_Flag
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        isRunning[chat_id] = True
        text = message.text
        Sign_Sen_search_Flag[chat_id] = False
        msg = bot.send_message(chat_id, 'Напишите текст искомого предложения')
        bot.register_next_step_handler(msg, search_ask_sign_name) #askSource

def search_ask_sign_name(message):
    global isRunning
    global Sign_Sen_search_Flag
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, search_ask_sign_name) #askSource
        return
    
    if chat_id not in Sign_Sen_search_Flag or Sign_Sen_search_Flag[chat_id] == True:
        signs = BotDB.search_signs(text,chat_id);
        msg, markup = form_list_msg_key(signs,1,text+'_t',obj_ref = '/show_sign',pg_ref = '/search_pg')
    else:
        sens = BotDB.search_sens(text,chat_id);
        msg, markup = form_list_msg_key(sens,1,text+'_f',obj_ref = '/show_sen',pg_ref = '/search_pg')

    isRunning[chat_id] = False
    #markup.add(types.InlineKeyboardButton(":arrow_right:", url=""))
    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/search_pg",c.data))
def process_callback_search_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])
    text = re.split("_", callback_query.data)[3]
    flag = re.split("_", callback_query.data)[4]

    if flag == 't':
        signs = BotDB.search_signs(text,chat_id);
        msg, markup = form_list_msg_key(signs,pg_num,text+'_t',obj_ref = '/show_sign',pg_ref = '/search_pg')
    else:
        sens = BotDB.search_sens(text,chat_id);
        msg, markup = form_list_msg_key(sens,pg_num,text+'_f',obj_ref = '/show_sen',pg_ref = '/search_pg')

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_sim_",c.data))
def process_callback_search_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.split("_", callback_query.data)[3])
    video_id = int(re.split("_", callback_query.data)[4])

    signs = BotDB.search_sim_sign_videos(video_id,chat_id);
 
    msg, markup = form_list_msg_key(signs,pg_num,video_id,obj_ref = '/show_sign',pg_ref = '/show_sim_pg',video_flag = 1)
    main_sign = BotDB.search_sign_by_video(video_id)
    msg = f'Жесты, похожие на <b>{main_sign[1]}</b> (<i>{main_sign[2]}</i>)\n' + msg

    if re.split("_", callback_query.data)[2] == 'f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_comp_",c.data))
def process_callback_search_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.split("_", callback_query.data)[4])
    video_id = int(re.split("_", callback_query.data)[5])

    if re.split("_", callback_query.data)[2] == 'sign':
        signs = BotDB.search_comp_signs_by_sen(video_id,chat_id);
        msg, markup = form_list_msg_key(signs,pg_num,video_id,obj_ref = '/show_sign',pg_ref = '/show_comp_sign_pg',video_flag = 1)
        main_sen = BotDB.search_sen_by_video(video_id)
        msg = f'Жесты, используемые в предложении: <b>"{main_sen[1]}"</b>\n' + msg
    else:
        sens = BotDB.search_sens_by_comp_sign(video_id,chat_id);
        msg, markup = form_list_msg_key(sens,pg_num,video_id,obj_ref = '/show_sen',pg_ref = '/show_comp_sen_pg',video_flag = 1)
        main_sign = BotDB.search_sign_by_video(video_id)
        msg = f'Предложения, в которых используется жест <b>{main_sign[1]}</b> (<i>{main_sign[2]}</i>)\n' + msg
    if re.split("_", callback_query.data)[3] == 'f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_sen",c.data))
def process_callback_show_sign(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sen_id = int(re.split("_", callback_query.data)[2])
    video_id = int(re.split("_", callback_query.data)[3])
    if video_id == 0:
        video = BotDB.search_sen_videos(sen_id, chat_id)[0]
        video_id = video[0]
    else:
        video = BotDB.search_sen_video(video_id, chat_id)
    sen = BotDB.search_sen(sen_id,chat_id);
    """
    msg = f'<b>{sign[1]}</b> (<i>{sign[2]}</i>)'
    if sign[2]:
        msg += f', 1 вариант'
    msg += f'\n{sign[3]}'
    """
    #videonote = open('VideoNoteTest.mp4', 'rb')
    #bot.send_video(chat_id, sign[3])
    
    markup,ver_num = form_sen_keyboard(chat_id,sen_id,video_id)
    msg = form_sen_text(sen,ver_num)
    #bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup=markup)
    bot.send_video(chat_id, video[2], caption = msg, parse_mode = 'html', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_sign",c.data))
def process_callback_show_sign(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sign_id = int(re.split("_", callback_query.data)[2])
    video_id = int(re.split("_", callback_query.data)[3])
    if video_id == 0:
        video = BotDB.search_sign_videos(sign_id, chat_id)[0]
        video_id = video[0]
    else:
        video = BotDB.search_sign_video(video_id, chat_id)
    sign = BotDB.search_sign(sign_id,chat_id);
    """
    msg = f'<b>{sign[1]}</b> (<i>{sign[2]}</i>)'
    if sign[2]:
        msg += f', 1 вариант'
    msg += f'\n{sign[3]}'
    """
    #videonote = open('VideoNoteTest.mp4', 'rb')
    #bot.send_video(chat_id, sign[3])
    
    markup,ver_num = form_sign_keyboard(chat_id,sign_id,video_id)
    msg = form_sign_text(sign,ver_num)
    #bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup=markup)
    bot.send_video(chat_id, video[2], caption = msg, parse_mode = 'html', reply_markup=markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_ver_sign_",c.data))
def process_callback_show_ver_sign(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    video_id = int(re.split("_", callback_query.data)[3])
    sign_id = int(re.split("_", callback_query.data)[4])

    sign = BotDB.search_sign(sign_id, chat_id)
    sign_video = BotDB.search_sign_video(video_id, chat_id)

    markup, ver_num = form_sign_keyboard(chat_id,sign_id,video_id)
    msg = form_sign_text(sign,ver_num)
    bot.edit_message_media(chat_id = chat_id, message_id = callback_query.message.message_id, media = types.InputMediaVideo(sign_video[2]))
    bot.edit_message_caption(caption = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_ver_sen_",c.data))
def process_callback_show_ver_sen(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    video_id = int(re.split("_", callback_query.data)[3])
    sen_id = int(re.split("_", callback_query.data)[4])

    sen = BotDB.search_sen(sen_id, chat_id)
    sen_video = BotDB.search_sen_video(video_id, chat_id)

    markup, ver_num = form_sen_keyboard(chat_id,sen_id,video_id)
    msg = form_sen_text(sen,ver_num)
    bot.edit_message_media(chat_id = chat_id, message_id = callback_query.message.message_id, media = types.InputMediaVideo(sen_video[2]))
    bot.edit_message_caption(caption = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/signFoldCh",c.data))
def process_callback_change_sign_folder(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    video_id = int(re.findall("\d+", callback_query.data)[0])
    if re.split("_", callback_query.data)[1] == 'fav':
        if re.split("_", callback_query.data)[2].startswith('t'):
            BotDB.make_sign_video_fav(chat_id,video_id)
        else:
            BotDB.make_sign_video_nfav(chat_id,video_id)
    else:
        if re.split("_", callback_query.data)[2].startswith('t'):
            BotDB.make_sign_video_learn(chat_id,video_id)
        else:
            BotDB.make_sign_video_nlearn(chat_id,video_id)

    markup, ver_num = form_sign_keyboard(chat_id,0,video_id)
    bot.edit_message_reply_markup(chat_id = chat_id, message_id = callback_query.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda c: re.findall("/ch_video_priv",c.data))
def process_callback_change_sign_folder(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    video_id = int(re.findall("\d+", callback_query.data)[0])
    if re.split("_", callback_query.data)[3] == 'sign':
        if re.split("_", callback_query.data)[4].startswith('t'):
            BotDB.make_sign_video_public(video_id)
        else:
            BotDB.make_sign_video_private(video_id)
        markup, ver_num = form_sign_keyboard(chat_id,0,video_id)
    else:
        if re.split("_", callback_query.data)[4].startswith('t'):
            BotDB.make_sen_video_public(video_id)
        else:
            BotDB.make_sen_video_private(video_id)
        markup, ver_num = form_sen_keyboard(chat_id,0,video_id)
    bot.edit_message_reply_markup(chat_id = chat_id, message_id = callback_query.message.message_id, reply_markup=markup)

@bot.message_handler(commands=['print_dict'])
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

@bot.message_handler(commands=['show_sign'])
def show_sign_handler(message):
    chat_id = message.chat.id
    sign_id = int(re.findall("\d+", message.text)[0])
    sign = BotDB.search_sign(sign_id,chat_id);
    msg = f'<b>{sign[5]}</b> (<i>{sign[6]}</i>)\n{sign[7]}'
    #videonote = open('VideoNoteTest.mp4', 'rb')
    bot.send_video(message.chat.id, sign[1], caption = msg, parse_mode = 'html')
   # bot.send_message(chat_id, msg, parse_mode = 'html')

@bot.message_handler(commands=['send_all'])
def send_all_handler(message):
    if message.from_user.id == ADMIN_id:
        text = re.split("send_all", message.text)[1]
        users = BotDB.get_users_by_name('')
        for user in users:
            msg = f'Привет, <b>{user[3]}'
            msg += f' {user[4]}!</b>' if not user[4] is None else '!</b>'
            msg += text
            bot.send_message(user[1], msg, parse_mode = 'html')
        
@bot.message_handler(commands=['show_fav'])
def show_fav_handler(message):
    chat_id = message.chat.id

    signs = BotDB.search_sign_videos_fav(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)

    msg, markup = form_list_msg_key(signs,1,'',obj_ref = '/show_sign',pg_ref = '/show_fav_pg',video_flag = 1)
    msg = '<b>'+user[9]+'</b>\n'+msg

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_fav_pg",c.data))
def process_callback_search_other_pg_fav(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    signs = BotDB.search_sign_videos_fav(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)
  
    msg, markup = form_list_msg_key(signs,pg_num,'',obj_ref = '/show_sign',pg_ref = '/show_fav_pg',video_flag = 1)
    msg = '<b>'+user[9]+'</b>\n'+msg

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.message_handler(commands=['show_learn'])
def show_learn_handler(message):
    chat_id = message.chat.id

    signs = BotDB.search_sign_videos_learn(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)

    msg, markup = form_list_msg_key(signs,1,'',obj_ref = '/show_sign',pg_ref = '/show_learn_pg',video_flag = 1)
    msg = '<b>'+user[10]+'</b>\n'+msg

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_learn_pg",c.data))
def process_callback_search_other_pg_learn(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    signs = BotDB.search_sign_videos_learn(chat_id);
    user = BotDB.get_user_by_user_id(chat_id)
 
    msg, markup = form_list_msg_key(signs,pg_num,'',obj_ref = '/show_sign',pg_ref = '/show_learn_pg',video_flag = 1)
    msg = '<b>'+user[10]+'</b>\n'+msg

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.message_handler(commands=['add_cat'])
def add_cat_ask_name(message):
    global isRunning
    chat_id = message.chat.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        isRunning[chat_id] = True
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
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Создана категория "' + text + '"', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(commands=['show_cats_sign'])
def show_sign_cats_handler(message):
    chat_id = message.chat.id

    cats = BotDB.search_all_cats_for_signs(chat_id);

    msg, markup = form_list_msg_key(cats,1,'',obj_ref = '/show_cat_signs_f_1',pg_ref = '/show_cats_sign_pg')

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cats_sign_pg",c.data))
def process_callback_show_cats_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    cats = BotDB.search_all_cats_for_signs(chat_id);

    msg, markup = form_list_msg_key(cats,pg_num,'',obj_ref = '/show_cat_signs_f_1',pg_ref = '/show_cats_sign_pg')

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)
    
@bot.callback_query_handler(func=lambda c: re.findall("/show_cat_signs_",c.data))
def process_callback_show_cat_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.split("_", callback_query.data)[4])
    cat_id = int(re.split("_", callback_query.data)[5])

    signs = BotDB.search_signs_in_cat(cat_id,chat_id);
    category = BotDB.get_cat_by_cat_id(cat_id)

    msg, markup = form_list_msg_key(signs,pg_num,cat_id,obj_ref = '/show_sign',pg_ref = '/show_cat_signs_pg')
    msg = '<b>'+category[1]+'</b>\n'+msg

    if re.split("_", callback_query.data)[3] == 'f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.message_handler(commands=['show_cats_sen'])
def show_sign_cats_handler(message):
    chat_id = message.chat.id

    cats = BotDB.search_all_cats_for_sens(chat_id);

    msg, markup = form_list_msg_key(cats,1,'',obj_ref = '/show_cat_sens_f_1',pg_ref = '/show_cats_sen_pg')

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cats_sen_pg",c.data))
def process_callback_show_cats_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    cats = BotDB.search_all_cats_for_sens(chat_id);

    msg, markup = form_list_msg_key(cats,pg_num,'',obj_ref = '/show_cat_sens_f_1',pg_ref = '/show_cats_sen_pg')

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cat_sens_",c.data))
def process_callback_show_cat_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.split("_", callback_query.data)[4])
    cat_id = int(re.split("_", callback_query.data)[5])

    signs = BotDB.search_sens_in_cat(cat_id,chat_id);
    category = BotDB.get_cat_by_cat_id(cat_id)

    msg, markup = form_list_msg_key(signs,pg_num,cat_id,obj_ref = '/show_sen',pg_ref = '/show_cat_sens_pg')
    msg = '<b>'+category[1]+'</b>\n'+msg

    if re.split("_", callback_query.data)[3] == 'f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

    """
@bot.callback_query_handler(func=lambda c: re.findall("/show_cat_",c.data))
def process_callback_show_cat_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.split("_", callback_query.data)[3])
    cat_id = int(re.split("_", callback_query.data)[4])

    signs = BotDB.search_signs_in_cat(cat_id,chat_id);
    category = BotDB.get_cat_by_cat_id(cat_id)

    msg, markup = form_list_msg_key(signs,pg_num,cat_id,obj_ref = '/show_sign',pg_ref = '/show_cat_pg')
    msg = '<b>'+category[1]+'</b>\n'+msg

    if re.split("_", callback_query.data)[2] == 'f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)
    """


@bot.callback_query_handler(func=lambda c: re.findall("/change_sign_cat_",c.data))
def process_callback_change_sign_cat(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    pg_num = int(re.split("_", callback_query.data)[4])
    sign_id = int(re.split("_", callback_query.data)[5])

    cats = BotDB.search_all_cats();

    msg, markup = form_list_msg_key(cats,pg_num,'',obj_ref = '/ch_sign_cat_'+str(sign_id),pg_ref = '/change_sign_cat_pg')

    if re.split("_", callback_query.data)[3]=='f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sign_cat_",c.data))
def process_callback_ch_sign_cat(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    category_id = int(re.split("_", callback_query.data)[4])
    sign_id = int(re.split("_", callback_query.data)[3])

    if BotDB.check_sign_in_cat(sign_id,category_id):
        BotDB.del_sign_cat(sign_id,category_id)
        msg = 'Жест удалён из категории'
    else:
        BotDB.add_sign_cat(sign_id, category_id)
        msg = 'Жест добавлен в категорию'
    bot.send_message(chat_id, msg, parse_mode = 'html')

@bot.callback_query_handler(func=lambda c: re.findall("/change_sen_cat_",c.data))
def process_callback_change_sign_cat(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    pg_num = int(re.split("_", callback_query.data)[4])
    sen_id = int(re.split("_", callback_query.data)[5])

    cats = BotDB.search_all_cats();

    msg, markup = form_list_msg_key(cats,pg_num,'',obj_ref = '/ch_sen_cat_'+str(sen_id),pg_ref = '/change_sen_cat_pg')

    if re.split("_", callback_query.data)[3]=='f':
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)
    else:
        bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/ch_sen_cat_",c.data))
def process_callback_ch_sign_cat(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    category_id = int(re.split("_", callback_query.data)[4])
    sen_id = int(re.split("_", callback_query.data)[3])

    if BotDB.check_sen_in_cat(sen_id,category_id):
        BotDB.del_sen_cat(sen_id,category_id)
        msg = 'Предложение удалено из категории'
    else:
        BotDB.add_sen_cat(sen_id, category_id)
        msg = 'Предложение добавлено в категорию'
    bot.send_message(chat_id, msg, parse_mode = 'html')

@bot.callback_query_handler(func=lambda c: re.findall("/add_sim_sign_",c.data))
def process_callback_add_sim_sign(callback_query: types.CallbackQuery):
    global sim_video_id
    global sim_video2_id
    global isRunning
    #bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    video_id = int(re.findall("\d+", callback_query.data)[0])
    if chat_id not in sim_video_id or sim_video_id[chat_id] == 0:
        sim_video_id[chat_id] = video_id
        bot.answer_callback_query(
            callback_query.id,
            text='Теперь нажмите такую же кнопку на втором (похожем) жесте', show_alert=False)
    elif video_id == sim_video_id[chat_id]:
        bot.answer_callback_query(
            callback_query.id,
            text='Вы уже выбрали этот жест. Теперь выберите второй', show_alert=False)
    else:
        sim_video2_id[chat_id] = video_id
        if BotDB.check_sim_sign_videos(sim_video_id[chat_id],sim_video2_id[chat_id]):
            BotDB.del_sim_signs(sim_video_id[chat_id],sim_video2_id[chat_id])
            bot.answer_callback_query(
                callback_query.id,
                text='Связь между выбранными жестами удалена', show_alert=False)
            del sim_video_id[chat_id]
            del sim_video2_id[chat_id]
        else:
            bot.answer_callback_query(callback_query.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
            markup.add(types.KeyboardButton('губам'),types.KeyboardButton('скорости движения'))
            markup.add(types.KeyboardButton('траектории'),types.KeyboardButton('количеству повторов'))
            markup.add(types.KeyboardButton('месту исполнения'),types.KeyboardButton('конфигурации'))
            markup.add(types.KeyboardButton('антонимы'),types.KeyboardButton('не знаю'))
            markup.add(types.KeyboardButton('один жест - часть другого'))
            msg = bot.send_message(chat_id, 'Выбранные жесты отличаются по ...?', reply_markup = markup)
            isRunning[chat_id] = True
            bot.register_next_step_handler(msg, add_sim_sign_after_ask)

def add_sim_sign_after_ask(message):
    global sim_video_id
    global sim_video2_id
    global isRunning
    chat_id = message.chat.id
    text = message.text
    if not text:
        msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_sim_sign_after_ask) #askSource
        return
    BotDB.add_sim_signs(sim_video_id[chat_id], sim_video2_id[chat_id], text)
    del sim_video_id[chat_id]
    del sim_video2_id[chat_id]
    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Связь между жестами сохранена', reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda c: re.findall("/add_comp_",c.data))
def process_callback_add_sim_sign(callback_query: types.CallbackQuery):
    global comp_video_id
    global comp_sen_video_id
    #bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    video_id = int(re.findall("\d+", callback_query.data)[0])
    who = re.split('_', callback_query.data)[2]
    if who == 'sign':
        comp_video_id[chat_id] = video_id
    elif who == 'sen':
        comp_sen_video_id[chat_id] = video_id
    if (chat_id in comp_video_id and comp_video_id[chat_id] != 0) and (chat_id not in comp_sen_video_id or comp_sen_video_id[chat_id] == 0):
        bot.answer_callback_query(
            callback_query.id,
            text='Теперь нажмите кнопку "Доб/Уд. Жесты" на предложении', show_alert=False)
    elif (chat_id not in comp_video_id or comp_video_id[chat_id] == 0) and (chat_id in comp_sen_video_id and comp_sen_video_id[chat_id] != 0):
        bot.answer_callback_query(
            callback_query.id,
            text='Теперь нажмите кнопку "Указ.предлож." на жесте', show_alert=False)
    elif (chat_id in comp_video_id and comp_video_id[chat_id] != 0) and (chat_id in comp_sen_video_id or comp_sen_video_id[chat_id] != 0):
        if BotDB.check_comp_sign_video(comp_video_id[chat_id],comp_sen_video_id[chat_id]):
            BotDB.del_comp_sign(comp_video_id[chat_id],comp_sen_video_id[chat_id])
            bot.answer_callback_query(
                callback_query.id,
                text='Связь между предложением и жестом удалена', show_alert=False)
        else:
            bot.answer_callback_query(callback_query.id)
            BotDB.add_comp_sign(comp_video_id[chat_id], comp_sen_video_id[chat_id])
            bot.send_message(chat_id, 'Связь между предложением и жестом сохранена', reply_markup=types.ReplyKeyboardRemove())
        del comp_video_id[chat_id]
        del comp_sen_video_id[chat_id]

@bot.callback_query_handler(func=lambda c: re.findall("/add_sign_video",c.data))
def process_callback_add_sign_video(callback_query: types.CallbackQuery):
    global isRunning
    global sign_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sign_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        msg = bot.send_message(chat_id, 'Отправьте видео со своим вариантом выбранного жеста')
        isRunning[chat_id] = True
        bot.register_next_step_handler(msg, add_sign_video_for_sign)
        
def add_sign_video_for_sign(message):
    global sign_id
    global isRunning
    chat_id = message.chat.id

    file_name, file_info = get_video_from_msg(message)
    if file_info == None:
        msg = bot.send_message(chat_id, 'Видео не обнаружено, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_sign_video_for_sign) #askSource
        return

    with open(file_name, "wb") as f:
        file_content = bot.download_file(file_info.file_path)
        f.write(file_content)
        #if chat_id not in files:
        #    files[chat_id] = []
        #files[chat_id].append(file_content)
    user = BotDB.get_user_by_user_id(chat_id)
    BotDB.add_sign_video(chat_id, user[5], sign_id[chat_id], file_content, user[8])

    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Ваш вариант жеста добавлен')

@bot.callback_query_handler(func=lambda c: re.findall("/add_sen_video",c.data))
def process_callback_add_sen_video(callback_query: types.CallbackQuery):
    global isRunning
    global sen_id
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    if chat_id not in isRunning or isRunning[chat_id] == False:
        sen_id[chat_id] = int(re.findall("\d+", callback_query.data)[0])
        msg = bot.send_message(chat_id, 'Отправьте видео со своим вариантом выбранного предложения')
        isRunning[chat_id] = True
        bot.register_next_step_handler(msg, add_sen_video_for_sen)
        
def add_sen_video_for_sen(message):
    global sen_id
    global isRunning
    chat_id = message.chat.id

    file_name, file_info = get_video_from_msg(message)
    if file_info == None:
        msg = bot.send_message(chat_id, 'Видео не обнаружено, отправьте ещё раз')
        bot.register_next_step_handler(msg, add_sen_video_for_sen) #askSource
        return

    with open(file_name, "wb") as f:
        file_content = bot.download_file(file_info.file_path)
        f.write(file_content)
        #if chat_id not in files:
        #    files[chat_id] = []
        #files[chat_id].append(file_content)
    user = BotDB.get_user_by_user_id(chat_id)
    BotDB.add_sen_video(chat_id, user[5], sen_id[chat_id], file_content, user[8])

    isRunning[chat_id] = False
    bot.send_message(chat_id, 'Ваш вариант предложения добавлен')

bot.polling(none_stop=True)