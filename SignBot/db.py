import psycopg2

#host = "127.0.0.1"
host = "178.250.158.248"
port = 34700
user = "postgres"
password = "password"
db_name = "RSLbot"

conn = psycopg2.connect(
                host = host,
                port = port,
                user = user,
                password = password,
                database = db_name)
cursor = conn.cursor()
print("Database opened successfully")

import sqlite3

# Переопределение функции преобразования к нижнему регистру
def sqlite_lower(value_):
    return value_.lower()
  
# Переопределение функции преобразования к верхнему геристру
def sqlite_upper(value_):
     return value_.upper()

# Переопределение правила сравнения строк
def ignore_case_collation(value1_, value2_):
    if value1_.lower() == value2_.lower():
        return 0
    elif value1_.lower() < value2_.lower():
        return -1
    else:
        return 1 


class BotDB:
    
    def __init__(self, db_file):
        """Инициализация соединения с БД"""
        """
        try:
            connection = psycopg2.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT version();"
                )
                print(cursor.fetchone())
        except Exception as _ex:
            print("Error while working with PostgreSQL", _ex)
        finally:
            if connection:
                connection.close()
                print("PostgreSQL connection closed")
        """

        """
        conn = sqlite3.connect(db_file, check_same_thread=False, timeout = 60)
       
        conn.create_collation("NOCASE", ignore_case_collation)
        conn.create_function("LOWER", 1, sqlite_lower)
        conn.create_function("UPPER", 1, sqlite_upper)

        cursor = conn.cursor()
        """

    def user_exists(self, user_id):
        """Проверка, есть ли пользователь в БД"""
        #cursor.execute("SELECT user_id FROM users WHERE user_id = %s",(user_id,))
        #return bool(len(cursor.fetchall()))
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s",(user_id,))
        return bool(len(cursor.fetchall()))
        """
        if cursor:
            return bool(len(cursor.fetchall()))
        else:
            return None
        """

    def get_user_by_user_id(self, user_id):
        """Получение пользователя из БД"""
        #cursor.execute("SELECT * FROM users WHERE user_id = %s",(user_id,))
        #return cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE user_id = %s",(user_id,))
        return cursor.fetchone()

    def get_users_by_name(self, name):
        """Получение пользователя из БД"""
        #cursor.execute("SELECT id, user_id, username, first_name, last_name FROM users WHERE username LIKE %s ",(name+"%",))
        #return cursor.fetchall()
        cursor.execute("SELECT id, user_id, username, first_name, last_name FROM users WHERE username LIKE %s ",(name+"%",))
        return cursor.fetchall()

    def add_user(self, user_id, username, fname, lname, dialect, privacy):
        """Добавление пользователя в БД"""
        #cursor.execute("INSERT INTO users (user_id, username, first_name, last_name, dialect, privacy) VALUES (%s, %s, %s, %s, %s, %s)",(user_id, username, fname, lname, dialect, privacy,))
        #return conn.commit()
        cursor.execute("INSERT INTO users (user_id, username, first_name, last_name, dialect, privacy) VALUES (%s, %s, %s, %s, %s, %s)",(user_id, username, fname, lname, dialect, privacy,))
        return conn.commit()

    def upd_user_dial_priv(self, user_id, dialect, privacy):
        """"""
        #cursor.execute("UPDATE users SET dialect = %s, privacy = %s WHERE user_id = %s",(dialect,privacy,user_id,))
        #return conn.commit()
        cursor.execute("UPDATE users SET dialect = %s, privacy = %s WHERE user_id = %s",(dialect,privacy,user_id,))
        return conn.commit()

    def upd_user_fav(self, user_id, fav_name):
        """"""
        #cursor.execute("UPDATE users SET fav_name = %s WHERE user_id = %s",(fav_name,user_id,))
        #return conn.commit()
        cursor.execute("UPDATE users SET fav_name = %s WHERE user_id = %s",(fav_name,user_id,))
        return conn.commit()

    def upd_user_learn(self, user_id, learn_name):
        """"""
        #cursor.execute("UPDATE users SET learn_name = %s WHERE user_id = %s",(learn_name,user_id,))
        #return conn.commit()
        cursor.execute("UPDATE users SET learn_name = %s WHERE user_id = %s",(learn_name,user_id,))
        return conn.commit()

    def upd_user_admin(self, user_id, admin):
        """"""
        #cursor.execute("UPDATE users SET admin = %s WHERE user_id = %s",(admin,user_id,))
        #return conn.commit()
        cursor.execute("UPDATE users SET admin = %s WHERE user_id = %s",(admin,user_id,))
        return conn.commit()

    def add_dialect(self, name):
        """Добавление диалекта в БД"""
        #cursor.execute("INSERT INTO dialects (name) VALUES (%s)",(name,))
        #conn.commit()
        #return cursor.fetchone()[0]
        cursor.execute("INSERT INTO dialects (name) VALUES (%s) RETURNING id",(name,))
        conn.commit()
        return cursor.fetchone()[0]

    def get_dialects(self):
        """"""
        #cursor.execute("SELECT * FROM dialects ORDER BY id")
        #return cursor.fetchall()
        cursor.execute("SELECT * FROM dialects ORDER BY id")
        return cursor.fetchall()

    def search_dialect(self, name):
        """П"""
        #cursor.execute("SELECT * FROM dialects WHERE name = %s", (name,))
        #return cursor.fetchone()
        cursor.execute("SELECT * FROM dialects WHERE name = %s", (name,))
        return cursor.fetchone()

    def add_sen(self, user_id, dialect, name, privacy, description):
        """Добавление жеста в БД"""
        cursor.execute("INSERT INTO sentences (author_id, dialect, name, privacy,description) VALUES (%s, %s, %s, %s, %s) RETURNING id",(user_id, dialect, name, privacy, description,))
        conn.commit()
        return cursor.fetchone()[0]

    def ch_sen_name(self, sen_id, name):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sentences SET name = %s WHERE id = %s",(name,sen_id,))
        return conn.commit()

    def ch_sen_desc(self, sen_id, desc):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sentences SET description = %s WHERE id = %s",(desc,sen_id,))
        return conn.commit()

    def add_sen_video(self, user_id, dialect, sen_id, video, privacy):
        """Добавление жеста в БД"""
        cursor.execute("INSERT INTO sentence_videos (author_id, dialect, sentence_id, video_file, privacy) VALUES (%s, %s, %s, %s, %s) RETURNING id",(user_id, dialect, sen_id, video, privacy,))
        conn.commit()
        return cursor.fetchone()[0]

    def del_sen_video(self, video_id):
        """Удаление жеста из БД"""
        cursor.execute("SELECT sentence_id FROM sentence_videos WHERE id = %s",(video_id,))
        sen = cursor.fetchone()
        cursor.execute("DELETE FROM sentence_videos WHERE id = %s",(video_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM sentence_videos WHERE sentence_id = %s",(sen[0],))
        if not bool(len(cursor.fetchall())):
            cursor.execute("DELETE FROM sentences WHERE id = %s",(sen[0],))
            cursor.execute("DELETE FROM sentence_categories WHERE sentence_id = %s",(sen[0],))

        cursor.execute("DELETE FROM sen_signs WHERE sen_video_id = %s",(video_id,))
        conn.commit()

        return

    def search_sen_videos(self, sen_id, user_id):
        """Поиск видосов жеста в БД"""
        cursor.execute("SELECT * FROM sentence_videos WHERE sentence_id = %s AND (privacy = 0 OR author_id = %s ) ORDER BY id",(sen_id, user_id,))
        return cursor.fetchall()

    def search_sen_video(self, video_id, user_id):
        """Поиск видео жеста в БД"""
        cursor.execute("SELECT * FROM sentence_videos WHERE id = %s AND (privacy = 0 OR author_id = %s ) ORDER BY id",(video_id, user_id,))
        return cursor.fetchone()

    def search_sens(self, name, user_id):
        """Поиск жестов в БД"""
        #if (name[0] >= а and name[0] <= я):
        cursor.execute("SELECT id, name, description FROM sentences WHERE (privacy = 0 OR author_id = %s ) AND LOWER(name) LIKE %s ",(user_id, "%"+name.lower()+"%",))
        #cursor.execute("SELECT id, name, part FROM signs WHERE name LIKE %s ",(name+"%",))
        return cursor.fetchall()

    def search_sen(self, sen_id, user_id):
        """Получение жеста из БД"""
        cursor.execute("SELECT * FROM sentences WHERE id = %s AND (privacy = 0 OR author_id = %s )",(sen_id, user_id))
        return cursor.fetchone()

    def search_sen_by_video(self, video_id):
        """Получение жеста из БД"""
        cursor.execute("SELECT sentences.id, sentences.name, sentences.dialect, sentences.author_id, sentences.privacy, sentences.description FROM sentences,sentence_videos WHERE sentence_videos.id = %s AND sentence_id = sentences.id",(video_id,))
        return cursor.fetchone()

    def add_sign(self, user_id, dialect, name, part, desc, picture, privacy):
        """Добавление жеста в БД"""
        cursor.execute("INSERT INTO signs (author_id, dialect, name, part, description, picture, privacy) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",(user_id, dialect, name, part, desc, picture,privacy,))
        conn.commit()
        return cursor.fetchone()[0]

    def ch_sign_name(self, sign_id, name):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE signs SET name = %s WHERE id = %s",(name,sign_id,))
        return conn.commit()

    def ch_sign_part(self, sign_id, part):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE signs SET part = %s WHERE id = %s",(part,sign_id,))
        return conn.commit()

    def ch_sign_desc(self, sign_id, desc):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE signs SET description = %s WHERE id = %s",(desc,sign_id,))
        return conn.commit()

    def ch_sign_dialect(self, sign_id, dialect_id):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE signs SET dialect = %s WHERE id = %s",(dialect_id,sign_id,))
        return conn.commit()

    def add_sign_video(self, user_id, dialect, sign_id, video, privacy):
        """Добавление жеста в БД"""
        cursor.execute("INSERT INTO sign_videos (author_id, dialect, sign_id, video_file, privacy) VALUES (%s, %s, %s, %s, %s) RETURNING id",(user_id, dialect, sign_id, video, privacy,))
        conn.commit()
        return cursor.fetchone()[0]

    def del_sign_video(self, video_id):
        """Удаление жеста из БД"""
        cursor.execute("SELECT sign_id FROM sign_videos WHERE id = %s",(video_id,))
        sign = cursor.fetchone()
        cursor.execute("DELETE FROM sign_videos WHERE id = %s",(video_id,))
        conn.commit()
        
        cursor.execute("SELECT * FROM sign_videos WHERE sign_id = %s",(sign[0],))
        if not bool(len(cursor.fetchall())):
            cursor.execute("DELETE FROM signs WHERE id = %s",(sign[0],))
            cursor.execute("DELETE FROM sign_categories WHERE sign_id = %s",(sign[0],))

        cursor.execute("DELETE FROM sim_sign_videos WHERE video_id = %s OR video2_id = %s",(video_id,video_id,))

        cursor.execute("DELETE FROM fav_sign_videos WHERE video_id = %s",(video_id,))

        cursor.execute("DELETE FROM learn_sign_videos WHERE video_id = %s",(video_id,))

        cursor.execute("DELETE FROM sen_signs WHERE sign_video_id = %s",(video_id,))
        conn.commit()
        return

    def search_sign_videos(self, sign_id, user_id):
        """Поиск видосов жеста в БД"""
        cursor.execute("SELECT * FROM sign_videos WHERE sign_id = %s AND (privacy = 0 OR author_id = %s ) ORDER BY id",(sign_id, user_id,))
        return cursor.fetchall()

    def search_sign_video(self, video_id, user_id):
        """Поиск видео жеста в БД"""
        cursor.execute("SELECT * FROM sign_videos WHERE id = %s AND (privacy = 0 OR author_id = %s ) ORDER BY id",(video_id, user_id,))
        return cursor.fetchone()

    def search_signs(self, name, user_id):
        """Поиск жестов в БД"""
        #if (name[0] >= а and name[0] <= я):
        cursor.execute("SELECT * FROM signs WHERE (privacy = 0 OR author_id = %s ) AND LOWER(name) LIKE %s ",(user_id, "%"+name.lower()+"%",))
        #cursor.execute("SELECT id, name, part FROM signs WHERE name LIKE %s ",(name+"%",))
        return cursor.fetchall()

    def search_sign(self, sign_id, user_id):
        """Получение жеста из БД"""
        cursor.execute("SELECT * FROM signs WHERE id = %s AND (privacy = 0 OR author_id = %s )",(sign_id, user_id))
        return cursor.fetchone()

    def search_sign_by_video(self, video_id):
        """Получение жеста из БД"""
        cursor.execute("SELECT signs.id, signs.name, signs.part, signs.description, signs.author_id, signs.privacy FROM signs,sign_videos WHERE sign_videos.id = %s AND sign_id = signs.id",(video_id,))
        return cursor.fetchone()

    def search_sign_by_name_auth(self, name, part, author_id):
        """Получение жеста из БД"""
        cursor.execute("SELECT * FROM signs WHERE name = %s AND part = %s AND author_id = %s",(name, part, author_id,))
        return cursor.fetchone()

    def make_sign_video_fav(self, user_id, video_id):
        """Добавление жеста в избранное"""
        cursor.execute("INSERT INTO fav_sign_videos (user_id, video_id) VALUES (%s, %s)",(user_id, video_id, ))
        return conn.commit()

    def search_sign_video_fav(self, user_id, video_id):
        """Проверка, добавлен ли жест в избранное"""
        cursor.execute("SELECT * FROM fav_sign_videos WHERE user_id = %s AND video_id = %s",(user_id,video_id,))
        return bool(len(cursor.fetchall()))

    def make_sign_video_nfav(self, user_id, video_id):
        """Удаление жеста из избранного"""
        cursor.execute("DELETE FROM fav_sign_videos WHERE user_id = %s AND video_id = %s",(user_id,video_id,))
        return conn.commit()

    def search_sign_videos_fav(self, user_id):
        """Поиск всех жестов в избранном"""
        cursor.execute("SELECT signs.id, name, part, video_id FROM signs, sign_videos, fav_sign_videos "\
            "WHERE (sign_videos.privacy = 0 OR sign_videos.author_id = %s) AND sign_videos.id = video_id AND sign_id = signs.id AND user_id = %s",(user_id,user_id,))
        return cursor.fetchall()

    def make_sign_video_learn(self, user_id, video_id):
        """Добавление жеста в изучаемые"""
        cursor.execute("INSERT INTO learn_sign_videos (user_id, video_id) VALUES (%s, %s)",(user_id, video_id, ))
        return conn.commit()

    def search_sign_video_learn(self, user_id, video_id):
        """Проверка, добавлен ли жест в изучаемое"""
        cursor.execute("SELECT * FROM learn_sign_videos WHERE user_id = %s AND video_id = %s",(user_id,video_id,))
        return bool(len(cursor.fetchall()))

    def make_sign_video_nlearn(self, user_id, video_id):
        """Удаление жеста из изуччаемого"""
        cursor.execute("DELETE FROM learn_sign_videos WHERE user_id = %s AND video_id = %s",(user_id,video_id,))
        return conn.commit()

    def search_sign_videos_learn(self, user_id):
        """Поиск всех жестов из изучаемого"""
        cursor.execute("SELECT signs.id, name, part, video_id FROM signs, sign_videos, learn_sign_videos "\
            "WHERE (sign_videos.privacy = 0 OR sign_videos.author_id = %s) AND sign_videos.id = video_id AND sign_id = signs.id AND user_id = %s",(user_id,user_id,))
        return cursor.fetchall()

    def make_sign_video_public(self, video_id):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sign_videos SET privacy = %s WHERE id = %s",(0,video_id,))
        return conn.commit()

    def make_sign_video_private(self, video_id):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sign_videos SET privacy = %s WHERE id = %s",(1,video_id,))
        return conn.commit()

    def make_sen_video_public(self, video_id):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sentence_videos SET privacy = %s WHERE id = %s",(0,video_id,))
        return conn.commit()

    def make_sen_video_private(self, video_id):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sentence_videos SET privacy = %s WHERE id = %s",(1,video_id,))
        return conn.commit()

    def add_comm_sign(self, text, user_id, video_id, privacy):
        """Добавление жеста в БД"""
        cursor.execute("INSERT INTO sign_comments (text, author_id, sign_video_id, privacy, date) VALUES (%s, %s, %s, %s, NOW()) RETURNING id",(text, user_id, video_id, privacy,))
        return conn.commit()

    def del_comm_sign(self, comm_id):
        """Удаление жеста из изуччаемого"""
        cursor.execute("DELETE FROM sign_comments WHERE id = %s",(comm_id,))
        return conn.commit()

    def del_comm_sen(self, comm_id):
        """Удаление жеста из изуччаемого"""
        cursor.execute("DELETE FROM sen_comments WHERE id = %s",(comm_id,))
        return conn.commit()

    def ch_comm_sign_text(self, comm_id, text):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sign_comments SET text = %s WHERE id = %s",(text,comm_id,))
        return conn.commit()
    
    def add_comm_sen(self, text, user_id, video_id, privacy):
        """Добавление жеста в БД"""
        cursor.execute("INSERT INTO sen_comments (text, author_id, sen_video_id, privacy, date) VALUES (%s, %s, %s, %s, NOW()) RETURNING id",(text, user_id, video_id, privacy,))
        return conn.commit()

    def ch_comm_sen_text(self, comm_id, text):
        """Добавление жеста в избранное"""
        cursor.execute("UPDATE sen_comments SET text = %s WHERE id = %s",(text,comm_id,))
        return conn.commit()
    
    def get_comms_by_sign_video_id(self, video_id, user_id):
        """Поиск всех категорий"""
        cursor.execute("SELECT com.id, com.text, users.user_id, users.first_name, date FROM sign_comments com, users WHERE com.sign_video_id = %s AND (com.privacy = 0 OR com.author_id = %s) AND users.user_id = com.author_id ORDER BY date",(video_id,user_id,))
        return cursor.fetchall()

    def get_comms_by_sen_video_id(self, video_id, user_id):
        """Поиск всех категорий"""
        cursor.execute("SELECT com.id, com.text, users.user_id, users.first_name, date FROM sen_comments com, users WHERE com.sen_video_id = %s AND (com.privacy = 0 OR com.author_id = %s) AND users.user_id = com.author_id ORDER BY date",(video_id,user_id,))
        return cursor.fetchall()

    def add_cat(self, name, description):
        """Добавление категории в БД"""
        cursor.execute("INSERT INTO categories (name, description) VALUES (%s, %s)",(name, description,))
        return conn.commit()

    def search_all_cats(self):
        """Поиск всех категорий"""
        cursor.execute("SELECT id, name, description FROM categories")
        return cursor.fetchall()

    def search_all_cats_for_signs(self,user_id):
        """Поиск всех категорий"""
        cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,sign_categories,sign_videos WHERE categories.id = category_id "\
            " AND sign_videos.sign_id = sign_categories.sign_id AND (sign_videos.privacy = 0 OR sign_videos.author_id = %s) GROUP BY categories.id",(user_id,))
        return cursor.fetchall()

    def search_all_cats_for_sens(self,user_id):
        """Поиск всех категорий"""
        cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,sentence_categories,sentence_videos WHERE categories.id = category_id "\
            " AND sentence_videos.sentence_id = sentence_categories.sentence_id AND (sentence_videos.privacy = 0 OR sentence_videos.author_id = %s) GROUP BY categories.id",(user_id,))
        return cursor.fetchall()

    def get_cat_by_cat_id(self,category_id):
        """Поиск категории по её id"""
        cursor.execute("SELECT id, name, description FROM categories WHERE id = %s",(category_id,))
        return cursor.fetchone()

    def get_cat_by_sign_id(self,sign_id):
        """Поиск категории по её id"""
        cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,signs,sign_categories"\
           " WHERE signs.id = %s AND categories.id = category_id AND sign_id = signs.id",(sign_id,))
        return cursor.fetchall()

    def get_cat_by_sen_id(self,sen_id):
        """Поиск категории по её id"""
        cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,sentences,sentence_categories"\
           " WHERE sentences.id = %s AND categories.id = category_id AND sentence_id = sentences.id",(sen_id,))
        return cursor.fetchall()

    def check_sign_in_cat(self,sign_id, category_id):
        """Поиск категории по её id"""
        cursor.execute("SELECT * FROM sign_categories WHERE sign_id = %s AND category_id = %s",(sign_id,category_id,))
        return bool(len(cursor.fetchall()))

    def check_sen_in_cat(self,sen_id, category_id):
        """Поиск категории по её id"""
        cursor.execute("SELECT * FROM sentence_categories WHERE sentence_id = %s AND category_id = %s",(sen_id,category_id,))
        return bool(len(cursor.fetchall()))

    def search_signs_in_cat(self,category_id, user_id):
        """Поиск всех жестов в категории"""
        cursor.execute("SELECT signs.id, signs.name, signs.part FROM categories, signs, sign_categories WHERE categories.id = %s AND "\
            "categories.id = category_id AND sign_id = signs.id AND (privacy = 0 OR author_id = %s)",(category_id,user_id,))
        return cursor.fetchall()

    def search_sens_in_cat(self,category_id, user_id):
        """Поиск всех жестов в категории"""
        cursor.execute("SELECT sentences.id, sentences.name FROM categories, sentences, sentence_categories WHERE categories.id = %s AND "\
            "categories.id = category_id AND sentence_id = sentences.id AND (privacy = 0 OR author_id = %s)",(category_id,user_id,))
        return cursor.fetchall()

    def add_sim_signs(self, video_id, video2_id, diff):
        """Добавление связи между похожими жестами"""
        cursor.execute("INSERT INTO sim_sign_videos (video_id, video2_id, diff) VALUES (%s, %s, %s)",(video_id, video2_id, diff,))
        return conn.commit()

    def add_comp_sign(self, comp_video_id, sen_video_id):
        """Добавление связи между похожими жестами"""
        cursor.execute("INSERT INTO sen_signs (sign_video_id, sen_video_id, date) VALUES (%s, %s, NOW())",(comp_video_id, sen_video_id,))
        return conn.commit()

    def del_sim_signs(self, video_id, video2_id):
        """Удаление связи между похожими жестами"""
        cursor.execute("DELETE FROM sim_sign_videos WHERE (video_id = %s AND video2_id = %s) OR (video2_id = %s AND video_id = %s)",(video_id, video2_id, video_id, video2_id,))
        return conn.commit()

    def del_comp_sign(self, comp_video_id, sen_video_id):
        """Проверка связи между похожими жестами"""
        cursor.execute("DELETE FROM sen_signs WHERE sign_video_id = %s AND sen_video_id = %s",(comp_video_id, sen_video_id,))
        return conn.commit()

    def check_sim_sign_videos(self, video_id, video2_id):
        """Проверка связи между похожими жестами"""
        cursor.execute("SELECT * FROM sim_sign_videos WHERE (video_id = %s AND video2_id = %s) OR (video2_id = %s AND video_id = %s)",(video_id, video2_id, video_id, video2_id,))
        return bool(len(cursor.fetchall()))

    def check_comp_sign_video(self, comp_video_id, sen_video_id):
        """Проверка связи между похожими жестами"""
        cursor.execute("SELECT * FROM sen_signs WHERE sign_video_id = %s AND sen_video_id = %s",(comp_video_id, sen_video_id,))
        return bool(len(cursor.fetchall()))

    def search_sim_sign_videos(self, video_id, user_id):
        """Поиск похожих жестов"""
        cursor.execute("SELECT signs.id, signs.name, signs.part, sign_videos.id, diff FROM signs,sign_videos, sim_sign_videos "\
           "WHERE video2_id = sign_videos.id AND sign_id = signs.id AND video_id = %s AND (sign_videos.privacy = 0 OR sign_videos.author_id = %s) "\
           "UNION SELECT signs.id, signs.name, signs.part, sign_videos.id, diff FROM signs,sign_videos, sim_sign_videos "\
           "WHERE video_id = sign_videos.id AND sign_id = signs.id AND video2_id = %s AND (sign_videos.privacy = 0 OR sign_videos.author_id = %s)",(video_id, user_id, video_id, user_id,))
        return cursor.fetchall()

    def search_comp_signs_by_sen(self, sen_video_id, user_id):
        """Поиск похожих жестов"""
        cursor.execute("SELECT signs.id, signs.name, signs.part, sign_videos.id FROM sign_videos,sen_signs,signs "\
           "WHERE sen_video_id = %s AND sen_signs.sign_video_id = sign_videos.id AND sign_videos.sign_id = signs.id AND (sign_videos.privacy = 0 OR sign_videos.author_id = %s) ORDER BY sen_signs.date",(sen_video_id, user_id,))
        return cursor.fetchall()

    def search_sens_by_comp_sign(self, sign_video_id, user_id):
        """Поиск похожих жестов"""
        cursor.execute("SELECT sentences.id, sentences.name, sentence_videos.id FROM sentence_videos,sen_signs,sentences "\
           "WHERE sen_signs.sign_video_id = %s AND sen_signs.sen_video_id = sentence_videos.id AND sentence_videos.sentence_id = sentences.id "\
           "AND (sentence_videos.privacy = 0 OR sentence_videos.author_id = %s)",(sign_video_id, user_id,))
        return cursor.fetchall()

    def add_sign_cat(self, sign_id, category_id):
        """Добавление категории для жеста"""
        #cursor.execute("DELETE FROM sign_categories WHERE sign_id = %s",(sign_id,))
        try:
            cursor.execute("INSERT INTO sign_categories (sign_id, category_id) VALUES (%s, %s)",(sign_id, category_id,))
            return conn.commit()
        except sqlite3.Error as er:
            print("SQLite error: %s" % (" ".join(er.args)))
            print("Exception class is: ", er.__class__)

    def del_sign_cat(self, sign_id, category_id):
        """Удаление категории для жеста"""
        cursor.execute("DELETE FROM sign_categories WHERE sign_id = %s AND category_id = %s",(sign_id,category_id,))
        return conn.commit()

    def add_sen_cat(self, sen_id, category_id):
        """Добавление категории для предложения"""
        #cursor.execute("DELETE FROM sign_categories WHERE sign_id = %s",(sign_id,))
        try:
            cursor.execute("INSERT INTO sentence_categories (sentence_id, category_id) VALUES (%s, %s)",(sen_id, category_id,))
            return conn.commit()
        except sqlite3.Error as er:
            print("SQLite error: %s" % (" ".join(er.args)))
            print("Exception class is: ", er.__class__)

    def del_sen_cat(self, sen_id, category_id):
        """Удаление категории для предложения"""
        cursor.execute("DELETE FROM sentence_categories WHERE sentence_id = %s AND category_id = %s",(sen_id,category_id,))
        return conn.commit()

    def close(self):
        """Закрытие соединения с БД"""
        conn.close()




