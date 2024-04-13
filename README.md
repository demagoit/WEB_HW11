FastAPI, Postgres, SQLAlchemy, Pydantic 

mkdir bd_data

sudo docker compose up

chmod 777 -R bd_data/pgdata

uvicorn main:app --reload

http://127.0.0.1:8000/docs#/
