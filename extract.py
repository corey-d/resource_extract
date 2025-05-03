import re

txt = '''
resource "aws_foo" "bar" {
asdf a
asdfasdfa 
adsfadf
}

resource "aws_foo" "baz" {
 { asdfadf 
    { asdfas dasfasfd a
    }
 }
}

resource "azure_bar" "gar_bar3_org" {


}
'''

class resource:
    def __init__(self, rtype: str, name: str, start: int, match_end: int):
        self.rtype = rtype
        self.name = name
        self.start = start
        self.match_end = match_end
        self.end = None
        self.len = None

    def find_end(self, txt: str):
        i = self.match_end
        N = len(txt)
        while txt[i].isspace() and i < N:
            i += 1
        b = '{'
        e = '}'
        
        count = int(txt[i] == b)
        while count > 0 and i < N:
            i += 1
            if txt[i] == b:
                count += 1
                continue
            if txt[i] == e:
                count -= 1
                continue
        if i == N  and txt[i - 1] != e:
            self.end = None
            self.len = None
            return
        self.end = i + 1
        self.len = self.end - self.start + 1


def find_resources(txt: str) -> list[resource]:
    pattern = re.compile(r'\s*(resource)\s+(\"\w+\")\s+(\"[\w\-]+\")\s*')
    resources = []
    for match in pattern.finditer(txt):
        r = resource(match.group(1), match.group(2), match.start(), match.end())
        r.find_end(txt)
        resources.append(r)
    return resources

rs = find_resources(txt)