from faststream import FastStream
from src.faststream.broker import broker
from src.faststream.subscribers.users import router as users_router
from src.database import init_db, dispose

app = FastStream(
    broker
)

broker.include_router(users_router)

@app.after_startup
async def startup():
    init_db() # Инициализируем engine и sessionmaker

@app.after_shutdown
async def shutdown():
    await dispose() # Закрываем соединения