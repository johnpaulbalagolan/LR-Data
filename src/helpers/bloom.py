from pybloomfilter import BloomFilter
import os.path

# def getBloomFilter(contentFile, filterFilename):
#     if not os.path.isfile(filterFilename):
#         # generate our whitelist filter
#         return createBloomFilter(contentFile, filterFilename)
#     else:
#         return BloomFilter.open(filterFilename)

FILTERS = {}

def getBloomFilter(contentFile, filterFilename):
    # bloom filters, while effective for memory are poor as whitelists/blacklists due to
    # posibility of false positive numbers.  Replacing old implementation with a set
    # And.. based on the settings for bloom filters below I was getting HIGH
    # false positives on my blacklist of 7 sites, which should have almost no collisions

    if contentFile not in FILTERS:

        filterSet = set()

        with open(contentFile, "r") as f:
            for domain in f:
                d = domain.rstrip()

                filterSet.add(d)

        FILTERS[contentFile] = filterSet


    return FILTERS[contentFile]

    # if not os.path.isfile(filterFilename):
    #     # generate our whitelist filter
    #     return createBloomFilter(contentFile, filterFilename)
    # else:
    #     return BloomFilter.open(filterFilename)

def createBloomFilter(contentFile, filterFilename):
    bf = BloomFilter(10000000, 0.9999999, filterFilename)
    total = 0
    count = 0
    failed = 0
    with open(contentFile, "r") as f:
        for domain in f:
            total += 1
            d = domain.rstrip()

            if bf.add(d):
                count += 1
                print(d)
            else:
                failed += 1

    print "Total ", total
    print "Added ", count
    print "Conflicted", failed

if __name__ == "__main__":
    createBloomFilter("whitelist.txt", "whitelist_filter.bloom")
    createBloomFilter("blacklist.txt", "blacklist_filter.bloom")

