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

def test_nothing():
    return True
