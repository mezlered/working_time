import os
import sys
import unittest
import xml.etree.cElementTree as etree
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.getcwd(), ''))

import working_time
from working_time import DATE_FORMAT, DATE_TIME_FORMAT
from tests.cases import cases


class TestSuite(unittest.TestCase):

    def get_etreeElement(self, person):
        root = etree.Element("person", full_name=person.get('full_name'))
        start, end = etree.Element("start"), etree.Element("end")
        start.text, end.text = person.get('start'), person.get('end')
        root.append(start)
        root.append(end)
        return root

    @cases(['10-02-2020', '10-03-2022', ])
    def test_valid_date_format(self, value):
        self.assertIsInstance(working_time.str_to_datetime(value, pattern=DATE_FORMAT), datetime)

    @cases(['', '2011:17:12', '31-02-2020', ])
    def test_invalid_date_format(self, value):
        with self.assertRaises(ValueError):
            working_time.str_to_datetime(value, pattern=DATE_FORMAT)

    @cases(['22-12-2011 19:43:02', '25-12-2011 19:43:02',])
    def test_valid_date_time_format(self, value):
        self.assertIsInstance(working_time.str_to_datetime(value, pattern=DATE_TIME_FORMAT), datetime)

    @cases(['', '22:12:2011:19:43:02', '31:02:2020',])
    def test_invalid_date_time_format(self, value):
        with self.assertRaises(ValueError):
            working_time.str_to_datetime(value, pattern=DATE_TIME_FORMAT)

    @cases([
        {'full_name': 'a.stepanova', 'start': '21-12-2011 09:40:10', 'end': '21-12-2011 17:59:15',},
        {'full_name': 'a.stepanova', 'start': '21-12-2011 10:40:10', 'end': '21-12-2011 20:40:10',},
        {'full_name': 'i.ivanov', 'start': '21-09-2020 08:30:10', 'end': '21-09-2020 15:30:10',},
    ])
    def test_valid_prosses_element(self, person):
        node = self.get_etreeElement(person)
        
        person['start'] = datetime.strptime(person['start'], DATE_TIME_FORMAT)
        person['end'] = datetime.strptime(person['end'], DATE_TIME_FORMAT)
        
        parse_person = working_time.prosses_element(node)
        self.assertIsInstance(parse_person, dict)
        self.assertEqual(person, parse_person)

    @cases([
        {},
        {'start': '21-12-2011 09:40:10', 'end': '21-12-2011 17:59:15',},
        {'full_name': '', 'start': '21-12-2011 09:40:10', 'end': '21-12-2011 17:59:15',},
        {'full_name': 'a.stepanova', 'end': '21-12-2011 20:40:10',},
        {'full_name': 'i.ivanov', 'start': '21-09-2020 08:30:10',},
        {'name': 'i.ivanov', 'start': '21-09-2020 08:30:10',},
    ])
    def test_invalid_prosses_element(self, person):
        node = self.get_etreeElement(person)
        self.assertIsNone(working_time.prosses_element(node))

    @cases([
        {'full_name': 'a.stepanova', 'start': '21-12-2011', 'end': '21-12-2011 17:59:15',},
        {'full_name': 'a.stepanova', 'start': '10:40:10', 'end': '21-12-2011 20:40:10',},
        {'full_name': 'i.ivanov', 'start': '21:09:2020 08:30:10', 'end': '21:09:2020 15:30:10',},
    ])
    def test_invalid_datetime_format(self, person):
        node = self.get_etreeElement(person)
        self.assertIsNone(working_time.prosses_element(node))

    @cases([
        {'full_name': 'a.stepanova', 'start': '21-12-2011 17:59:15', 'end': '21-12-2011 09:40:10',},
        {'full_name': 'a.stepanova', 'start': '21-12-2011 20:40:10', 'end': '21-12-2011 10:40:10',},
        {'full_name': 'i.ivanov', 'start': '21-09-2020 15:30:10', 'end': '21-09-2020 08:30:10',},
    ])
    def test_invalid_datetime_values(self, person):
        node = self.get_etreeElement(person)
        self.assertIsNone(working_time.prosses_element(node))


if __name__ == '__main__':
    unittest.main()
