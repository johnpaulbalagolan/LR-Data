from base import PayloadSchemaParser
from lxml import etree

class NsdlDcParser(PayloadSchemaParser):
    def _parse(self, doc, envelope, mapping):

        #parse the resource_data into an XML dom object
        dom = etree.fromstring(envelope['resource_data'])
        #dictionary containing XML namespaces and their prefixes
        dc_namespaces = {
            "nsdl_dc": "http://ns.nsdl.org/nsdl_dc_v1.02/",
             "dc": "http://purl.org/dc/elements/1.1/",
             "dct": "http://purl.org/dc/terms/"
         }
        # run an XPath query againt the dom object that pulls out all the document titles
        standards = dom.xpath('/nsdl_dc:nsdl_dc/dct:conformsTo',
                           namespaces=dc_namespaces)
        # extract a set of all the titles from the DOM elements
        standards = {elm.text[elm.text.rfind('/') + 1:].lower() for elm in standards}
        standards = (mapping.get(s, [s]) for s in standards)

        final_standards = []
        for ids in standards:
            for s in ids:
                final_standards.append(s)

        title = dom.xpath('/nsdl_dc:nsdl_dc/dc:title', namespaces=dc_namespaces)
        if title:
            doc['title'] = title.pop().text

        description = dom.xpath('/nsdl_dc:nsdl_dc/dc:description', namespaces=dc_namespaces)
        if description:
            doc['description'] = description.pop().text

        doc['standards'] = final_standards


        subjects = dom.xpath('/nsdl_dc:nsdl_dc/dc:subject', namespaces=dc_namespaces)
        doc['keys'].extend([s.text for s in subjects])

        grades = dom.xpath('/nsdl_dc:nsdl_dc/dct:educationLevel', namespaces=dc_namespaces)
        doc['grades'].extend([g.text.lower().replace('grade ', '') for g in grades])
