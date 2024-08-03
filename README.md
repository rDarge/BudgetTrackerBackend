# I need a budget
Do you need a budget too? Do you need to manage your finances but don't want to ~~sell your soul~~ share your personal data in order to chart your spending? Does the thought of exhaustively sharing your entire spending history in exchange for basic budgeting tools make you sigh? Unfortunately, this project probably still isn't right for you, as it's still very rough around the edges. Consider looking at other alternatives like:

*  [Firefly III](https://github.com/firefly-iii/firefly-iii)
*  [Money Manager Ex](https://github.com/moneymanagerex/moneymanagerex)
*  [GnuCash](https://github.com/Gnucash/gnucash)

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
* [DONE] *basic database setup*
* [DONE] *basic csv parsing*
* [NEXT] **FastAPI router for basic operations**
* OpenAPI json generator
* React App for frontend
* Consider reimplementing in Electron?