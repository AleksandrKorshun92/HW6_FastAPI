# Создать API для управления списком задач.
# Каждая задача должна содержать поля "название",
# "описание" и "статус" (выполнена/не выполнена).
# API должен позволять выполнять CRUD операции с
# задачами.

from fastapi import FastAPI
from pydantic import BaseModel, Field
import databases
import sqlalchemy
from typing import List
import aiosqlite
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

app = FastAPI()

tasks = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(50)),
    sqlalchemy.Column("description", sqlalchemy.String(1000)),
    sqlalchemy.Column("status", sqlalchemy.String(50))
)

class Task(BaseModel):
    id: int
    name: str = Field(title="Name", max_length=50)
    description: str = Field(default=None, title="Description", max_length=1000)
    status: str = Field(title="Status")

class TaskIn(BaseModel):
    name: str = Field(title="Name", max_length=50)
    description: str = Field(default=None, title="Description", max_length=1000)
    status: str = Field(title="Status")

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


@app.get("/tasks/{count}")
async def create_tasks(count: int):
    task_true = "выполнена"
    task_false = "не выполнена"
    for i in range(count):
        if i%2==0:
            query = tasks.insert().values(name=f'task{i}', description=f'description{i}', status= f'задача {task_true}')
        else:
            query = tasks.insert().values(name=f'task{i}', description=f'description{i}', status= f'задача {task_false}')
        await database.execute(query)
    return {'message': f'{count} tasks create'}


@app.get("/all/", response_model=List[Task])
async def read_tasks_all():
    query = tasks.select()
    return await database.fetch_all(query)

@app.get("/task/{tasks_id}", response_model=Task)
async def read_task_id(tasks_id: int):
    query = tasks.select().where(tasks.c.id == tasks_id)
    return await database.fetch_one(query)


@app.post("/append/", response_model=Task)
async def create_task(task: TaskIn):
    query = tasks.insert().values(name=task.name, description=task.description, status= task.description)
    last_record_id = await database.execute(query)
    return {**task.dict(), "id": last_record_id}

@app.put("/update/{tsk_id}", response_model=Task)
async def update_task(tsk_id: int, new_task: TaskIn):
    query = tasks.update().where(tasks.c.id == tsk_id).values(**new_task.dict())
    await database.execute(query)
    return await read_task_id(tsk_id)

@app.delete("/delete/{tsk_id}")
async def delete_task(tsk_id: int):
    query = tasks.delete().where(tasks.c.id == tsk_id)
    await database.execute(query)
    return {'message': f'Task deleted {tsk_id}'}