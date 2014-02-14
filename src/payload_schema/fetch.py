from base import PayloadSchemaParser

class FetchParser(PayloadSchemaParser):
    def _parse(self, doc, envelope, mapping):
        url = envelope['resource_locator']

        doc.update(self.get_html_display(url, envelope['identity']['submitter']))


    def get_html_display(self, url, publisher):
        resp = urllib2.urlopen(url)
        if not resp.headers['content-type'].startswith('text/html'):
            return {}

        doc = {}

        raw = resp.read()
        raw = raw.decode('utf-8')
        soup = BeautifulSoup(raw)
        title = url
        if soup.html is not None and \
                soup.html.head is not None and \
                soup.html.head.title is not None:
            doc['title'] = soup.html.head.title.string


        # search meta tags for descriptions
        for d in soup.findAll(attrs={"name": "description"}):
            print d
            if d['content'] is not None:
                doc['description'] = d['content']
                break

        # should we not find a description, make one out of the first 100 non-HTML words on the site
        if doc['description'] is None:
            raw = nltk.clean_html(raw)
            tokens = nltk.word_tokenize(raw)
            doc['description'] = " ".join(tokens[:100])

        return doc
