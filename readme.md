# myLibrary

## Fastapi application with the ability to view books on different devices with saving reading progress

# How to run it:
1) create `backend/.env` file
2) create `alembic.ini` file
3) create postgres database:\
`docker run --name postgres -e POSTGRES_PASSWORD=PASS -e POSTGRES_USER=USER -p 5432:5432 -d postgres`
4) create pgadmin:\
`docker run --name pgadmin -p 80:80 -e PGADMIN_DEFAULT_EMAIL=MAIL -e PGADMIN_DEFAULT_PASSWORD=PASS_FOR_PGADMIN -d dpage/pgadmin4`
5) create table in pgadmin
6) create redis: 
`docker run --name redis -p 6369:6379 -d redis`
7) run migrations:\
`alembic revision --autogenerate -m "Message"`\
`alembic upgrade head`
8) run backend: \
`cd backend`\
`python3 main.py`
9) run frontend:\
`cd frontend`\
`yarn start`
10) enjoy 👀

