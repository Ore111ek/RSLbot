﻿import sqlite3

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
        self.conn = sqlite3.connect(db_file, check_same_thread=False)

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

    def add_user(self, user_id, username, fname, lname, dialect):
        """Добавление пользователя в БД"""
        self.cursor.execute("INSERT INTO `users` (`user_id`, `username`, `first_name`, `last_name`, `dialect`) VALUES (?, ?, ?, ?, ?)",(user_id, username, fname, lname, dialect,))
        return self.conn.commit()

    def add_sign(self, user_id, dialect, name, part, desc, video1, video2, video3, picture, privacy):
        """Добавление жеста в БД"""
        self.cursor.execute("INSERT INTO `signs` (`author_id`, `dialect`, `name`, `part`, `description`, `video_file1`, `video_file2`, `video_file3`, `picture`, `privacy`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(user_id, dialect, name, part, desc, video1, video2, video3, picture,privacy,))
        return self.conn.commit()

    def add_sign_more_video(self, user_id, dialect, sign_id, video, privacy):
        """Добавление жеста в БД"""
        self.cursor.execute("INSERT INTO sign_more_videos (`author_id`, `dialect`, `sign_id`, `video_file`, `privacy`) VALUES (?, ?, ?, ?, ?)",(user_id, dialect, sign_id, video, privacy,))
        return self.conn.commit()

    def search_sign_more_video(self, sign_id, user_id):
        """Поиск дополнительных вариантов жестов в БД"""
        result = self.cursor.execute("SELECT * FROM sign_more_videos WHERE sign_id = ? AND (privacy = 0 OR author_id = ? ) ORDER BY id",(sign_id, user_id,))
        return result.fetchall()

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

    def search_sign_by_name_auth(self, name, part, author_id):
        """Получение жеста из БД"""
        result = self.cursor.execute("SELECT * FROM signs WHERE name = ? AND part = ? AND author_id = ?",(name, part, author_id,))
        return result.fetchone()

    def make_sign_fav(self, user_id, sign_id):
        """Добавление жеста в избранное"""
        self.cursor.execute("INSERT INTO fav_signs (user_id, sign_id) VALUES (?, ?)",(user_id, sign_id, ))
        return self.conn.commit()

    def search_sign_fav(self, user_id, sign_id):
        """Проверка, добавлен ли жест в избранное"""
        result = self.cursor.execute("SELECT * FROM fav_signs WHERE user_id = ? AND sign_id = ?",(user_id,sign_id,))
        return bool(len(result.fetchall()))

    def make_sign_nfav(self, user_id, sign_id):
        """Удаление жеста из избранного"""
        self.cursor.execute("DELETE FROM fav_signs WHERE user_id = ? AND sign_id = ?",(user_id,sign_id,))
        return self.conn.commit()

    def search_signs_fav(self, user_id):
        """Поиск всех жестов в избранном"""
        result = self.cursor.execute("SELECT id, name, part FROM signs, fav_signs WHERE (privacy = 0 OR author_id = ?) AND id = sign_id AND user_id = ?",(user_id,user_id,))
        return result.fetchall()

    def make_sign_learn(self, user_id, sign_id):
        """Добавление жеста в изучаемые"""
        self.cursor.execute("INSERT INTO learn_signs (user_id, sign_id) VALUES (?, ?)",(user_id, sign_id, ))
        return self.conn.commit()

    def search_sign_learn(self, user_id, sign_id):
        """Проверка, добавлен ли жест в изучаемое"""
        result = self.cursor.execute("SELECT * FROM learn_signs WHERE user_id = ? AND sign_id = ?",(user_id,sign_id,))
        return bool(len(result.fetchall()))

    def make_sign_nlearn(self, user_id, sign_id):
        """Удаление жеста из изуччаемого"""
        self.cursor.execute("DELETE FROM learn_signs WHERE user_id = ? AND sign_id = ?",(user_id,sign_id,))
        return self.conn.commit()

    def search_signs_learn(self, user_id):
        """Поиск всех жестов из изучаемого"""
        result = self.cursor.execute("SELECT id, name, part FROM signs, learn_signs WHERE (privacy = 0 OR author_id = ?) AND id = sign_id AND user_id = ?",(user_id,user_id,))
        return result.fetchall()

    def add_cat(self, name, description):
        """Добавление категории в БД"""
        self.cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)",(name, description,))
        return self.conn.commit()

    def search_all_cats(self):
        """Поиск всех категорий"""
        result = self.cursor.execute("SELECT id, name, description FROM categories")
        return result.fetchall()

    def get_cat_by_cat_id(self,category_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT id, name, description FROM categories WHERE id = ?",(category_id,))
        return result.fetchone()

    def get_cat_by_sign_id(self,sign_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT categories.id, categories.name, categories.description FROM categories,signs,sign_categories WHERE signs.id = ? AND categories.id = category_id AND sign_id = signs.id",(sign_id,))
        return result.fetchall()

    def check_sign_in_cat(self,sign_id, category_id):
        """Поиск категории по её id"""
        result = self.cursor.execute("SELECT * FROM sign_categories WHERE sign_id = ? AND category_id = ?",(sign_id,category_id,))
        return bool(len(result.fetchall()))

    def search_signs_in_cat(self,category_id, user_id):
        """Поиск всех жестов в категории"""
        result = self.cursor.execute("SELECT signs.id, signs.name, signs.part FROM categories, signs, sign_categories WHERE categories.id = ? AND categories.id = category_id AND sign_id = signs.id AND (privacy = 0 OR author_id = ?)",(category_id,user_id,))
        return result.fetchall()

    def add_sim_signs(self, sign_id, sign2_id, diff):
        """Добавление связи между похожими жестами"""
        self.cursor.execute("INSERT INTO sim_signs (sign_id, sign2_id, diff) VALUES (?, ?, ?)",(sign_id, sign2_id, diff,))
        return self.conn.commit()

    def del_sim_signs(self, sign_id, sign2_id):
        """Удаление связи между похожими жестами"""
        self.cursor.execute("DELETE FROM sim_signs WHERE (sign_id = ? AND sign2_id = ?) OR (sign2_id = ? AND sign_id = ?)",(sign_id, sign2_id, sign_id, sign2_id,))
        return self.conn.commit()

    def check_sim_signs(self, sign_id, sign2_id):
        """Проверка связи между похожими жестами"""
        result = self.cursor.execute("SELECT * FROM sim_signs WHERE (sign_id = ? AND sign2_id = ?) OR (sign2_id = ? AND sign_id = ?)",(sign_id, sign2_id, sign_id, sign2_id,))
        return bool(len(result.fetchall()))

    def search_sim_signs(self, sign_id, user_id):
        """Поиск похожих жестов"""
        result = self.cursor.execute("SELECT signs.id, signs.name, signs.part, diff FROM signs, sim_signs WHERE sign_id = ? AND sign2_id = id AND (privacy = 0 OR author_id = ?) UNION SELECT signs.id, signs.name, signs.part, diff FROM signs, sim_signs WHERE sign2_id = ? AND sign_id = id AND (privacy = 0 OR author_id = ?)",(sign_id, user_id, sign_id, user_id,))
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

    def close(self):
        """Закрытие соединения с БД"""
        self.conn.close()




