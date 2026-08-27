
## Assurance - Backend
- write/update tests
- Test with locust -- t
- profile before and after (with free-threaded python). Bump up to 3.13

### AI features
- Add logging/monitoring layer, i.e logfire for AI layer  -- done
- Tools, Prompt, Resources  -- Turns out, all i need are tools but prohibitive cost of claude means self hosting models 
- Interact with sqlite database on this one -- I called the json directly from the storage bucket


- Expose with Daphne on the frontend
- Evaluate prompts 
- expose mcp to resolvers, maybe not necessary?? can plugin to frontend typescript, experiment with


### DevOps
- deploy backend - move to uvicorn
- Deploy open-weight model for mcp feature (maybe use a cluster)
- Logfire for other monitoring aspectS? --- I already have cloud logs


### Authorization & Authentication
- rate limit participant report endpoint
- authorize league report endpoint
- only io blocking task in leagueweeklyreport is get_data, split methods to worker threads, to gain speedup, i.e map reduce?



### Nice to haves
- use async connection engine for database
- wrap async functions in task groups
    - async functions within report class
- Django is overkill, can replace only with fastAPI
- write tests, use task groups where appropriate (league, )



### Done 
- parameterize async client --- Done
- Test async client works 


Limitations.
- Unable to use Django user model because of embedded database which is replaced on redeploy
- Try out pgembed/aiosqlite as embedded database, and for concurrent async connections
