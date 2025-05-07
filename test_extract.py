import unittest
import extract

class TestExtract(unittest.TestCase):
  def test_find_last_brace(self):
    data = {'{}': 1,
            'a{}': 2,
            '{a}': 2,
            '{}a': 1,
            '{a{}b}': 5,
            ' {}': 2,
            '{} ': 1,
            '\n\n\n{a{b{c}}{}\n\n\n\n{z{z}}\n\n}\n\n': 25
    }
    for txt, expected in data.items():
      index = extract.find_last_brace(txt, 0)
      self.assertEqual(expected, index)
      self.assertEqual('}', txt[index])

  def test_resource_sets_length(self):
    data = { extract.resource("","", 0, 9): 10,
             extract.resource("", "", 11, 30): 20,
    }
    for resource, expected in data.items():
      self.assertEqual(expected, resource.len)

  def test_find_resources_for_single_cases(self):
    # hand crafting these offset values is a pain, sorry :(
    e1 = extract.resource('"aws_foo"', '"foo"', 0, 26)
    e2 = extract.resource('"aws_foo"', '"foo2"', 0, 50)
    e3 = extract.resource('"a"', '"b"', 0, 18)
    e4 = extract.resource('"a"', '"c"', 20, 38)
    e5 = extract.resource('"aws_bar"', '"bar"', 50, 179)
    e6 = extract.resource('"aws_bat"', '"bat"', 188, 221)
    data = { # txt input : expected resources)
      'resource "aws_foo" "foo" {}' : [e1],
      'resource "aws_foo" "foo2" {{stuff} otherstuff {{}}}': [e2],
      'resource "a" "b" {}\nresource "a" "c" {}': [e3, e4],
      '''
      data "aws_thing" "thing1" {
      }

      resource "aws_bar" "bar" {
        this doesn't matter if it is valid HCL, just needs the proper brace matching
        {}
      }

      resource "aws_bat" "bat" {
      }
      ''' : [e5, e6]
    }
    for txt, expected in data.items():
      resources = extract.find_resources(txt)
      self.assertEqual(len(expected), len(resources))
      for index, resource in enumerate(resources):
        self.assertEqual(expected[index], resource)

  # test that the document class returns the correct text segments
  # for given resource objects
  def test_document(self):
    text = '0123456789'
    r1 = extract.resource('text', 'whole', 0, 10)
    r2 = extract.resource('text', 'subsection', 2, 8)
    data = {('text', 'whole') : (text[0:10], r1),
            ('text', 'subsection') : (text[2:8], r2),
            ('wrong', 'stillwrong') : (None, None)
    }
    doc = extract.document(text)
    doc.add_resource(r2)
    doc.add_resource(r1)

    for (rtype, name), (expected_text, expected_resource) in data.items():
      r = doc.get_resource(rtype, name)
      self.assertEqual(expected_resource, r)
      if not r:
        continue
      txt = doc.get_resource_text(r)
      self.assertEqual(expected_text, txt)

  # this is more of an integration test since it's testing a function
  # that uses live classes and not mocks
  def test_merge_document_into(self):
    # expected (merged) : (generated txt, original text)
    data = {'resource "a" "b" {aa}' : ('resource "a" "b" {aa}', 'resource "a" "b" {a}'),
            'resource "a" "c" {c}' : ('resource "a" "c" {c}', 'resource "a" "c" {aaaaa}'),
            '''
            resource "aws" "preserved" {
               description = "i should be the same"
            }
            resource "aws" "mushed" {
              description  = "i came from the generated text"
            }
            resource "aws" "alsopreserved" {
              description = "i should also be the same"
            }
            ''' :
            (
            '''
            resource "aws" "mushed" {
              description  = "i came from the generated text"
            }
            ''',
            '''
            resource "aws" "preserved" {
               description = "i should be the same"
            }
            resource "aws" "mushed" {
              description  = "i should be replaced"
              name = "doomed"
              thing = {name: "value"}
            }
            resource "aws" "alsopreserved" {
              description = "i should also be the same"
            }
            ''')
    }
    for expected, (gen_text, orig_text) in data.items():
      gen_doc = extract.document(gen_text)
      orig_doc = extract.document(orig_text)
      for doc in [gen_doc, orig_doc]:
        for r in extract.find_resources(doc.txt):
          doc.add_resource(r)
      self.assertEqual(expected, extract.merge_document_into(gen_doc, orig_doc))

if __name__ == '__main__':
  unittest.main()
