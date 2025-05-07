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
        print(resource)
        self.assertEqual(expected[index], resource)


if __name__ == '__main__':
  unittest.main()
