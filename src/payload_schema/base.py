import traceback
import json

class PayloadSchemaParser:
    def parse(self, envelope, standardsMapping):

        document = self.base_document(envelope)

        try:
            self._parse(document, envelope, standardsMapping)
        except Exception as ex:
            print "Failed to parse"
            traceback.print_exc()

        return document

    def base_document(self, envelope):

        url = envelope['resource_locator']

        return {
            'title': url,
            'description': '',
            'publisher': self.identify_publisher(envelope),
            'url': url,
            'keys': envelope.get('keys', []),
            'hasScreenshot': False,
            'grades': [ i[6:] for i in envelope.get('keys', []) if i.lower()[:6] == 'grade ' ],
        }

    def identify_publisher(self, envelope):

        identity = envelope['identity']

        if 'submitter' in identity and 'owner' in identity \
            and identity['submitter'] and identity['owner'] \
            and identity['submitter'] != identity['owner']:

            publisher = "{0} on behalf of {1}".format(identity['submitter'], identity['owner'])

        elif 'submitter' in identity and identity['submitter']:
            publisher = identity['submitter']

        elif 'owner' in identity:
            publisher = idenity['owner']

        else:
            publisher = ''

        return publisher


    def _loadJSONResourceData(self, envelope):
        """ If resource_data is a string, convert it to a JSON object """

        data = envelope.get('resource_data', {})

        if self.is_string(data):
            data = json.loads(data)

        return data

    # helper function to cope with string vs unicode
    def is_string(self, value):
        return isinstance(value, str) or isinstance(value, unicode)

