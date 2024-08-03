# Budget Project
Need to manage your finances but you don't want to sell your soul for a meager intuition of what to do? Does the thought of exhaustively sharing your entire spending history in exchange for basic budgeting tools make you sigh? Maybe this project is right for you then

The current goal is to create a simple tool that allows you to import, review, and categorize transactions for one or more credit or checking accounts, creating one or more budgets or forecasts to better manage your financial resources. 

This repository encapsulates the work involved in orechestrating the behind-the-scenes work of making that all happen. 

Starting database (first time)

```
docker run --name budget-database -e POSTGRES_PASSWORD=ineedabudget -p 127.0.0.1:5432:5432/tcp -d postgres
```

Connecting to database using psql
(Consider setting an environment variable for `SQLALCHEMY_CONNECTION_STRING` if you want to chagne it from the default)
```
psql -U postgres -h localhost
create database budget;
```

Creating new database migrations and upgrading your local database
```
cd database
alembic revision --autogenerate
alembic upgrade head
```

TODO: 
[DONE] basic database setup
[DONE] basic csv parsing
FastAPI router for basic operations
OpenAPI json generator
React App for frontend
Consider reimplementing in Electron?