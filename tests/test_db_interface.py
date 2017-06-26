# coding=utf-8

from time import sleep

import pytest

from pymongo import MongoClient

from netscrape.daemon import daemon
from netscrape.db_interface import db_interface


def get_interface():
    client = MongoClient("127.0.0.1")
    system_db = "test-sys"
    data_db = "test-data"
    schedule_col = "test-schedule"
    return db_interface(client, system_db, data_db, schedule_col)

@pytest.fixture(autouse=True)
def setup():
    interface = get_interface()
    interface.nuke()
    daemon(interface)

def test_simple_get():
    interface = get_interface()
    assert(interface.get_schedule() == [])
    oid = (interface.put_navigator({
        "name": "ArizonaIcedTea",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": False,
        "schema": False,
        "function": "output = ['Not', 'bad']"
    }))
    sleep(1)
    sched = interface.get_schedule()
    assert (len(sched) == 1)
    assert(sched[0]["times"] == 0)
    assert(sched[0]["_id"]["$oid"] == oid)
    assert(sched[0]["name"] == "ArizonaIcedTea")
    assert(sched[0]["description"] == "Tea")
    assert(sched[0]["every"] == 1)
    assert(sched[0]["save"] == False)
    assert(interface.get_navigator("ArizonaIcedTea") != None)

    assert(interface.delete_navigator("ArizonaIcedTea") == 1)
    assert (interface.get_schedule() == [])
    interface.close_stream()

def test_simple_use_case():
    interface = get_interface()

    # Simple put with data access test
    assert(interface.get_schedule() == [])
    assert (interface.get_newest_data("Metal_navigator") == None)
    assert (len(interface.get_history("Metal_navigator")) == 0)
    interface.put_navigator({
        "name": "Metal_navigator",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": True,
        "schema": False,
        "function": "output = \"Some scraped content.\""
    })
    assert (len(interface.get_schedule()) == 1)
    assert(interface.get_navigator("Metal_navigator") != None)
    sleep(1)
    assert(interface.get_newest_data("Metal_navigator") != None)
    assert(interface.get_newest_data("Metal_navigator")["data"] == "Some scraped content.")
    sleep(1)
    assert(len(interface.get_history("Metal_navigator")) == 1)
    # Update test
    assert(interface.update_navigator("Metal_navigator", {"times": 3}) == 1)
    sleep(1)
    assert(len(interface.get_history("Metal_navigator")) == 4)
    # get_newest_data actually returns newest data test
    newest_time = interface.get_newest_data("Metal_navigator")["creation_date"]
    for item in interface.get_history("Metal_navigator"):
        assert(item["creation_date"] <= newest_time)
    # get_newest_data utility function in navigator test
    interface.put_navigator({
        "name": "Iron_navigator",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": True,
        "schema": False,
        "function": "output = utility.get_newest_data(\"Metal_navigator\")[\"data\"]"
    })
    sleep(1)
    assert (len(interface.get_schedule()) == 2)
    assert (interface.get_newest_data("Iron_navigator") != None)
    # get_history utility function in navigator test
    assert (interface.get_newest_data("Iron_navigator")["data"] == "Some scraped content.")
    interface.put_navigator({
        "name": "Gold_navigator",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": True,
        "schema": False,
        "function": "output = utility.get_history(\"Metal_navigator\")"
    })
    sleep(1)
    assert(len(interface.get_newest_data("Gold_navigator")["data"]) == 4)
    # Test rename
    assert(interface.update_navigator("Gold_navigator", {"name": "Bronze_navigator"}) == 1)
    assert(len(interface.get_newest_data("Bronze_navigator")["data"]) == 4)
    assert(len(interface.get_history("Bronze_navigator")) == 1)
    assert(len(interface.get_history("Gold_navigator")) == 0)
    # Test delete
    assert(interface.delete_navigator("Metal_navigator") == 1)
    assert(interface.delete_navigator("Iron_navigator") == 1)
    assert(interface.delete_navigator("Bronze_navigator") == 1)
    assert (interface.get_schedule() == [])
    assert (interface.get_history("Metal_navigator") == [])
    assert (interface.get_history("Iron_navigator") == [])
    assert (interface.get_history("Bronze_navigator") == [])
    # Clean up
    interface.close_stream()
