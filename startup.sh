
source init_env.sh
source dev-auth.sh
touch $DB_PATH
cd LiveProject

python src/db/update_player_information.py -ha 1
python src/db/update_player_information.py -ha 2

for i in {1..38}
do
python src/db/update_gameweek_score.py -g $i
done
