# Research

To run the application you will need a database. The choice was made in favor of PostgreSQL.

Benefits of PostgreSQL:

1) Reliability and data integrity:
PostgreSQL provides high reliability and supports transactionality,
making it the preferred choice for applications,
where data security is required, for example.
2) SQL support and complex queries: PostgreSQL offers full support
SQL language, including advanced functions, stored procedures and capabilities
query optimization.
3) Extensibility: PostgreSQL supports user-defined stored functions
procedures, indexes, and other extensions that allow developers to create
more complex and optimized queries.

MongoDB in this case is a much less suitable DBMS, since we do not
required to store different types of data within one collection without strict
schemas, does not support SQL queries and does not guarantee data integrity.
