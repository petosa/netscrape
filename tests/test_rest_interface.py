# coding=utf-8

import os
import shutil
import signal
import subprocess
from time import sleep

import pytest

from flask import Flask
from multiprocessing import Process
from pymongo import MongoClient

from netscrape import server
from netscrape.daemon import daemon
from netscrape.db_interface import db_interface


def get_interface():
    client = MongoClient("127.0.0.1:4000")
    system_db = "test-sys"
    data_db = "test-data"
    schedule_col = "test-schedule"
    return db_interface(client, system_db, data_db, schedule_col)

@pytest.fixture(autouse=True)
def setup():

    def launch_server(app, interface):
        server.start(app, interface)

    def launch_mongo():
        subprocess.Popen("mongod --dbpath \"" + mongo_dir + "\" --port 4000", shell=True)

    mongo_dir = os.path.dirname(os.path.realpath(__file__)) + "/mongo-data"
    if not os.path.exists(mongo_dir):
        os.mkdir(mongo_dir)

    app = Flask(__name__)
    interface = get_interface()
    daemon(interface)
    mongo_thread = Process(target=launch_mongo)
    mongo_thread.daemon = True
    mongo_thread.start()
    server_thread = Process(target=launch_server, args=[app, interface])
    server_thread.daemon = True
    server_thread.start()
    yield

    mongo_thread.terminate()
    mongo_thread.join()
    server_thread.terminate()
    server_thread.join()
    os.kill(int(subprocess.check_output(["pidof", "-s", "mongod"])), signal.SIGKILL)
    shutil.rmtree(mongo_dir)
    interface.close_stream()

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
    interface.put_navigator({
        "name": "Shiny_navigator",
        "description": "Tea",
        "next": 0,
        "every": 1,
        "times": 1,
        "save": True,
        "schema": False,
        "function": "output = \"Some scraped content.\""
    })
    sleep(1)
    assert (len(interface.get_schedule()) == 1)
    assert(interface.get_navigator("Shiny_navigator") != None)
    assert(interface.get_newest_data("Shiny_navigator") != None)
    assert(interface.get_newest_data("Shiny_navigator")["data"] == "Some scraped content.")
    assert(len(interface.get_history("Shiny_navigator")) == 1)
    # Update test
    assert(interface.update_navigator("Shiny_navigator", {"times": 3}) == 1)
    sleep(1)
    assert(len(interface.get_history("Shiny_navigator")) == 4)
    # get_newest_data actually returns newest data test
    newest_time = interface.get_newest_data("Shiny_navigator")["creation_date"]
    for item in interface.get_history("Shiny_navigator"):
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
        "function": "output = utility.get_newest_data(\"Shiny_navigator\")[\"data\"]"
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
        "function": "output = utility.get_history(\"Shiny_navigator\")"
    })
    sleep(1)
    assert(len(interface.get_newest_data("Gold_navigator")["data"]) == 4)
    # Test rename
    assert(interface.update_navigator("Gold_navigator", {"name": "Bronze_navigator"}) == 1)
    assert(len(interface.get_newest_data("Bronze_navigator")["data"]) == 4)
    assert(len(interface.get_history("Bronze_navigator")) == 1)
    assert(len(interface.get_history("Gold_navigator")) == 0)
    # Test delete
    assert(interface.delete_navigator("Shiny_navigator") == 1)
    assert(interface.delete_navigator("Iron_navigator") == 1)
    assert(interface.delete_navigator("Bronze_navigator") == 1)
    assert (interface.get_schedule() == [])
    assert (interface.get_history("Shiny_navigator") == [])
    assert (interface.get_history("Iron_navigator") == [])
    assert (interface.get_history("Bronze_navigator") == [])
    # Clean up
    interface.close_stream()
