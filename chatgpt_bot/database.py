import aiosqlite
import json


class DataBase:
    # def __init__(self):
    #     self.create_connection()

    async def create_connection(self):
        self.con = await aiosqlite.connect('chatgpt_bot_db.db')
        await self.create_tables()

    async def create_tables(self):
        await self.con.execute('''CREATE TABLE IF NOT EXISTS conversation 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                messages json)''')

        await self.con.execute('''CREATE TABLE IF NOT EXISTS users 
                                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER)''')

    async def add_message(self, user_id: int, message: str):
        async with self.con.execute('''SELECT messages FROM conversation WHERE user_id=?''', (user_id,)) as cur:
            user_messages = (await cur.fetchone())

        if user_messages is None:
            messages = [{'role': 'user', 'content': message}]
            async with self.con.execute('''INSERT INTO conversation (user_id, messages) VALUES(?, ?)''',
                                        (user_id, json.dumps(messages))):
                await self.con.commit()
        else:
            messages = json.loads(user_messages[0])
            messages.append({'role': 'user', 'content': message})
            async with self.con.execute('''UPDATE conversation SET messages=? WHERE user_id=?''',
                                        (json.dumps(messages), user_id)):
                await self.con.commit()

    async def add_assistant_message(self, user_id: int, message: str):
        async with self.con.execute('''SELECT messages FROM conversation WHERE user_id=?''', (user_id,)) as cur:
            user_messages = (await cur.fetchone())

        if user_messages is None:
            messages = [{'role': 'assistant', 'content': message}]
            async with self.con.execute('''INSERT INTO conversation (user_id, messages) VALUES(?, ?)''',
                                        (user_id, json.dumps(messages))):
                await self.con.commit()
        else:
            messages = json.loads(user_messages[0])[-10:]
            messages.append({'role': 'assistant', 'content': message})
            async with self.con.execute('''UPDATE conversation SET messages=? WHERE user_id=?''',
                                        (json.dumps(messages), user_id)):
                await self.con.commit()

    async def get_messages(self, user_id: int):
        async with self.con.execute('''SELECT messages FROM conversation WHERE user_id=?''', (user_id,)) as cur:
            user_messages = (await cur.fetchone())
        if user_messages is None:
            return None
        return json.loads(user_messages[0])

    async def clear_messages(self, user_id: int):
        async with self.con.execute('''DELETE FROM conversation WHERE user_id=?''',
                                    (user_id,)):
            await self.con.commit()

    async def add_user(self, user_id: int):
        async with self.con.execute('''INSERT INTO users (user_id) VALUES(?)''', (user_id,)):
            await self.con.commit()

    async def get_users(self):
        async with self.con.execute('''SELECT * FROM users''') as cur:
            return await cur.fetchall()


db = DataBase()
