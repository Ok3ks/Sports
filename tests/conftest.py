import pytest
from src.paths import REPORT_DIR
import os
from os.path import join,realpath

from src.utils import Participant


@pytest.fixture(scope="module")
def league_fixture():
    return int(1088941)

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

