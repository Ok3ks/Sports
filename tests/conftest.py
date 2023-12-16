import pytest
from src.paths import REPORT_DIR
import os
from os.path import join,realpath

@pytest.fixture(scope="module")
def create_league():
    return

@pytest.fixture(scope="module")
def filepath():
    return realpath(REPORT_DIR)

@pytest.fixture(scope="module")
def player():
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
def diff_gw_fixture():
    return [8,10]

@pytest.fixture(scope="module")
def values():
    return  [1.0, 2.0, 17, 3.0, 26, 2.0, 1, 10]

@pytest.fixture(scope="module")
def transfer_obj():
    return {"element_in": 5, 'element_in_cost': 76, 
           "element_out": 19, "element_out_cost": 11,
           "entry": 98120, "event": 12, "time": 2300}

