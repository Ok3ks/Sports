for i in {1..38}
    do
    python src/db/update_gameweek_score.py -g "$i"
    done

python src/db/update_player_information.py -ha 1
python src/db/update_player_information.py -ha 2
