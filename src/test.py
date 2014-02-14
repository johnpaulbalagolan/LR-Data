# -*- coding: utf-8 -*-

from helpers.tasks import getTaskFunction
from celeryconfig import config
import requests
import unittest
import urllib
import traceback
from pprint import pprint

class DisplayTests(unittest.TestCase):
    def test_types(self):
        test_docs = [
            "http://www.khanacademy.org/video/dependent-probability-example-1?playlist=Probability",
            "http://illuminations.nctm.org/LessonDetail.aspx?ID=U159",
            "http://carrefour-numerique.cite-sciences.fr/ressources/flash/anims/url/cyberbase08_home.html",
            "http://www.shodor.org/interactivate/lessons/FindingRemaindersinPascal/",
            "http://www.cmhouston.org/attachments/files/1690/CaterpillarMeasure.pdf",
            "http://www2.edu.fi/materiaalipankki/showfile.php?id=158&file=158_lankarulla4.jpg",
        ]

        for doc_id in test_docs:
            try:
                print ""
                print "============== %s ==============" % doc_id


                url = "https://node01.public.learningregistry.net/obtain?"+urllib.urlencode({ "request_id": doc_id})
                print url
                request = requests.get(url)
                obtainResponse = request.json()


                for data in obtainResponse['documents'][0]['document']:
                    if(data['resource_data_type'] == 'metadata'):
                        doc = getTaskFunction(config, 'validate')(data, config, False)

                        break

            except Exception as ex:
                print "Failed to load: "+url
                traceback.print_exc()

if __name__ == "__main__":
    unittest.main()
