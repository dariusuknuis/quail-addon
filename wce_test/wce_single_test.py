import unittest
import io
import os

from wce.wce import wce

def read_file(path):
    with open(path, "r") as file_reader:
        data = file_reader.read()
    return io.StringIO(data)

class TestSingleWCE(unittest.TestCase):
    def test_single(self):
        path = ""
        if not os.path.exists(path):
            print(f"File does not exist: {path}")
            return
        data = read_file(path+"/_root.wce")
        e = wce("")
        e.parse_definitions(path, data)


