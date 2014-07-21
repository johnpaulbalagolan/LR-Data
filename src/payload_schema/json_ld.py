from base import PayloadSchemaParser

import urlparse
from pprint import pprint

class JsonLdParser(PayloadSchemaParser):
    def _parse(self, doc, envelope, mapping):
        doc.update({
            'standards': [],
            'accessMode': [],
            'mediaFeatures': [],
            'hasScreenshot': True,
        })

        resource_data = self._loadJSONResourceData(envelope)

        payload_graph = resource_data.get('@graph')
        if not payload_graph:
            payload_graph = [resource_data]


        graph_data = self.process_json_ld_graph(payload_graph, mapping)

        for k in ['keys', 'standards', 'accessMode', 'mediaFeatures', 'grades']:
            doc[k].extend(graph_data.get(k, []))

        for k in ['title', 'description', 'publisher']:
            if k in graph_data:
                doc[k] = graph_data[k]

    def process_json_ld_graph(self, graph, mapping):
        data = {}
        keys = []
        standards = []
        grades = []
        media_features = []
        access_mode = []
        for node in graph:
            keys.extend(self.handle_keys_json_ld(node))
            standards.extend(self.handle_standards_json_ld(node, mapping))
            grades.extend(self.handle_grades_json_ld(node))

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
                data['title'] = self.get_first_or_value(node, 'name', self.is_string)
            if "description" in node and 'description' not in data:
                data['description'] = self.get_first_or_value(node, 'description', self.is_string)
            if 'publisher' in node:
                pub = self.get_first_or_value(node, 'publisher', lambda x: self.is_string(x) or isinstance(x, dict))
                if isinstance(pub, dict):
                    data['publisher'] = pub.get('name', '')
                else:
                    data['publisher'] = pub
        data['keys'] = keys
        data['standards'] = standards
        data['accessMode'] = set(access_mode)
        data['mediaFeatures'] = set(media_features)
        data['grades'] = set(grades)

        return data

    def get_first_or_value(self, data, key, test):
        if test(data[key]):
            return data[key]
        elif isinstance(data[key], list):
            return data[key].pop()

    def get_educational_alignments_by_framework(self, node, frameworks):

        if self.is_string(frameworks):
            frameworks = [frameworks]

        frameworks = [i.lower() for i in frameworks]

        if 'educationalAlignment' in node:

            edAlignment = node['educationalAlignment']

            # Compensate for EZ-Publish not producing proper lists when only a single object is defined for educationalAlignment
            if(isinstance(edAlignment, dict)):
                edAlignment = [edAlignment]

            alignments = (n
                for n in edAlignment \
                    if 'targetName' in n  and 'educationalFramework' in n\
                        and ( \
                            (self.is_string(n['educationalFramework']) and n['educationalFramework'].lower().strip() in frameworks) \
                            or (isinstance(n['educationalFramework'], list) and len(n['educationalFramework']) and n['educationalFramework'].pop().lower().strip() in frameworks) \
                        ) \
                    )

            return alignments


        return []


    def handle_standards_json_ld(self, node, mapping):
        standards = []

        framework = [
            "Common Core State Standards",
            "Common Core State Standards for Math",
            "Common Core State Standards for English Language Arts"
        ]

        standardValues = [ i['targetName'] for i in self.get_educational_alignments_by_framework(node, framework) ]

        for standardName in standardValues:

            if self.is_string(standardName):
                standardNames = [standardName]
            else:
                standardNames = standardName[:]

            for standard in standardNames:
                standards.extend(mapping.get(standard.lower(), [standard]))

        return standards

    def handle_grades_json_ld(self, node):
        grades = []

        framework = "US K-12 Grade Levels"

        gradeValues = [ i['targetName'] for i in self.get_educational_alignments_by_framework(node, framework) ]

        for grade in gradeValues:
            if self.is_string(grade):
                grades.extend(grade.split(','))
            elif isinstance(alignment, list):
                for g in grade:
                    grades.extend(g.split(','))

        return grades

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
                if self.is_string(node[k]):
                    keys.extend(node[k].split(','))
                elif isinstance(node[k], list):
                    keys.extend([handle_possible_dict(i) for i in node[k]])
                elif isinstance(node[k], dict):
                    keys.append(handle_possible_dict(node[k]))

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
                if self.is_string(qs['downloadFormat']):
                    keys.append(qs['downloadFormat'])
                else:
                    keys.extend(qs['downloadFormat'])
        return keys

