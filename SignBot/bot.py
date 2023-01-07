import telebot
from telebot import types
import re

from db import BotDB
BotDB = BotDB('RSLbot.db')

bot = telebot.TeleBot('5744274566:AAHRaYf-jV2o0ibwQWlL92Bh3jpLh3CTEcg')
ADMIN_id = 923048680

isRunning = 0
#isRunningSearch = 0
#isRunningAddCat = 0
sim_video_id = 0
sim_video2_id = 0
files = []

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
        ver_num = 1
    else:
        i = 1
        for v in videos:
            if video_id == v[0]:
                ver_num = i
            i += 1
    if len(videos) < 2:
        ver_num = 0
    markup = types.InlineKeyboardMarkup()
    markup.row_width = 2
    btns = []
    #more_videos = BotDB.search_sign_more_video(sign_id, chat_id)

    num = len(videos)
    if num>1:
        num_of_rows = (num-1)/8+1
        i=1
        for v in videos:
            btn = types.InlineKeyboardButton(str(i), callback_data = '/show_ver_sign_'+str(videos[i-1][0])+'_'+str(sign_id))
            btns.append(btn)
            if (num_of_rows > 1) and (i%((num+num%2)/num_of_rows) == 0):
                markup.row(*btns)
                btns = []
            i += 1
        markup.row(*btns)
        btns = []

    categories = BotDB.get_cat_by_sign_id(sign_id)
    if len(categories):
        for cat in categories:
            btn = types.InlineKeyboardButton(cat[1], callback_data = '/show_cat_f_1_'+str(cat[0]))
            btns.append(btn)
    if user[7]==1:
        btn = types.InlineKeyboardButton("Изм.категорию", callback_data = '/change_sign_cat_f_1_'+str(sign_id))
        btns.append(btn)
    if len(BotDB.search_sim_sign_videos(video_id,chat_id)):
        btn = types.InlineKeyboardButton("Похожие жесты", callback_data = '/show_sim_f_1_'+str(video_id))
        btns.append(btn)
    if user[7]==1:
        btn = types.InlineKeyboardButton("Доб/Уд.похожие", callback_data = '/add_sim_sign_'+str(video_id))
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
    if (isRunning==False) and (not message.text.startswith('/')):
        chat_id = message.chat.id
        text = message.text
        signs = BotDB.search_signs(text,chat_id);
        msg, markup = form_list_msg_key(signs,1,text,obj_ref = '/show_sign',pg_ref = '/search_pg')
        bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.message_handler(commands=["start"])
def start(message):
    print(message.text)
    if message.text == "/start":
        if(not BotDB.user_exists(message.from_user.id)):
            BotDB.add_user(message.from_user.id,message.from_user.username,message.from_user.first_name,message.from_user.last_name,1)
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}!")


@bot.message_handler(is_owner=True, commands=["ping"])
def cmd_ping_bot(message):
    message.reply("<b>👊 Up & Running!</b>\n\n")


@bot.message_handler(commands=['add_sign'])
def add_sign_handler(message):
    chat_id = message.chat.id
    text = message.text
    msg = bot.send_message(chat_id, 'Отправьте видео жеста')
        #bot.register_next_step_handler(msg, ask_sign_video) #askSource

@bot.message_handler(content_types=['video','animation','video_note'])
def ask_sign_video(message):
    global isRunning
    if not isRunning:
        
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
        global files
        with open(file_name, "wb") as f:
            file_content = bot.download_file(file_info.file_path)
            f.write(file_content)
            files.append(file_content)
        msg = bot.send_message(chat_id, 'Отправьте видео с другим вариантом жеста или напишите название жеста')
        bot.register_next_step_handler(msg, add_ask_sign_name)

def add_ask_sign_name(message):
    global sign_name
    chat_id = message.chat.id

    if message.video or message.animation or message.video_note:
        #bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
        ask_sign_video(message)
    else:
        sign_name = message.text
        if not sign_name:
            msg = bot.send_message(chat_id, 'Текст пустой, отправьте ещё раз')
            bot.register_next_step_handler(msg, add_ask_sign_name) #askSource
            return
        global isRunning
        isRunning = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
        markup.add(types.KeyboardButton('Существительное'),types.KeyboardButton('Глагол'))
        markup.add(types.KeyboardButton('Наречие'),types.KeyboardButton('Прилагательное'))
        msg = bot.send_message(chat_id, 'Выберите часть речи', reply_markup = markup)
        bot.register_next_step_handler(msg, add_ask_sign_part)

def add_ask_sign_part(message):
    global isRunning
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
    sign_id = BotDB.add_sign(chat_id,dialect,sign_name,text,"",None,privacy)
    #sign = BotDB.search_sign_by_name_auth(sign_name, text, chat_id)
    if len(files):
        for f in files:
            video_id = BotDB.add_sign_video(chat_id, dialect, sign_id, f, privacy)
    files = []
    isRunning = False
    bot.send_message(chat_id, 'Спасибо за вклад, жест "' + sign_name + '" добавлен)', reply_markup=types.ReplyKeyboardRemove())
    """
    ВЫЗЫВАТЬ ФУНКЦИЮ ДЛЯ ПОКАЗА ДОБАВЛЕННОГО ЖЕСТА ПО ПОСЛЕДНЕМУ video_id!!!!!!!!!!!!!!




    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    !!!!!!!!!!!!!!!
    """

@bot.message_handler(commands=['search_sign'])
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
 
    msg, markup = form_list_msg_key(signs,pg_num,text,obj_ref = '/show_sign',pg_ref = '/search_pg')

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
def process_callback_change_sign_cat(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id

    video_id = int(re.split("_", callback_query.data)[3])
    sign_id = int(re.split("_", callback_query.data)[4])

    sign = BotDB.search_sign(sign_id, chat_id)
    sign_video = BotDB.search_sign_video(video_id, chat_id)
    """
    msg = callback_query.message.caption
    sign_name = re.split(' ', msg)
    sign_part = re.findall('\(.*\)', msg)
    sign_descript = re.findall('\n.*', msg)
    msg = ''
    if len(sign_name):
        msg += f'<b>{sign_name[0]}</b>'
    if len(sign_part):
        msg += f' <i>{sign_part[0]}</i>'
    msg += f', {ver_num} вариант'
    if len(sign_descript):
        msg += f'{sign_descript[0]}'
    #msg = f'<b>{sign_name}</b> <i>{sign_part}</i>, {ver_num} вариант{sign_descript}'
    markup = callback_query.message.reply_markup
    """
    markup, ver_num = form_sign_keyboard(chat_id,sign_id,video_id)
    msg = form_sign_text(sign,ver_num)
    bot.edit_message_media(chat_id = chat_id, message_id = callback_query.message.message_id, media = types.InputMediaVideo(sign_video[2]))
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

@bot.message_handler(commands=['show_cats'])
def show_cats_handler(message):
    chat_id = message.chat.id

    cats = BotDB.search_all_cats();

    msg, markup = form_list_msg_key(cats,1,'',obj_ref = '/show_cat_f_1',pg_ref = '/show_cats_pg')

    bot.send_message(chat_id, msg, parse_mode = 'html', reply_markup = markup)

@bot.callback_query_handler(func=lambda c: re.findall("/show_cats_pg",c.data))
def process_callback_show_cats_other_pg(callback_query: types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    pg_num = int(re.findall("\d+", callback_query.data)[0])

    cats = BotDB.search_all_cats(chat_id);

    msg, markup = form_list_msg_key(cats,pg_num,'',obj_ref = '/show_cat_f_1',pg_ref = '/show_cats_pg')

    bot.edit_message_text(text = msg, chat_id = chat_id, message_id = callback_query.message.message_id, parse_mode = 'html', reply_markup = markup)

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
def process_callback_change_sign_cat(callback_query: types.CallbackQuery):
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

@bot.callback_query_handler(func=lambda c: re.findall("/add_sim_sign_",c.data))
def process_callback_add_sim_sign(callback_query: types.CallbackQuery):
    global sim_video_id
    global sim_video2_id
    global isRunning
    #bot.answer_callback_query(callback_query.id)
    chat_id = callback_query.from_user.id
    sign_id = int(re.findall("\d+", callback_query.data)[0])
    if sim_video_id == 0:
        sim_video_id = sign_id
        bot.answer_callback_query(
            callback_query.id,
            text='Теперь нажмите такую же кнопку на втором (похожем) жесте', show_alert=False)
    elif sign_id == sim_video_id:
        bot.answer_callback_query(
            callback_query.id,
            text='Вы уже выбрали этот жест. Теперь выберите второй', show_alert=False)
    else:
        sim_video2_id = sign_id
        if BotDB.check_sim_sign_videos(sim_video_id,sim_video2_id):
            BotDB.del_sim_signs(sim_video_id,sim_video2_id)
            bot.answer_callback_query(
                callback_query.id,
                text='Связь между выбранными жестами удалена', show_alert=False)
        else:
            bot.answer_callback_query(callback_query.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width = 2)
            markup.add(types.KeyboardButton('губам'),types.KeyboardButton('скорости движения'))
            markup.add(types.KeyboardButton('траектории'),types.KeyboardButton('количеству повторов'))
            markup.add(types.KeyboardButton('месту исполнения'),types.KeyboardButton('конфигурации'))
            markup.add(types.KeyboardButton('антонимы'),types.KeyboardButton('не знаю'))
            msg = bot.send_message(chat_id, 'Выбранные жесты отличаются по ...?', reply_markup = markup)
            isRunning = True
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
    BotDB.add_sim_signs(sim_video_id, sim_video2_id, text)
    sim_video_id = 0
    sim_video2_id = 0
    isRunning = False
    bot.send_message(chat_id, 'Связь между жестами сохранена', reply_markup=types.ReplyKeyboardRemove())

        

bot.polling(none_stop=True)