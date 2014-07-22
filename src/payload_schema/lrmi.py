from base import PayloadSchemaParser

class LrmiParser(PayloadSchemaParser):
    def _parse(self, doc, envelope, mapping):
        url = envelope['resource_locator']
        resource_data = self._loadJSONResourceData(envelope)

        if 'items' in resource_data:
            properties = resource_data['items'].pop().get('properties', {})
        else:
            properties = resource_data.get('properties', {})

        educational_alignment = properties.get('educationalAlignment', [{}]).pop()
        educational_alignment_properties = educational_alignment.get('properties', {})
        standards_names = educational_alignment_properties.get('targetName', [''])

        standards = []
        for ids in (mapping.get(standards_name.lower(), [standards_name.lower()]) for standards_name in standards_names):
            for s in ids:
                standards.append(s)


        for props in educational_alignment_properties:
            if props.get('type') == 'alignmentType':
                doc['keys'].push(props.get('target_name'))

        if 'publisher' in properties:
            doc['publisher'] = properties.get('publisher', []).pop().get('name')


        name = properties.get('name')
        description = ''

        if isinstance(name, list):
            name = name.pop()
            description = properties.get('description')
            if isinstance(description, list):
                description = description.pop()


        doc['keys'].extend(properties.get('about', []))

        keywords = properties.get('keywords', '')

        if keywords is not "":
            docs['keys'].extend([i.trim() for i in keywords.split(',')])

        doc.update({
            'title': name,
            'description': description,
            'standards': standards,
            'hasScreenshot': False,
        })


