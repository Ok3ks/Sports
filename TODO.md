## Done

- use async connection engine for database
- parameterize async client
- wrap async functions in task groups
    - async functions within report class
- Test async client works 
- write tests, use task groups where appropriate (league, )


- Test with locust
- profile before and after (with free-threaded python)
- deploy - move to uvicorn

- rate limit participant report endpoint
- authorize league report endpoint
- parameterize season as an enum or rather an env variable?
- only io blocking task in leagueweeklyreport is get_data, split methods to worker threads, to gain speedup, i.e map reduce?

Limitations.
- Unable to use Django user model because of embedded database which is replaced on redeploy

- Try out pgembed/aiosqlite as embedded database, and for concurrent async connections

Features
- Live Table which updates