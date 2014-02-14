from base import PayloadSchemaParser

import urlparse

class JsonLdParser(PayloadSchemaParser):
    def _parse(self, doc, envelope, mapping):
        doc.update({
            'standards': [],
            'accessMode': [],
            'mediaFeatures': [],
            'hasScreenshot': True,
        })


        payload_graph = envelope.get('resource_data', {}).get('@graph')
        if not payload_graph:
            payload_graph = [envelope.get('resource_data', {})]


        graph_data = self.process_json_ld_graph(payload_graph, mapping)

        for k in ['keys', 'standards', 'accessMode', 'mediaFeatures']:
            doc[k].extend(graph_data.get(k, []))

        for k in ['title', 'description', 'publisher']:
            if k not in doc and k in graph_data:
                doc[k] = graph_data[k]

    def process_json_ld_graph(self, graph, mapping):
        data = {}
        keys = []
        standards = []
        media_features = []
        access_mode = []
        for node in graph:
            keys.extend(self.handle_keys_json_ld(node))
            standards.extend(self.handle_standards_json_ld(node, mapping))
            if 'accessMode' in node:
                accessMode = node['accessMode']
                if isinstance(accessMode, list):
                    access_mode.extend(accessMode)
                else:
                    access_mode.append(accessMode)
            for feature in ['accessibilityFeature', 'mediaFeature']:
                if  feature in node:
                    mediaFeature = node[feature]
                    if isinstance(mediaFeature, list):
                        media_features.extend(mediaFeature)
                    else:
                        media_features.append(mediaFeature)
            if '@type' in node:
                t = node['@type']
                if '/' in t:
                    type_value = t[t.rfind('/')+1:].lower()
                    keys.append(type_value)
                else:
                    keys.append(t)
            if 'name' in node and 'title' not in data:
                data['title'] = self.get_first_or_value(node, 'name', lambda x: isinstance(x, str) or isinstance(x, unicode))
            if "description" in node and 'description' not in data:
                data['description'] = self.get_first_or_value(node, 'description', lambda x: isinstance(x, str) or isinstance(x, unicode))
            if 'publisher' in node:
                pub = self.get_first_or_value(node, 'publisher', lambda x: isinstance(x, str) or isinstance(x, unicode))
                if isinstance(pub, dict):
                    data['publisher'] = pub.get('name', '')
                else:
                    data['publisher'] = pub
        data['keys'] = keys
        data['standards'] = standards
        data['accessMode'] = set(access_mode)
        data['mediaFeatures'] = set(media_features)

        return data

    def get_first_or_value(self, data, key, test):
        if test(data[key]):
            return data[key]
        elif isinstance(data[key], list):
            return data[key].pop()

    def handle_standards_json_ld(self, node, mapping):
        standards = []
        if 'educationalAlignment' in node:
            alignments = (n['targetName'] for n in node['educationalAlignment'] if 'targetName' in n and n.get('educationalFramework','').lower().strip() == "common core state standards")

            alignments = (n['targetName']
                for n in node['educationalAlignment'] \
                    if 'targetName' in n \
                        and ( \
                            (isinstance(n.get('educationalFramework',''), str) and n.get('educationalFramework','').lower().strip() == "common core state standards") \
                            or (isinstance(n.get('educationalFramework',''), list) and n.get('educationalFramework',[]).pop().lower().strip() == "common core state standards") \
                        ) \
                    )

            for alignment in alignments:
                if isinstance(alignment, str):
                    standards.extend(mapping.get(alignment, alignment))
                elif isinstance(alignment, list):
                    for aln in alignment:
                        standards.extend(mapping.get(aln, aln))

        return standards

    def handle_keys_json_ld(self, node):
        keys = []
        target_elements = ['inLanguage', 'isbn', 'provider',
                           'learningResourceType', 'keywords',
                           'educationalUse', 'author', "intendedUserRole"]
        def handle_possible_dict(data):
            if isinstance(data, dict):
                return data.get('name')
            return data
        for k in target_elements:

            if k in node:
                if isinstance(node[k], str):
                    keys.append(handle_possible_dict(node[k]))
                elif isinstance(node[k], list):
                    keys.extend([handle_possible_dict(k) for k in node[k]])
        if "bookFormat" in node:
            bookFormat = node['bookFormat']
            #increment the rfind result by 1 to exclude the '/' character
            f = bookFormat[bookFormat.rfind('/')+1:]
            keys.append(f)
        if "@id" in node:
            url = node['@id']
            parts = urlparse.urlparse(url)
            qs = urlparse.parse_qs(parts.query)
            if 'downloadFormat' in qs:
                if isinstance(qs['downloadFormat'], str):
                    keys.append(qs['downloadFOrmat'])
                else:
                    keys.extend(qs['downloadFormat'])
        return keys

