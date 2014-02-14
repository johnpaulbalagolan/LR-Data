import csv

STANDARDS_MAPPING_FILE = "standards_mapping.csv"

STANDARDS_MAPPING = None

def getStandardsMapping():
    global STANDARDS_MAPPING

    if STANDARDS_MAPPING is None:

        STANDARDS_MAPPING = buildStandardsMapping(STANDARDS_MAPPING_FILE)


    return STANDARDS_MAPPING


def buildStandardsMapping(file_name):

    mapping = {}
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for item in row:
                if 'asn.jesandco.org' in item:
                    continue
                for item2 in row:
                    if item != item2:
                        if 'asn.jesandco.org' in item2:
                            item2 = item2[item2.rfind('/')+1:]
                        else:
                            continue
                        key = item.lower()
                        if key not in mapping:
                            mapping[key] = []
                        mapping[key].append(item2.lower())

    return mapping
