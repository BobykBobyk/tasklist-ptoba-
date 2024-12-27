import aiomysql
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()


class Task(BaseModel):
    id_get: int = Query(..., description='enter id for your task')
    description_get: str = Query(..., description='enter description for your task')


async def get_db_pool():
    return await aiomysql.create_pool(
        host='localhost',
        port=3306,
        user='root',
        password='password',
        db='db',
        minsize=5,
        maxsize=10
    )


async def create_database():
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("CREATE DATABASE IF NOT EXISTS db;")
        await connection.commit()
    pool.close()
    await pool.wait_closed()


async def create_table():
    pool = await get_db_pool()
    async with pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                description VARCHAR(255),
                content TEXT
            );
            """)
        await connection.commit()
    pool.close()
    await pool.wait_closed()


@app.on_event('startup')
async def startup_event():
    await create_database()
    await create_table()


@app.post('/task_add/')
async def task_add(task: Task):
    try:
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO data (id, description)
                    VALUES (%s, %s, %s)""", (task.id_get, task.description_get)
                )
            await connection.commit()
        pool.close()
        await pool.wait_closed()
        return {'message': 'It was added succesfully'}

    except:
        raise HTTPException(status_code=400, detail="Enter valid data")


@app.put('/task_edit/')
async def task_edit(task: Task):
    try:
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("""
                DELETE FROM data WHERE id = %s
                """, (task.id_get,)
                )
            await connection.commit()
        pool.close()
        await pool.wait_closed()

        pool = await get_db_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO data (id, description)
                    VALUES (%s, %s, %s)""", (task.id_get, task.description_get)
                )
            await connection.commit()
        pool.close()
        await pool.wait_closed()

        return{'message': 'changes were added succesfully'}

    except:
        raise HTTPException(status_code=400, detail="Enter valid data")


@app.delete('/task_delete/')
async def task_delete(task: Task):
    try:
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute("""
                       DELETE FROM data WHERE id = %s
                       """, (task.id_get,)
                                     )
            await connection.commit()
        pool.close()
        await pool.wait_closed()
        return {'message': 'The given task was deleted succesfully'}

    except:
        raise HTTPException(status_code=400, detail="Enter valid data")


@app.get('/task_get_one/')
async def task_get_one(task: Task):
    try:
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM data WHERE id = %s""", (task.id_get,)
                )
                response = await cursor.fetchone()
        pool.close()
        await pool.wait_closed()
        return {'response': response}
    except:
        raise HTTPException(status_code=400, detail="Enter valid data")


@app.get('/task_get_all/')
async def task_get_all():
    try:
        pool = await get_db_pool()
        async with pool.acquire() as connection:
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT * FROM data"""
                )
                response = await cursor.fetchone()
        pool.close()
        await pool.wait_closed()
        return {'response': response}
    except:
        raise HTTPException(status_code=400, detail="Enter valid data")
