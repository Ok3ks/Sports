cp reports/weekly_report/1088941_16.json app/LiveProject/templates
mv 1088941_16.json 1088941.json
into a script

for i in {1..25}
do python3 src write_participant_weekly -g -ta -l 
done


sqlite3 -json fpl "select * from EPL_PLAYERS_2023_1ST_HALF" > file.json

table of league to participants_id #important for offseason
table of fixtures - write_fixtures.py
table of transfer entries with each column representing each gameweek, and rows are entry_id (10m * 38) - write_transfer_entries.py

source init_env.sh
source auth.sh
initialize virtual environment

git reset --soft HEAD~

Frontend

Backend

Cloud deployment

Prototype - all above, with Downtown league for starters

- Migrate downtown alone to cloud with sqldump
- Build Django models with frontend data
- Design form, authorization and login with Django

- Deploy with Docker compose, cloudsql and containerised django application
- Map domain to ip address

- In the meantime, find FPL wire, group link and begin to make noise on discord/twitter. A good way to begin promotion
- Use Gameweek 1 entries to profile, optimize codebase and add gameweek features for large data.

- Use dash
- Use poetry
