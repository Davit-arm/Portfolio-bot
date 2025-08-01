import sqlite3
from config import DATABASE


skills = [ (_,) for _ in (['github skills', 'working with json files', 'working with databases', 'working with Telegram API'])]
statuses = [ (_,) for _ in (['Not Ready', 'In Progress', 'Partially done', 'fully completed'])]

class DB_Manager:
    def __init__(self, database):
        self.database = database # имя базы данных
        
    def create_tables(self):
        conn = sqlite3.connect(self.database)

        with conn:
            # создаем таблицу project
            conn.execute('''CREATE TABLE IF NOT EXISTS project (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            name TEXT NOT NULL,
                            description TEXT,
                            url TEXT,
                            status_id INTEGER,
                            FOREIGN KEY(status_id) REFERENCES status(id))''')
            
            # создаем таблицу skill
            conn.execute('''CREATE TABLE IF NOT EXISTS skill (
                            id INTEGER PRIMARY KEY,
                            name TEXT)''')
            
            # создаем таблицу project_skill
            conn.execute('''CREATE TABLE IF NOT EXISTS project_skill (
                            project_id INTEGER,
                            skill_id INTEGER,
                            FOREIGN KEY(project_id) REFERENCES project(id),
                            FOREIGN KEY(skill_id) REFERENCES skill(id))''')
            
            # создаем таблицу status
            conn.execute('''CREATE TABLE IF NOT EXISTS status  (
                            id INTEGER PRIMARY KEY,
                            name TEXT)''')
            
            # сохраняем изменения и закрываем соединение
            conn.commit()

    def __executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()
    
    def __select_data(self, sql, data = tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()
        
    def default_insert(self):
        sql = 'INSERT OR IGNORE INTO skill (name) values(?)'
        data = skills
        self.__executemany(sql, data)
        sql = 'INSERT OR IGNORE INTO status (name) values(?)'
        data = statuses
        self.__executemany(sql, data)

    def insert_project(self, data):
        sql = """INSERT INTO projects 
    (user_id, project_name, url, status_id) 
    values(?, ?, ?, ?)"""
        self.__executemany(sql, data)

    def insert_skill(self, user_id, project_name, skill):
        sql = 'SELECT id FROM project WHERE name = ? AND user_id = ?'
        project_id = self.__select_data(sql, (project_name, user_id))[0][0]
        skill_id = self.__select_data('SELECT id FROM skill WHERE name = ?', (skill,))[0][0]
        data = [(project_id, skill_id)]
        sql = 'INSERT OR IGNORE INTO project_skill VALUES(?, ?)'
        self.__executemany(sql, data)

    def get_statuses(self):
        sql = """INSERT INTO projects 
    (user_id, project_name, url, status_id) 
    values(?, ?, ?, ?)"""
        return self.__select_data(sql)
        
    def get_status_id(self, status_name):
        sql = 'SELECT id FROM status WHERE name = ?'
        res = self.__select_data(sql, (status_name,))
        if res: return res[0][0]
        else: return None

    def get_projects(self, user_id):
        sql = sql="""SELECT * FROM projects 
        WHERE user_id = ?"""
        return self.__select_data(sql, data = (user_id,))
        
    def get_project_id(self, project_name, user_id):
        return self.__select_data(sql='SELECT id FROM project WHERE name = ? AND user_id = ?  ', data = (project_name, user_id,))[0][0]
        
    def get_skills(self):
        return self.__select_data(sql='SELECT * FROM skill')
    
    def get_project_skills(self, project_name):
        res = self.__select_data(sql='''SELECT name FROM project 
        JOIN project_skill ON projects.id = project_skills.project_id 
        JOIN skill ON skills.id = project_skills.skill_id 
        WHERE name = ?''', data = (project_name,) )
        return ', '.join([x[0] for x in res])
    
    def get_project_info(self, user_id, project_name):
        sql = """
        SELECT name, description, url, name FROM projects 
        JOIN status ON
        status.id = projects.status_id
        WHERE name=? AND user_id=?
        """
        return self.__select_data(sql=sql, data = (project_name, user_id))


    def update_projects(self, param, data):
        sql = sql = f"""UPDATE projects SET {param} = ? 
        WHERE project_name = ? AND user_id = ?"""
        self.__executemany(sql, [data]) 

    def delete_project(self, user_id, project_id):
        sql = sql = """DELETE FROM projects 
        WHERE user_id = ? AND project_id = ? """
        self.__executemany(sql, [(user_id, project_id)])
    
    def delete_skill(self, project_id, skill_id):
        sql = """DELETE FROM skills 
    WHERE skill_id = ? AND project_id = ? """
        self.__executemany(sql, [(skill_id, project_id)])

if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    manager.create_tables()