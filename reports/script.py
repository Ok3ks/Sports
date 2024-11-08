import json
from app.src.utils import get_player

with open("reports/weekly_report/1088941_12.json", "r") as ins:
    obj = json.load(ins)

with open("json/downtown_players.json", "r") as ins:
    participant_json = json.load(
        ins
    )  # store as json because it can change weekly or update table weekly

keys = obj.keys()
print(keys)


def plural(value):
    if value > 1:
        return str(value) + " players"
    else:
        return str(value) + " player"


def text_output():
    """Output"""
    for key, values in obj.items():
        if key == "captain":
            print("Captain Stats")
            for i, j in values.items():
                print(f"\t{get_player(i).player_name} was captained by {plural(j)}")
        if key == "chips":
            print("\nChips Usage")
            for i, j in values.items():
                print(f"\t{i} was activated by {plural(j)}")

        # buggy, check code
        # if key == "league_average":
        # print(f"\nLeague Average was {values} points")

        if key == "most_points":
            for value in values:
                print(
                    f"{participant_json[value[0]]} was unlucky, with {value[2]} points on the bench"
                )
                # add more context to output

        if key == "jammy_points":
            print("\nLucky players rescued by Auto_sub")
            for value in values:
                print(
                    f"{participant_json[value[0]]}  {value[1]} coming on for {value[2]}, points_gained {value[3]}"
                )


text_output()
