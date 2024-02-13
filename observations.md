## In trying to migrate sqlite3 to Mysql, I noticed pandas only supports sqlite3 or sqlalchemy connections for its .to_sql function
## Was able to achieve speedups by switching db from sqlite3 to mysql, open a sessionmaker factory once which allows multiple reads across program lifetime

## Also sped up promoted vice by modifying algorithms 
## Major speed delay seems to come from getting the data through API calls 

## Also save report results in a nosql db