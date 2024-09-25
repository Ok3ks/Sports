- In trying to migrate sqlite3 to Mysql, I noticed pandas only supports sqlite3 or sqlalchemy connections for its .to_sql function
- Was able to achieve speedups by switching db from sqlite3 to mysql, open a sessionmaker factory once which allows multiple reads across program lifetime

- Combined all gameweeks into one table since 38 * 714 is within the limit of rows for a mysql table, these prevents joins when analysis done over gameweeks 

- Also sped up promoted vice by modifying algorithms 
- Major speed delay seems to come from getting the data through API calls 

- Tested multithreading(multiprocessing.dummies) to improve speed of retrieving entries via APIs, and chained generators with itertools for League reports. 

Issue was generators have to be fully loaded into memory by pandas before execution. Solution was to write to db in chunks and analyse in chunks or with clusters and Dask for rows upto 10m

- Also experimented with other frameworks like concurrent.futures ProcessPoolExecutor which I preferred to multiprocessing.Pool to bypass the Global Interpreter lock for multiprocessing.

- Also save report results in a nosql db.

- Difference between multithreading and multiprocessing is that multithreading shares same memory space, which can sometimes not lead to speed gains for large datasets as memory per core is limited. Multiprocesses, each memory has its own memory space but shared memory can be instantiated with these frameworks.

- For cython optimized code, OpenMp can be used for immediate parallelism.

- Requirements.txt may contain some packages that are unneeded so trim before Dockerfile is created