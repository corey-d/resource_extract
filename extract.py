import re

class resource:
    def __init__(self, rtype: str, name: str, start: int, end: int):
        self.rtype = rtype
        self.name = name
        self.start = start
        self.end = end
        self.len = end - start + 1

    def __eq__(self, other):
        return (self.rtype == other.rtype and
            self.name == other.name and
            self.start == other.start and
            self.end == other.end and
            self.len == other.len)

    def __hash__(self):
        return hash(f'{id(self)}')

    def __repr__(self):
        return f'rtype: {self.rtype}, name: {self.name}, start: {self.start}, end: {self.end}, len: {self.len}'


def find_last_brace(txt: str, start: int) -> int:
        i = start
        N = len(txt)
        count = 0
        while i < N and count >= 0:
            if txt[i] == '{':
                count += 1
            elif txt[i] == '}':
                count -= 1
                if count == 0:
                    break
            i += 1
        return i


def find_resources(txt: str) -> list[resource]:
    # search up to the char right before opening {
    pattern = re.compile(r'\s*(resource)\s+(\"\w+\")\s+(\"[\w\-]+\")\s*')
    resources = []
    for match in pattern.finditer(txt):
        # this returns the starting index from the first group (word resource) within the match
        # this effectively skips any whitespace objects found prior to the resource word.
        start = match.start(1)
        end = find_last_brace(txt, start)
        r = resource(match.group(2), match.group(3), start, end)
        resources.append(r)
    return resources

class document:
    def __init__(self, txt: str):
        self.txt = txt
        self.resources = []

    def add_resource(self, res):
        self.resources.append(res)

    def get_resource(self, rtype, name: str) -> resource:
        for r in self.resources:
            if r.rtype == rtype and r.name == name:
                 return r
        return None

    def get_resource_text(self, res: resource):
        r = self.get_resource(res.rtype, res.name)
        if not r:
            return ''
        return self.txt[r.start:r.end]



def create_document(txt: str) -> document:
    doc = document(txt)
    for res in find_resources(txt):
        doc.add_resource(res)
    return doc

# source = generated, destionation = original
def merge_document_into(source: document, destination: document) -> str:
    merged = ''
    index = 0
    # get resources that need replacing from destination document
    # get replacment text from source document
    # copy replacement text from source to dest
    # preserve non-replaced text
    # update index
    for s in source.resources:
        print(f'S: {s}')
        # get new text from source, if
        newtext = source.get_resource_text(s)
        print(f'N: {newtext}')
        if not newtext:
            # TODO: handle this error situation - source resource should be returning source text
            continue

        # get indices of preserved text block
        d = destination.get_resource(s.rtype, s.name)
        # copy in perserved text, up to start of that resource's block
        merged += destination.txt[index:d.start]
        # replace that resource block with new text
        merged += newtext
        # update index to end of original block to get next address of preserved text
        index += d.end
    # copy the rest
    merged += destination.txt[index:]
    return merged


if __name__ == '__main__':
    f = open('orig.tf', 'r')
    orig = create_document(f.read())
    f.close()
    f = open('generated.tf', 'r')
    gen = create_document(f.read())
    f.close()
    print(merge_document_into(gen, orig))
