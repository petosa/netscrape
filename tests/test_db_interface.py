# coding=utf-8

from time import sleep

import pytest

from pymongo import MongoClient

from netscrape.daemon import daemon
from netscrape.db_interface import db_interface


def interface():
    client = MongoClient("127.0.0.1")
    system_db = "test-sys"
    data_db = "test-data"
    schedule_col = "test-schedule"
    return db_interface(client, system_db, data_db, schedule_col)

@pytest.fixture(autouse=True)
def setup():
    interface().nuke()
    yield
    interface().nuke()

def test_empty_schedule():
    assert interface().get_schedule() == []

def test_no_navigators_queued():
    assert interface().get_next() == None

def test_simple_put():
    d = daemon(interface())
    interface().put_navigator({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": False,
        "schema": False,
        "function": "output = \"Answer\""
    })
    sleep(1)
    assert len(interface().get_schedule()) == 1
    assert interface().get_newest_data("ArizonaIcedTea") == None
    assert len(interface().get_history("ArizonaIcedTea")) == 0
    d.stop()

def test_simple_put_saved():
    d = daemon(interface())
    assert len(interface().get_history("ArizonaIcedTea")) == 0
    interface().put_navigator({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": True,
        "schema": False,
        "function": "output = \"Answer\""
    })
    sleep(1)
    assert len(interface().get_schedule()) == 1
    assert interface().get_newest_data("ArizonaIcedTea") != None
    assert len(interface().get_history("ArizonaIcedTea")) == 1
    d.stop()

def test_multiple_times():
    d = daemon(interface())
    assert len(interface().get_history("ArizonaIcedTea")) == 0
    interface().put_navigator({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 5,
        "save": True,
        "schema": False,
        "function": "output = \"Answer\""
    })
    sleep(1)
    assert len(interface().get_schedule()) == 1
    assert interface().get_newest_data("ArizonaIcedTea") != None
    assert len(interface().get_history("ArizonaIcedTea")) == 5
    d.stop()

def test_utility():
    d = daemon(interface())
    assert len(interface().get_history("ArizonaIcedTea")) == 0
    interface().put_navigator({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 5,
        "save": True,
        "schema": False,
        "function": "output = \"Answer\""
    })
    sleep(1)
    interface().put_navigator({
        "name": "SnapplePeachTea",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": True,
        "schema": False,
        "function": "output = utility.get_history(\"ArizonaIcedTea\")"
    })
    sleep(.1)
    assert len(interface().get_newest_data("SnapplePeachTea")["data"]) == 5
    d.stop()

def test_data_added():
    assert len(interface().get_schedule()) == 0
