from fastapi import FastAPI, Depends
from src.routes import contacts, users
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import uvicorn
import redis.asyncio as redis
from src.conf.config import config


app = FastAPI()
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

@app.on_event('startup')
async def startup():
    rds = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0,
                      encoding='utf-8', decode_responses=True)  # password=config.REDIS_PASSWORD,
    await FastAPILimiter.init(rds)

@app.get('/', dependencies=[Depends(RateLimiter(times=2, seconds=5))])
def index():
    return {'message': 'Contacts application'}

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload=True)