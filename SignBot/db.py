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
        self.conn = sqlite3.connect(db_file, check_same_thread=False, timeout = 60)
       
        self.conn.create_collation("NOCASE", ignore_case_collation)
        self.conn.create_function("LOWER", 1, sqlite_lower)
        self.conn.create_function("UPPER", 1, sqlite_upper)

        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        """Проверка, есть ли пользователь в БД"""
        result = self.cursor.execute("SELECT `user_id` FROM `users` WHERE `user_id` = ?",(user_id,))
        return bool(len(result.fetchall()))

    def get_user_by_user_id(self, user_id):
        """Получение пользователя из БД"""
        result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?",(user_id,))
        return result.fetchone()

    def get_users_by_name(self, name):
        """Получение пользователя из БД"""
        result = self.cursor.execute("SELECT id, user_id, username, first_name, last_name FROM users WHERE username LIKE ? ",(name+"%",))
        return result.fetchall()

    def add_user(self, user_id, username, fname, lname, dialect, privacy):
        """Добавление пользователя в БД"""
        self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `first_name`, `last_name`, `dialect`, `privacy`) VALUES (?, ?, ?, ?, ?, ?)",(user_id, username, fname, lname, dialect, privacy,))
        return self.conn.commit()

    def upd_user_dial_priv(self, user_id, dialect, privacy):
        """Добавление пользователя в БД"""
        self.cursor.execute("UPDATE users SET dialect = ?, privacy = ? WHERE user_id = ?",(dialect,privacy,user_id,))
        return self.conn.commit()

    def upd_user_fav(self, user_id, fav_name):
        """Добавление пользователя в БД"""
        self.cursor.execute("UPDATE users SET fav_name = ? WHERE user_id = ?",(fav_name,user_id,))
        return self.conn.commit()

    def upd_user_learn(self, user_id, learn_name):
        """Добавление пользователя в БД"""
        self.cursor.execute("UPDATE users SET learn_name = ? WHERE user_id = ?",(learn_name,user_id,))
        return self.conn.commit()

    def upd_user_admin(self, user_id, admin):
        """Добавление пользователя в БД"""
        self.cursor.execute("UPDATE users SET admin = ? WHERE user_id = ?",(admin,user_id,))
        return self.conn.commit()

    def add_dialect(self, name):
        """Добавление пользователя в БД"""
        self.cursor.execute("INSERT INTO dialects (name) VALUES (?)",(name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_dialects(self):
        """Поиск дополнительных вариантов жестов в БД"""
        result = self.cursor.execute("SELECT * FROM dialects ORDER BY id")
        return result.fetchall()

    def search_dialect(self, name):
        """Поиск дополнительных вариантов жестов в БД"""
        result = self.cursor.execute("SELECT * FROM dialects WHERE name = ?", (name,))
        return result.fetchone()

    def add_sen(self, user_id, dialect, name, privacy, description):
        """Добавление жеста в БД"""
        self.cursor.execute("INSERT INTO `sentences` (`author_id`, `dialect`, `name`, `privacy`,'description') VALUES (?, ?, ?, ?, ?)",(user_id, dialect, name, privacy, description,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_sen_video(self, user_id, dialect, sen_id, video, privacy):
        """Добавление жеста в БД"""
        self.cursor.execute("INSERT INTO sentence_videos (`author_id`, `dialect`, `sentence_id`, `video_file`, `privacy`) VALUES (?, ?, ?, ?, ?)",(user_id, dialect, sen_id, video, privacy,))
        self.conn.commit()
        return self.cursor.lastrowid

    def del_sen_video(self, video_id):
        """Удаление жеста из БД"""
        result = self.cursor.execute("SELECT sentence_id FROM sentence_videos WHERE id = ?",(video_id,))
        sen = result.fetchone()
        print(sen)
        self.cursor.execute("DELETE FROM sentence_videos WHERE id = ?",(video_id,))
        self.conn.commit()
        
        result2 = self.cursor.execute("SELECT * FROM sentence_videos WHERE sentence_id = ?",(sen[0],))
        if not bool(len(result2.fetchall())):
            self.cursor.execute("DELETE FROM sentences WHERE id = ?",(sen[0],))
            self.cursor.execute("DELETE FROM sentence_categories WHERE sentence_id = ?",(sen[0],))

        self.cursor.execute("DELETE FROM sen_signs WHERE sen_video_id = ?",(video_id,))
        self.conn.commit()

        return

    def search_sen_videos(self, sen_id, user_id):
        """Поиск видосов жеста в БД"""
        result = self.cursor.execute("SELECT * FROM sentence_videos WHERE sentence_id = ? AND (privacy = 0 OR author_id = ? ) ORDER BY id",(sen_id, user_id,))
        return result.fetchall()

    def search_sen_video(self, video_id, user_id):
        """Поиск видео жеста в БД"""
        result = self.cursor.execute("SELECT * FROM sentence_videos WHERE id = ? AND (privacy = 0 OR author_id = ? ) ORDER BY id",(video_id, user_id,))
        return result.fetchone()

    def search_sens(self, name, user_id):
        """Поиск жестов в БД"""
        #if (name[0] >= 'а' and name[0] <= 'я'):
        result = self.cursor.execute("SELECT id, name, description FROM sentences WHERE (privacy = 0 OR author_id = ? ) AND LOWER(name) LIKE ? ",(user_id, name.lower()+"%",))
        #result = self.cursor.execute("SELECT id, name, part FROM signs WHERE name LIKE ? ",(name+"%",))
        return result.fetchall()

    def search_sen(self, sen_id, user_id):
        """Получение жеста из БД"""
        result = self.cursor.execute("SELECT * FROM sentences WHERE id = ? AND (privacy = 0 OR author_id = ? )",(sen_id, user_id))
        return result.fetchone()

    def search_sen_by_video(self, video_id):
        """Получение жеста из БД"""
        result = self.cursor.execute("SELECT sentences.id, sentences.name FROM sentences,sentence_videos WHERE sentence_videos.id = ? AND sentence_id = sentences.id",(video_id,))
        return result.fetchone()

    def add_sign(self, user_id, dialect, name, part, desc, picture, privacy):
        """Добавление жеста в БД"""
        self.cursor.execute("INSERT INTO `signs` (`author_id`, `dialect`, `name`, `part`, `description`, `picture`, `privacy`) VALUES (?, ?, ?, ?, ?, ?, ?)",(user_id, dialect, name, part, desc, picture,privacy,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_sign_video(self, user_id, dialect, sign_id, video, privacy):
        """Добавление жеста в БД"""
        self.cursor.execute("INSERT INTO sign_videos (`author_id`, `dialect`, `sign_id`, `video_file`, `privacy`) VALUES (?, ?, ?, ?, ?)",(user_id, dialect, sign_id, video, privacy,))
        self.conn.commit()
        return self.cursor.lastrowid

    def del_sign_video(self, video_id):
        """Удаление жеста из БД"""
        result = self.cursor.execute("SELECT sign_id FROM sign_videos WHERE id = ?",(video_id,))
        sign = result.fetchone()
        print(sign)
        self.cursor.execute("DELETE FROM sign_videos WHERE id = ?",(video_id,))
        self.conn.commit()
        
        result2 = self.cursor.execute("SELECT * FROM sign_videos WHERE sign_id = ?",(sign[0],))
        if not bool(len(result2.fetchall())):
            self.cursor.execute("DELETE FROM signs WHERE id = ?",(sign[0],))
            self.cursor.execute("DELETE FROM sign_categories WHERE sign_id = ?",(sign[0],))

        self.cursor.execute("DELETE FROM sim_sign_videos WHERE video_id = ? OR video2_id = ?",(video_id,video_id,))

        self.cursor.execute("DELETE FROM fav_sign_videos WHERE video_id = ?",(video_id,))

        self.cursor.execute("DELETE FROM learn_sign_videos WHERE video_id = ?",(video_id,))

        self.cursor.execute("DELETE FROM sen_signs WHERE sign_video_id = ?",(video_id,))
        self.conn.commit()
        return

    def search_sign_videos(self, sign_id, user_id):
        """Поиск видосов жеста в БД"""
        result = self.cursor.execute("SELECT * FROM sign_videos WHERE sign_id = ? AND (privacy = 0 OR author_id = ? ) ORDER BY id",(sign_id, user_id,))
        return result.fetchall()

    def search_sign_video(self, video_id, user_id):
        """Поиск видео жеста в БД"""
        result = self.cursor.execute("SELECT * FROM sign_videos WHERE id = ? AND (privacy = 0 OR author_id = ? ) ORDER BY id",(video_id, user_id,))
        return result.fetchone()

    def search_signs(self, name, user_id):
        """Поиск жестов в БД"""
        #if (name[0] >= 'а' and name[0] <= 'я'):
        result = self.cursor.execute("SELECT id, name, part FROM signs WHERE (privacy = 0 OR author_id = ? ) AND LOWER(name) LIKE ? ",(user_id, name.lower()+"%",))
        #result = self.cursor.execute("SELECT id, name, part FROM signs WHERE name LIKE ? ",(name+"%",))
        return result.fetchall()

    def search_sign(self, sign_id, user_id):
        """Получение жеста из БД"""
        result = self.cursor.execute("SELECT * FROM signs WHERE id = ? AND (privacy = 0 OR author_id = ? )",(sign_id, user_id))
        return result.fetchone()

    def search_sign_by_video(self, video_id):
        """Получение жеста из БД"""
        result = self.cursor.execute("SELECT signs.id, signs.name, signs.part FROM signs,sign_videos WHERE sign_videos.id = ? AND sign_id = signs.id",(video_id,))
        return result.fetchone()

    def search_sign_by_name_auth(self, name, part, author_id):
        """Получение жеста из БД"""
        result = self.cursor.execute("SELECT * FROM signs WHERE name = ? AND part = ? AND author_id = ?",(name, part, author_id,))
        return result.fetchone()

    def make_sign_video_fav(self, user_id, video_id):
        """Добавление жеста в избранное"""
        self.cursor.execute("INSERT INTO fav_sign_videos (user_id, video_id) VALUES (?, ?)",(user_id, video_id, ))
        return self.conn.commit()

    def search_sign_video_fav(self, user_id, video_id):
        """Проверка, добавлен ли жест в избранное"""
        result = self.cursor.execute("SELECT * FROM fav_sign_videos WHERE user_id = ? AND video_id = ?",(user_id,video_id,))
        return bool(len(result.fetchall()))

    def make_sign_video_nfav(self, user_id, video_id):
        """Удаление жеста из избранного"""
        self.cursor.execute("DELETE FROM fav_sign_videos WHERE user_id = ? AND video_id = ?",(user_id,video_id,))
        return self.conn.commit()

    def search_sign_videos_fav(self, user_id):
        """Поиск всех жестов в избранном"""
        result = self.cursor.execute("SELECT signs.id, name, part, video_id FROM signs, sign_videos, fav_sign_videos "\
            "WHERE (sign_videos.privacy = 0 OR sign_videos.author_id = ?) AND sign_videos.id = video_id AND sign_id = signs.id AND user_id = ?",(user_id,user_id,))
        return result.fetchall()

    def make_sign_video_learn(self, user_id, video_id):
        """Добавление жеста в изучаемые"""
        self.cursor.execute("INSERT INTO learn_sign_videos (user_id, video_id) VALUES (?, ?)",(user_id, video_id, ))
        return self.conn.commit()

    def search_sign_video_learn(self, user_id, video_id):
        """Проверка, добавлен ли жест в изучаемое"""
        result = self.cursor.execute("SELECT * FROM learn_sign_videos WHERE user_id = ? AND video_id = ?",(user_id,video_id,))
        return bool(len(result.fetchall()))

    def make_sign_video_nlearn(self, user_id, video_id):
        """Удаление жеста из изуччаемого"""
        self.cursor.execute("DELETE FROM learn_sign_videos WHERE user_id = ? AND video_id = ?",(user_id,video_id,))
        return self.conn.commit()

    def search_sign_videos_learn(self, user_id):
        """Поиск всех жестов из изучаемого"""
        result = self.cursor.execute("SELECT signs.id, name, part, video_id FROM signs, sign_videos, learn_sign_videos "\
            "WHERE (sign_videos.privacy = 0 OR sign_videos.author_id = ?) AND sign_videos.id = video_id AND sign_id = signs.id AND user_id = ?",(user_id,user_id,))
        return result.fetchall()

    def add_cat(self, name, description):
        """Добавление категории в БД"""
        self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",(name, description,))
        return self.conn.commit()

    def search_all_cats(self):
        """Поиск всех категорий"""
        result = self.cursor.execute("SELECT id, name, description FROM categories")
        return result.fetchall()

    def search_all_cats_for_signs(self,user_id):
        """Поиск всех категорий"""
        result = self.cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,sign_categories,sign_videos WHERE categories.id = category_id "\
            " AND sign_videos.sign_id = sign_categories.sign_id AND (sign_videos.privacy = 0 OR sign_videos.author_id = ?) GROUP BY categories.id",(user_id,))
        return result.fetchall()

    def search_all_cats_for_sens(self,user_id):
        """Поиск всех категорий"""
        result = self.cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,sentence_categories,sentence_videos WHERE categories.id = category_id "\
            " AND sentence_videos.sentence_id = sentence_categories.sentence_id AND (sentence_videos.privacy = 0 OR sentence_videos.author_id = ?) GROUP BY categories.id",(user_id,))
        return result.fetchall()

    def get_cat_by_cat_id(self,category_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT id, name, description FROM categories WHERE id = ?",(category_id,))
        return result.fetchone()

    def get_cat_by_sign_id(self,sign_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,signs,sign_categories"\
           " WHERE signs.id = ? AND categories.id = category_id AND sign_id = signs.id",(sign_id,))
        return result.fetchall()

    def get_cat_by_sen_id(self,sen_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,sentences,sentence_categories"\
           " WHERE sentences.id = ? AND categories.id = category_id AND sentence_id = sentences.id",(sen_id,))
        return result.fetchall()

    def check_sign_in_cat(self,sign_id, category_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT * FROM sign_categories WHERE sign_id = ? AND category_id = ?",(sign_id,category_id,))
        return bool(len(result.fetchall()))

    def check_sen_in_cat(self,sen_id, category_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT * FROM sentence_categories WHERE sentence_id = ? AND category_id = ?",(sen_id,category_id,))
        return bool(len(result.fetchall()))

    def search_signs_in_cat(self,category_id, user_id):
        """Поиск всех жестов в категории"""
        result = self.cursor.execute("SELECT signs.id, signs.name, signs.part FROM categories, signs, sign_categories WHERE categories.id = ? AND "\
            "categories.id = category_id AND sign_id = signs.id AND (privacy = 0 OR author_id = ?)",(category_id,user_id,))
        return result.fetchall()

    def search_sens_in_cat(self,category_id, user_id):
        """Поиск всех жестов в категории"""
        result = self.cursor.execute("SELECT sentences.id, sentences.name FROM categories, sentences, sentence_categories WHERE categories.id = ? AND "\
            "categories.id = category_id AND sentence_id = sentences.id AND (privacy = 0 OR author_id = ?)",(category_id,user_id,))
        return result.fetchall()

    def add_sim_signs(self, video_id, video2_id, diff):
        """Добавление связи между похожими жестами"""
        self.cursor.execute("INSERT INTO sim_sign_videos (video_id, video2_id, diff) VALUES (?, ?, ?)",(video_id, video2_id, diff,))
        return self.conn.commit()

    def add_comp_sign(self, comp_video_id, sen_video_id):
        """Добавление связи между похожими жестами"""
        self.cursor.execute("INSERT INTO sen_signs (sign_video_id, sen_video_id) VALUES (?, ?)",(comp_video_id, sen_video_id,))
        return self.conn.commit()

    def del_sim_signs(self, video_id, video2_id):
        """Удаление связи между похожими жестами"""
        self.cursor.execute("DELETE FROM sim_sign_videos WHERE (video_id = ? AND video2_id = ?) OR (video2_id = ? AND video_id = ?)",(video_id, video2_id, video_id, video2_id,))
        return self.conn.commit()

    def del_comp_sign(self, comp_video_id, sen_video_id):
        """Проверка связи между похожими жестами"""
        self.cursor.execute("DELETE FROM sen_signs WHERE sign_video_id = ? AND sen_video_id = ?",(comp_video_id, sen_video_id,))
        return self.conn.commit()

    def check_sim_sign_videos(self, video_id, video2_id):
        """Проверка связи между похожими жестами"""
        result = self.cursor.execute("SELECT * FROM sim_sign_videos WHERE (video_id = ? AND video2_id = ?) OR (video2_id = ? AND video_id = ?)",(video_id, video2_id, video_id, video2_id,))
        return bool(len(result.fetchall()))

    def check_comp_sign_video(self, comp_video_id, sen_video_id):
        """Проверка связи между похожими жестами"""
        result = self.cursor.execute("SELECT * FROM sen_signs WHERE sign_video_id = ? AND sen_video_id = ?",(comp_video_id, sen_video_id,))
        return bool(len(result.fetchall()))

    def search_sim_sign_videos(self, video_id, user_id):
        """Поиск похожих жестов"""
        result = self.cursor.execute("SELECT signs.id, signs.name, signs.part, sign_videos.id, diff FROM signs,sign_videos, sim_sign_videos "\
           "WHERE video2_id = sign_videos.id AND sign_id = signs.id AND video_id = ? AND (sign_videos.privacy = 0 OR sign_videos.author_id = ?) "\
           "UNION SELECT signs.id, signs.name, signs.part, sign_videos.id, diff FROM signs,sign_videos, sim_sign_videos "\
           "WHERE video_id = sign_videos.id AND sign_id = signs.id AND video2_id = ? AND (sign_videos.privacy = 0 OR sign_videos.author_id = ?)",(video_id, user_id, video_id, user_id,))
        return result.fetchall()

    def search_comp_signs_by_sen(self, sen_video_id, user_id):
        """Поиск похожих жестов"""
        result = self.cursor.execute("SELECT signs.id, signs.name, signs.part, sign_videos.id FROM sign_videos,sen_signs,signs "\
           "WHERE sen_video_id = ? AND sen_signs.sign_video_id = sign_videos.id AND sign_videos.sign_id = signs.id AND (sign_videos.privacy = 0 OR sign_videos.author_id = ?)",(sen_video_id, user_id,))
        return result.fetchall()

    def search_sens_by_comp_sign(self, sign_video_id, user_id):
        """Поиск похожих жестов"""
        result = self.cursor.execute("SELECT sentences.id, sentences.name, sentence_videos.id FROM sentence_videos,sen_signs,sentences "\
           "WHERE sen_signs.sign_video_id = ? AND sen_signs.sen_video_id = sentence_videos.id AND sentence_videos.sentence_id = sentences.id "\
           "AND (sentence_videos.privacy = 0 OR sentence_videos.author_id = ?)",(sign_video_id, user_id,))
        return result.fetchall()

    def add_sign_cat(self, sign_id, category_id):
        """Добавление категории для жеста"""
        #self.cursor.execute("DELETE FROM sign_categories WHERE sign_id = ?",(sign_id,))
        try:
            self.cursor.execute("INSERT INTO sign_categories (sign_id, category_id) VALUES (?, ?)",(sign_id, category_id,))
            return self.conn.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)

    def del_sign_cat(self, sign_id, category_id):
        """Удаление категории для жеста"""
        self.cursor.execute("DELETE FROM sign_categories WHERE sign_id = ? AND category_id = ?",(sign_id,category_id,))
        return self.conn.commit()

    def add_sen_cat(self, sen_id, category_id):
        """Добавление категории для предложения"""
        #self.cursor.execute("DELETE FROM sign_categories WHERE sign_id = ?",(sign_id,))
        try:
            self.cursor.execute("INSERT INTO sentence_categories (sentence_id, category_id) VALUES (?, ?)",(sen_id, category_id,))
            return self.conn.commit()
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
            print("Exception class is: ", er.__class__)

    def del_sen_cat(self, sen_id, category_id):
        """Удаление категории для предложения"""
        self.cursor.execute("DELETE FROM sentence_categories WHERE sentence_id = ? AND category_id = ?",(sen_id,category_id,))
        return self.conn.commit()

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()




