from base import PayloadSchemaParser
from lxml import etree

class LomParser(PayloadSchemaParser):
    def _parse(self, doc, envelope, mapping):

        base_xpath = "//lom:lom/lom:general/lom:{0}/lom:string[@language='en-us' or @language='en-gb' or @language='en']"
        namespaces = {
            "lom": "http://ltsc.ieee.org/xsd/LOM"
            }
        dom = etree.fromstring(envelope['resource_data'])

        found_titles = dom.xpath(base_xpath.format('title'), namespaces=namespaces)
        found_description = dom.xpath(base_xpath.format('description'), namespaces=namespaces)
        found_keyword = dom.xpath(base_xpath.format('keyword'), namespaces=namespaces)


        if found_titles:
            doc['title'] = found_titles.pop().text

        if found_description:
            doc['description'] = found_description.pop().text

        doc['keys'].extend([i.text for i in found_titles])
        doc['keys'].extend([i.text for i in found_description])
        doc['keys'].extend([i.text for i in found_keyword])

