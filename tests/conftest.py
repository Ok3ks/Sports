import pytest
from src.paths import REPORT_DIR
import os
from os.path import join,realpath


@pytest.fixture(scope="module")
def league_fixture():
    return int(1088941)

@pytest.fixture(scope="module")
def auto_sub_fixture():
    return {
        "auto_subs": {"0": {"in": [], "out": []}, "1": {"in": [377], "out": [8]}, "2": {"in": [298], "out": [157]}, "3": {"in": [], "out": []}, "4": {"in": [], "out": []}, 
                      "5": {"in": [], "out": []}, "6": {"in": [], "out": []}, "7": {"in": [], "out": []}, "8": {"in": [113], "out": [28]}, "9": {"in": [], "out": []}, 
                      "10": {"in": [], "out": []}, "11": {"in": [275], "out": [148]}, "12": {"in": [], "out": []}, "13": {"in": [], "out": []}, "14": {"in": [], "out": []}, 
                      "15": {"in": [], "out": []}, "16": {"in": [], "out": []}, "17": {"in": [], "out": []}, "18": {"in": [], "out": []}, "19": {"in": [], "out": []}, 
                      "20": {"in": [], "out": []}, "21": {"in": [], "out": []}, "22": {"in": [], "out": []}, "23": {"in": [], "out": []}, "24": {"in": [], "out": []}, 
                      "25": {"in": [], "out": []}, "26": {"in": [], "out": []}, "27": {"in": [], "out": []}, "28": {"in": [139], "out": [415]}, "29": {"in": [], "out": []}, 
                      "30": {"in": [], "out": []}, "31": {"in": [], "out": []}, "32": {"in": [], "out": []}, "33": {"in": [], "out": []}, "34": {"in": [], "out": []}, 
                      "35": {"in": [], "out": []}, "36": {"in": [], "out": []}, "37": {"in": [], "out": []}, "38": {"in": [], "out": []}, "39": {"in": [], "out": []}, 
                      "40": {"in": [524], "out": [148]}, "41": {"in": [], "out": []}, "42": {"in": [298], "out": [341]}, "43": {"in": [], "out": []}, "44": {"in": [], "out": []}
        }
    }

@pytest.fixture(scope="module")
def league_weekly_score():

    return {
        "auto_subs": {"0": {"in": [], "out": []}, "1": {"in": [], "out": []},"2": {"in": [], "out": []}, "3": {"in": [377], "out": [8]}, "4": {"in": [298], "out": [157]}, 
                    "5": {"in": [], "out": []}, "6": {"in": [85], "out": [415]}, "7": {"in": [], "out": []}, "8": {"in": [], "out": []}, 
                    "9": {"in": [], "out": []}, "10": {"in": [], "out": []}, "11": {"in": [], "out": []}, "12": {"in": [], "out": []}, 
                    "13": {"in": [5], "out": [558]}, "14": {"in": [], "out": []}, "15": {"in": [113], "out": [28]}, "16": {"in": [], "out": []}, 
                    "17": {"in": [], "out": []}, "18": {"in": [], "out": []}, "19": {"in": [], "out": []}, "20": {"in": [], "out": []},"21": {"in": [], "out": []}, 
                    "22": {"in": [275], "out": [148]}, "23": {"in": [], "out": []}, "24": {"in": [], "out": []}, "25": {"in": [], "out": []}, 
                    "26": {"in": [], "out": []}, "27": {"in": [], "out": []}, "28": {"in": [314], "out": [8]}, "29": {"in": [], "out": []}, 
                    "30": {"in": [], "out": []}, "31": {"in": [], "out": []}, "32": {"in": [], "out": []}, "33": {"in": [], "out": []}, 
                    "34": {"in": [], "out": []}, "35": {"in": [], "out": []}, "36": {"in": [], "out": []}, "37": {"in": [], "out": []}, 
                    "38": {"in": [], "out": []}, "39": {"in": [], "out": []}, "40": {"in": [], "out": []}, 
                    },
        "entry": {"0": 3960377, "1": 1086398, "2": 293449, "3": 98120, "4": 175583, "5": 1070898, "6": 4006993, "7": 6388931, "8": 18103, "9": 32133, "10": 3955774, "11": 563294, "12": 5748350, "13": 213565, "14": 5336861, "15": 1145568, "16": 4145862, "17": 3968042, "18": 4805585, "19": 6380329, "20": 3572212, "21": 6570495, "22": 4050576, "23": 3962660, "24": 24268, "25": 1172179, "26": 3829907, "27": 4691088, "28": 1635237, "29": 150479, "30": 4275778, "31": 669180, "32": 2873232, "33": 124922, "34": 4917316, "35": 890194, "36": 456141, "37": 6013821, "38": 2246822, "39": 992871, "40": 1680671},
        "active_chip": {"0": None, "1": None, "2": None, "3": None, "4": None, "5": None, "6": None, "7": None, "8": None, "9": None, "10": None, "11": None, "12": None, "13": None, "14": None, "15": None, "16": None, "17": None, "18": None, "19": None, "20": None, "21": None, "22": None, "23": None, "24": None, "25": None, "26": None, "27": None, "28": None, "29": None, "30": None, "31": None, "32": None, "33": None, "34": None, "35": None, "36": None, "37": None, "38": None, "39": None, "40": None},
        "points_on_bench": {"0": -1, "1": 0, "2": 1, "3": 2, "4": 16, "5": 3, "6": 9, "7": 16, "8": 5, "9": 0, "10": 3, "11": 1, "12": 22, "13": 1, "14": 20, "15": 8, "16": 4, "17": 13, "18": 13, "19": 6, "20": 0, "21": 4, "22": 20, "23": 1, "24": 17, "25": 2, "26": 7, "27": 5, "28": 0, "29": 19, "30": 7, "31": 11, "32": 3, "33": 2, "34": 15, "35": 2, "36": 20, "37": 5, "38": 0, "39": 19, "40": 4},
        "total_points": {"0": 76, "1": 83, "2": 86, "3": 92, "4": 90, "5": 109, "6": 44, "7": 62, "8": 91, "9": 91, "10": 81, "11": 69, "12": 69, "13": 62, "14": 56, "15": 57, "16": 68, "17": 83, "18": 86, "19": 75, "20": 60, "21": 75, "22": 62, "23": 67, "24": 64, "25": 89, "26": 75, "27": 87, "28": 66, "29": 88, "30": 80, "31": 65, "32": 86, "33": 87, "34": 68, "35": 59, "36": 75, "37": 67, "38": 54, "39": 77, "40": 82},
        "event_transfers_cost": {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 4, "12": 0, "13": 0, "14": 0, "15": 0, "16": 0, "17": 0, "18": 0, "19": 0, "20": 0, "21": 0, "22": 0, "23": 0, "24": 0, "25": 0, "26": 0, "27": 0, "28": 0, "29": 0, "30": 0, "31": 0, "32": 0, "33": 4, "34": 0, "35": 0, "36": 0, "37": 0, "38": 0, "39": 0, "40": 0},
        "players": {"0": "524,407,506,131,34,362,349,353,19,117,60", "1": "409,506,430,290,362,19,353,412,85,355,60", "2": "409,369,131,427,12,19,509,362,526,117,60", "3": "409,290,83,131,377,294,412,509,353,349,60", "4": "597,131,430,298,353,362,19,303,60,117,355", "5": "113,342,430,506,294,509,353,19,362,355,60", "6": "409,519,369,5,526,349,19,362,303,343,85", "7": "524,290,506,31,430,362,349,19,526,85,60", 
                    "8": "409,519,5,131,353,19,134,509,412,60,355", "9": "275,519,290,131,362,382,353,412,135,355,60", "10": "113,131,506,5,349,134,353,19,362,60,117", "11": "275,506,265,633,19,526,382,349,82,355,60", "12": "275,506,430,5,294,509,412,362,526,355,60", "13": "113,203,369,48,5,19,134,526,362,355,60", "14": "291,506,290,131,349,362,19,294,85,60,343", "15": "113,290,506,342,509,294,362,526,85,343,60", 
                    "16": "409,369,36,131,362,19,349,382,60,343,293", "17": "524,369,506,131,134,362,349,353,19,117,60", "18": "524,506,203,430,349,362,526,353,343,85,60", "19": "113,131,31,290,43,509,19,362,412,60,117", "20": "409,405,506,36,14,509,344,362,355,60,85", "21": "409,131,430,48,526,19,353,362,343,60,85", "22": "275,369,506,342,373,509,19,362,293,135,355", "23": "230,20,506,427,19,373,353,526,14,117,60", 
                    "24": "524,36,519,369,294,19,412,362,355,60,85", "25": "275,506,430,131,19,362,353,412,504,60,355", "26": "49,36,430,234,526,349,362,19,504,85,60", "27": "520,369,506,313,353,19,349,362,590,60,293", "28": "524,131,150,245,506,349,412,353,362,314,355", "29": "275,131,407,430,362,509,353,349,60,85,355", "30": "409,20,369,430,303,509,19,362,60,355,85", "31": "275,519,131,316,412,542,19,509,355,117,60", 
                    "32": "524,430,36,234,19,353,412,294,343,60,85", "33": "409,430,131,506,353,19,412,509,355,60,85", "34": "409,36,430,5,412,294,353,362,60,343,85", "35": "520,519,5,430,412,526,294,362,60,355,85", "36": "524,407,506,131,362,412,353,349,135,60,355", "37": "524,265,220,506,353,362,599,349,343,85,60", "38": "49,290,427,342,349,664,526,362,85,343,60", "39": "352,290,430,519,362,526,294,19,343,85,60", 
                    "40": "524,20,430,260,313,19,353,362,267,60,343"},
        "captain": {
                    "0": 349, "1": 355, "2": 60, "3": 60, "4": 355, "5": 60, "6": 349, "7": 349, "8": 412, "9": 355, "10": 349,
                    "11": 19, "12": 355, "13": 355, "14": 349, "15": 343, "16": 349, "17": 349, "18": 60, "19": 19, "20": 355, 
                    "21": 343, "22": 355, "23": 373, "24": 362, "25": 362, "26": 19, "27": 349, "28": 349, "29": 355, "30": 355, 
                    "31": 355, "32": 60, "33": 85, "34": 85, "35": 355, "36": 349, "37": 349, "38": 349, "39": 60, "40": 362,
        },
        "vice_captain": {
                        "0": 353, "1": 362, "2": 19, "3": 412, "4": 60, "5": 430, "6": 343, "7": 19, "8": 60, "9": 412, "10": 353, 
                        "11": 60, "12": 509, "13": 526, "14": 294, "15": 362, "16": 343, "17": 353, "18": 362, "19": 412, "20": 60, 
                        "21": 19, "22": 373, "23": 353, "24": 412, "25": 355, "26": 362, "27": 362, "28": 412, "29": 349, "30": 60, 
                        "31": 60, "32": 85, "33": 355, "34": 60, "35": 60, "36": 355, "37": 60, "38": 60, "39": 19, "40": 343},
        "bench": {
            "0": "28,178,5,538", "1": "524,226,5,178", "2": "524,293,5,313", "3": "524,8,234,33", "4": "524,382,157,5", "5": "524,131,203,193", "6": "524,415,203,245", "7": "546,382,27,558", "8": "301,36,220,33", "9": "524,5,197,308", 
            "10": "28,203,220,538", "11": "263,5,516,160", "12": "152,590,131,112", "13": "524,558,298,308", "14": "113,369,32,526", "15": "28,5,19,178", "16": "524,526,528,419", "17": "597,178,538,139", "18": "113,19,29,83", "19": "361,355,260,473",
            "20": "524,5,178,308", "21": "113,36,20,308", "22": "148,134,31,245", "23": "28,228,473,490", "24": "28,382,29,602", "25": "524,427,33,602", "26": "409,220,168,29", "27": "291,664,20,419", "28": "28,8,178,308", "29": "524,382,36,29",
            "30": "520,703,689,519", "31": "263,20,245,308", "32": "498,388,393,473", "33": "28,526,5,688", "34": "49,392,545,311", "35": "116,501,528,42", "36": "291,290,382,532", "37": "28,412,203,36", "38": "524,5,316,308", "39": "524,12,377,150", "40": "230,225,220,308"
        }
    }
    
@pytest.fixture(scope="module")
def league_weekly_transfer():
    return {"1086398": {"element_in": [355], "element_out": [343]}, "98120": {"element_in": [294], "element_out": [362]}, 
     "175583": {"element_in": [597], "element_out": [352]}, "1070898": {"element_in": [193], "element_out": [135]},
     "18103": {"element_in": [355], "element_out": [8]}, "32133": {"element_in": [355], "element_out": [415]}, 
     "563294": {"element_in": [355], "element_out": [343]}, "5748350": {"element_in": [509], "element_out": [303]}, 
     "1145568": {"element_in": [294], "element_out": [353]}, "4805585": {"element_in": [430], "element_out": [342]}, 
     "6380329": {"element_in": [117], "element_out": [135]}, "4050576": {"element_in": [355], "element_out": [558]}, 
     "24268": {"element_in": [412], "element_out": [353]}, "1172179": {"element_in": [427], "element_out": [20]}, 
     "3829907": {"element_in": [349], "element_out": [12]}, "150479": {"element_in": [355], "element_out": [343]}, 
     "4275778": {"element_in": [355], "element_out": [590]}, "669180": {"element_in": [316], "element_out": [703]}, 
     "2873232": {"element_in": [294], "element_out": [526]}, "124922": {"element_in": [355], "element_out": [246]}, 
     "4917316": {"element_in": [294], "element_out": [526]}, "456141": {"element_in": [355], "element_out": [343]}, 
     "7572179": {"element_in": [362], "element_out": [50]}, "973439": {"element_in": [349], "element_out": [308]}, 
     "6862778": {"element_in": [349], "element_out": [557]}, "634702": {"element_in": [19], "element_out": [14]}, 
     "4834604": {"element_in": [294], "element_out": [344]}, "8020458": {"element_in": [362], "element_out": [557]}, 
     "4027607": {"element_in": [343], "element_out": [135]}, "700024": {"element_in": [617], "element_out": [33]}, 
     "5019432": {"element_in": [504], "element_out": [14]}, "483899": {"element_in": [597], "element_out": [101]}, 
     "1714236": {"element_in": [430], "element_out": [290]}, "4858268": {"element_in": [412], "element_out": [516]}, 
     "4063268": {"element_in": [430], "element_out": [377]}, "3261888": {"element_in": [689], "element_out": [12]}, 
     "2538570": {"element_in": [294], "element_out": [570]}, "4875945": {"element_in": [355], "element_out": [415]}, 
     "3395657": {"element_in": [362], "element_out": [134]}, "1118096": {"element_in": [355], "element_out": [60]}, 
     "1551370": {"element_in": [294], "element_out": [557]}, "2543360": {"element_in": [362], "element_out": [344]}, 
     "4905008": {"element_in": [294], "element_out": [353]}, "1319649": {"element_in": [504], "element_out": [378]}, 
     "5660289": {"element_in": [509], "element_out": [14]}, "805203": {"element_in": [412], "element_out": [353]}, 
     "6195467": {"element_in": [236], "element_out": [526]}, "2800001": {"element_in": [407], "element_out": [220]}, 
     "53088": {"element_in": [355], "element_out": [85]}, "1380760": {"element_in": [430], "element_out": [197]}, 
     "852560": {"element_in": [509], "element_out": [344]}, "3107465": {"element_in": [355], "element_out": [135]}, 
     "4116225": {"element_in": [664], "element_out": [526]}, "321602": {"element_in": [504], "element_out": [516]}, 
     "6956822": {"element_in": [396], "element_out": [526]}, "3722386": {"element_in": [437], "element_out": [415]}}

@pytest.fixture(scope = "module")
def league_participants():
    return [{'id': 37378749, 'event_total': 36, 'player_name': 'Emmanuel Okedele', 'rank': 1, 'last_rank': 2, 'rank_sort': 1, 'total': 1100, 'entry': 98120, 'entry_name': 'Potters Touch'},\
    {'id': 38949786, 'event_total': 26, 'player_name': 'Adedapo Adedire', 'rank': 2, 'last_rank': 3, 'rank_sort': 2, 'total': 1088, 'entry': 1086398, 'entry_name': 'Sylarexx Fc'}, \
    {'id': 37386221, 'event_total': 19, 'player_name': 'Uncle Buzzey', 'rank': 3, 'last_rank': 1, 'rank_sort': 3, 'total': 1084, 'entry': 293449, 'entry_name': 'Coyg'},\
    {'id': 62483704, 'event_total': 28, 'player_name': 'Star Boy', 'rank': 4, 'last_rank': 4, 'rank_sort': 4, 'total': 1058, 'entry': 456141, 'entry_name': 'Akaza Dono'}, \
    {'id': 47033862, 'event_total': 15, 'player_name': 'Martins Omoniyi', 'rank': 5, 'last_rank': 5, 'rank_sort': 5, 'total': 1044, 'entry': 3572212, 'entry_name': 'Bulldozers FC'},\
    {'id': 37391869, 'event_total': 30, 'player_name': 'moyosola junior', 'rank': 6, 'last_rank': 8, 'rank_sort': 6, 'total': 1041, 'entry': 32133, 'entry_name': 'olympique mayonnaise'}, \
    {'id': 67447801, 'event_total': 19, 'player_name': 'Progress Akintade', 'rank': 7, 'last_rank': 6, 'rank_sort': 7, 'total': 1038, 'entry': 4145862, 'entry_name': 'PROGRESSS'}, \
    {'id': 45353356, 'event_total': 24, 'player_name': 'coker sunkanmi', 'rank': 8, 'last_rank': 7, 'rank_sort': 8, 'total': 1037, 'entry': 4834604, 'entry_name': 'Sujeyinc'}, \
    {'id': 37437413, 'event_total': 25, 'player_name': 'Vicapo Awosika', 'rank': 9, 'last_rank': 10, 'rank_sort': 9, 'total': 1033, 'entry': 124922, 'entry_name': 'Vicapo FC'}, \
    {'id': 39299443, 'event_total': 31, 'player_name': 'Femi Sobodu', 'rank': 10, 'last_rank': 11, 'rank_sort': 10, 'total': 1032, 'entry': 973439, 'entry_name': 'Chronicles Of VARnia'}, \
    {'id': 53769740, 'event_total': 22, 'player_name': 'Gbemileke David', 'rank': 11, 'last_rank': 9, 'rank_sort': 11, 'total': 1027, 'entry': 4917316, 'entry_name': 'Aare Ika CF'}, \
    {'id': 37598256, 'event_total': 24, 'player_name': 'John Dere', 'rank': 12, 'last_rank': 14, 'rank_sort': 12, 'total': 998, 'entry': 4858268, 'entry_name': 'Lord Madara'}, \
    {'id': 43227690, 'event_total': 8, 'player_name': 'Matthew Omoniyi', 'rank': 13, 'last_rank': 12, 'rank_sort': 13, 'total': 997, 'entry': 5493191, 'entry_name': 'FPL Juggernaut'}, \
    {'id': 51006805, 'event_total': 16, 'player_name': 'Abideen Ayangbemi', 'rank': 14, 'last_rank': 13, 'rank_sort': 14, 'total': 992, 'entry': 483899, 'entry_name': 'Dafuq FC'}, \
    {'id': 37627137, 'event_total': 24, 'player_name': 'Chukwudi Onyewuchi', 'rank': 15, 'last_rank': 16, 'rank_sort': 15, 'total': 990, 'entry': 2929610, 'entry_name': 'Zups!'}, \
    {'id': 38275547, 'event_total': 43, 'player_name': 'Ayodeji Omoniyi', 'rank': 16, 'last_rank': 19, 'rank_sort': 16, 'total': 980, 'entry': 34174, 'entry_name': 'God Abeg…'}, \
    {'id': 40102684, 'event_total': 3, 'player_name': 'chisom ndianefo', 'rank': 17, 'last_rank': 15, 'rank_sort': 17, 'total': 973, 'entry': 5144052, 'entry_name': 'Eventually!'}, \
    {'id': 47799952, 'event_total': 31, 'player_name': 'Iam KayY', 'rank': 18, 'last_rank': 18, 'rank_sort': 18, 'total': 968, 'entry': 1118096, 'entry_name': 'KayY'}, \
    {'id': 37475582, 'event_total': 28, 'player_name': 'Uncle Tunes', 'rank': 19, 'last_rank': 20, 'rank_sort': 19, 'total': 964, 'entry': 805203, 'entry_name': 'Shikamaru Fergie FC'}, \
    {'id': 52412247, 'event_total': 17, 'player_name': 'Oyeniyi Okusi', 'rank': 20, 'last_rank': 17, 'rank_sort': 20, 'total': 958, 'entry': 1551370, 'entry_name': 'Manchachi'}, \
    {'id': 48580891, 'event_total': 14, 'player_name': 'Emmanuel Nnaemeka', 'rank': 21, 'last_rank': 21, 'rank_sort': 21, 'total': 902, 'entry': 5104192, 'entry_name': 'Emiradofc'}, \
    {'id': 37612408, 'event_total': 33, 'player_name': 'Peterclever Nnodim', 'rank': 22, 'last_rank': 23, 'rank_sort': 22, 'total': 884, 'entry': 1552881, 'entry_name': 'Cashflow FC'}, \
    {'id': 43398060, 'event_total': 13, 'player_name': 'Reginald Maduka', 'rank': 23, 'last_rank': 22, 'rank_sort': 23, 'total': 878, 'entry': 5509203, 'entry_name': 'Bullion van'}]

@pytest.fixture(scope = "module")
def league_fill_fixture():
    return [{'id': 37378749, 'event_total': 36, 'player_name': 'Emmanuel Okedele', 'rank': 1, 'last_rank': 2, 'rank_sort': 1, 'total': 1100, 'entry': 98120, 'entry_name': 'Potters Touch'},\
    {'id': 38949786, 'event_total': 26, 'player_name': 'Adedapo Adedire', 'rank': 2, 'last_rank': 3, 'rank_sort': 2, 'total': 1088, 'entry': 1086398, 'entry_name': 'Sylarexx Fc'}, \
    {'id': 37386221, 'event_total': 19, 'player_name': 'Uncle Buzzey', 'rank': 3, 'last_rank': 1, 'rank_sort': 3, 'total': 1084, 'entry': 293449, 'entry_name': 'Coyg'}]

@pytest.fixture(scope="module")
def filepath():
    return realpath(REPORT_DIR)

@pytest.fixture(scope="module")
def participant():
    return int(98120)

@pytest.fixture(scope="module")
def h2h_league():
    return int(1089000)

@pytest.fixture(scope="module")
def classic_league():
    return int(1088941)

@pytest.fixture(scope="module")
def gw_fixture():
    return int(8)

@pytest.fixture(scope="module")
def span_fixture():
    return [8,10,3]

@pytest.fixture(scope="module")
def values():
    return  [1.0, 2.0, 17, 3.0, 26, 2.0, 1, 10]

@pytest.fixture(scope="module")
def transfer_obj():
    return {"element_in": 5, 'element_in_cost': 76, 
           "element_out": 19, "element_out_cost": 11,
           "entry": 98120, "event": 12, "time": 2300}

