import aiosqlite


# Drop the existing table
async def drop_table(conn):
    async with conn.cursor() as cursor:
        await cursor.execute("DROP TABLE IF EXISTS users;")
        await conn.commit()


# Create the new table
async def create_table(conn):
    async with conn.cursor() as cursor:
        await cursor.execute("""CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username VARCHAR(32) NOT NULL,
                            language VARCHAR(80) NOT NULL,
                            name VARCHAR(20) NOT NULL,
                            age INTEGER NOT NULL,
                            height INTEGER NOT NULL,
                            coord_x REAL NOT NULL,
                            coord_y REAL NOT NULL,
                            photos VARCHAR NOT NULL,
                            mainText VARCHAR,
                            gender VARCHAR(1) NOT NULL,
                            find_gender VARCHAR(1) NOT NULL,
                            minAge INTEGER,
                            maxAge INTEGER,
                            minHeight INTEGER,
                            maxHeight INTEGER
                            );""")
        await conn.commit()


# Insert data into the users table
async def insert_data(conn, user_data):
    async with conn.cursor() as cursor:
        await cursor.execute("""INSERT INTO users (
                            username, language, name, age, height, coord_x, coord_y, photos, mainText, gender,
                             find_gender, minAge, maxAge, minHeight, maxHeight
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", user_data)
        await conn.commit()


async def add_user(user_data):
    async with aiosqlite.connect('./db/users_data.sqlite') as conn:
        await insert_data(conn, user_data)


async def get_user_data(user_id: str) -> tuple[str, int, float, str, str]:
    try:
        async with aiosqlite.connect('./db/users_data.sqlite') as conn:
            async with conn.cursor() as cursor:
                query = "SELECT name, age, height, photos, mainText FROM users WHERE user_id =?"
                await cursor.execute(query, (user_id,))
                result = await cursor.fetchone()
                if result:
                    return result  # Return the tuple without dereferencing
                # else:
                #     return None  # Return None if no user found
    except aiosqlite.Error as e:
        print(f"Error fetching user data: {e}")
        # return None

from data import database
from data.user_form import User
async def get_user_by_id(user_id: str):
    try:
        session = database.create_session()
        try:
            user = await session.query(User).filter_by(user_id=user_id).first()
        except Exception:
            user = User()
            user.user_id = user_id
            session.add(user)
            session.commit()
            await get_user_by_id(user_id)

    except Exception as err:
        return err

