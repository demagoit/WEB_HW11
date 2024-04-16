FastAPI, Postgres, SQLAlchemy, Pydantic 

in auth.yaml set desired JWT crypto algorithm and secret

mkdir bd_data

sudo docker compose up

chmod 777 -R bd_data/pgdata

uvicorn main:app --reload

http://127.0.0.1:8000/docs#/
