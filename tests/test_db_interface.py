from time import sleep

import pytest
from pymongo import MongoClient

from skython.db_interface import db_interface

@pytest.fixture(autouse=True)
def setup():
    interface().nuke()
    yield
    interface().nuke()

def interface():
    client = MongoClient("127.0.0.1")
    system_db = "test"
    schedule_col = "catalog"
    return db_interface(client, system_db, schedule_col)

def test_empty_schedule():
    assert interface().get_catalog() == []

def test_put_and_delete():
    assert len(interface().get_catalog()) == 0
    interface().put_lambda({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "args": {},
        "function": "output = \"Answer\""
    })
    sleep(1)
    assert len(interface().get_catalog()) == 1
    assert(interface().delete_lambda("ArizonaIcedTea"))
    assert len(interface().get_catalog()) == 0

def test_function_simple():
    assert(interface().run_function("output = 5", {}) == 5)

def test_function_advanced():
    assert(interface().run_function("output = int(val1) + int(val2)", {"val1": 1, "val2": 2}) == 3)

def test_function_from_catalog_int():
    assert len(interface().get_catalog()) == 0
    interface().put_lambda({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "args": {"flavor" : "A cool value"},
        "function": "output = [flavor]"
    })
    sleep(1)
    assert len(interface().get_catalog()) == 1
    lam = interface().get_lambda("ArizonaIcedTea")
    assert(interface().run_function(lam["function"], {"flavor": "1"}) == [1])

def test_function_from_catalog_str():
    assert len(interface().get_catalog()) == 0
    interface().put_lambda({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "args": {"flavor" : "A cool value"},
        "function": "output = [flavor]"
    })
    sleep(1)
    assert len(interface().get_catalog()) == 1
    lam = interface().get_lambda("ArizonaIcedTea")
    assert(interface().run_function(lam["function"], {"flavor": "\"cat\""}) == ["cat"])

def test_function_from_catalog_dict():
    assert len(interface().get_catalog()) == 0
    interface().put_lambda({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "args": {"flavor" : "A cool value"},
        "function": "output = [flavor]"
    })
    sleep(1)
    assert len(interface().get_catalog()) == 1
    lam = interface().get_lambda("ArizonaIcedTea")
    assert(interface().run_function(lam["function"], {"flavor": "{\"val\": 1}"}) == [{"val":1}])

def test_function_from_catalog_fail():
    assert len(interface().get_catalog()) == 0
    interface().put_lambda({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "args": {"flavor" : "A cool value"},
        "function": "output = [flavor]"
    })
    sleep(1)
    assert len(interface().get_catalog()) == 1
    lam = interface().get_lambda("ArizonaIcedTea")
    assert(interface().run_function(lam["function"], {"flavor": "Invalid thing"}) == "Exception in function: Expecting value: line 1 column 1 (char 0)")