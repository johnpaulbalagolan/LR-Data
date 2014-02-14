# -*- coding: utf-8 -*-

from helpers.tasks import getTaskFunction
from celeryconfig import config
import requests
import unittest
from pprint import pprint
import importlib

class DisplayTests(unittest.TestCase):
    def test_types(self):
        test_docs = [
            "http://www.khanacademy.org/video/dependent-probability-example-1?playlist=Probability",

        ]

        for doc_id in test_docs:
            base_url = "http://sandbox.learningregistry.org/obtain?request_id="+doc_id
            data = requests.get(url).json()

            data = data['documents'][0]['document'][0]

            getTaskFunction(config, 'validation')(data, config, False)

if __name__ == "__main__":
    unittest.main()
