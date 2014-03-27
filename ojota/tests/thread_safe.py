import os

from threading import Thread
from time import sleep
from unittest.case import TestCase

from ojota import Ojota, current_data_code
from ojota.base import set_data_source, get_current_data_code
from ojota.cache import DummyCache


class Person(Ojota):
    pk_field = "id"
    cache = DummyCache()


class OjotaTest(TestCase):
    def setUp(self):
        TestCase.setUp(self)
        file_path = (os.path.dirname(os.path.abspath(__file__)))
        set_data_source(os.path.join(file_path, "data"))

    def test_multiprocess(self):

        def thread1_test(data_code):
            current_data_code(data_code)
            print "data code 1", get_current_data_code()
            sleep(1)
            print "data code 2", get_current_data_code()

        def thread2_test(data_code):
            current_data_code(data_code)
            print "data code 3", get_current_data_code()

        p1 = Thread(target=thread1_test, args=('', ))
        p1.start()

        p2 = Thread(target=thread2_test, args=('alternative', ))
        p2.start()
        p1.join()
        p2.join()

