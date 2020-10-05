import argparse
import logging
import os
import xml.etree.cElementTree as etree
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Iterable, List, Set, Tuple

DATE_FORMAT = '%d-%m-%Y'
DATE_TIME_FORMAT = '%d-%m-%Y %H:%M:%S'
FILE_EXTENSION = '.xml'


def xml_to_dict_gen(file_path: str, tag: str='person') -> Iterable[dict]:
    '''Provides incremental parsing of xml document and returns a parsed element `tag`.
    '''

    total = processed = 0
    for _, element in etree.iterparse(file_path, events=('start', )):
        if element.tag == tag:
            total += 1
            person = prosses_element(element)
            if person:
                processed += 1
                yield person
            else:
                logging.debug(f'Error parsing element: {etree.tostring(element)}')
        element.clear()

    logging.info(
        f'Успешно записей обработано - {processed} из {total}. '
        f'Процент успешного парсинга - {processed / total * 100:.2f} %.')


def prosses_element(element: etree) -> dict:
    '''Checks for non-empty values ​​for tags:'`full_name`, `start`, `end` and validity
    of the string representation of the date and time of `end` and `start` tags.
    '''

    full_name = element.get('full_name')
    if not full_name:
        logging.info('`full_name` tag cannot be empty.')
        return
    
    person = {'full_name': full_name}
    for child in element:
        person[child.tag] = child.text

    for tag in ('start', 'end'):
        data = person.get(tag)
        if not data:
            logging.info('There are no valid tags or their value must be non-empty.')
            return
        try:
            person[tag] = str_to_datetime(data, DATE_TIME_FORMAT)
        except ValueError as exc:
            logging.info(exc)
            return
    
    if person['end'] < person['start']:
        logging.info(
            'The time value of the `end` tag cannot be greater than the `start` value.')
        return

    return person


def str_to_datetime(str_value: str, pattern: str) -> datetime:
    try:
        date = datetime.strptime(str_value, pattern)
    except ValueError:
        raise ValueError(f'Error date format: {str_value}')
    return date


def get_total_time_person_for_date(
        times_of_visit: List[Tuple[datetime, datetime]], day: datetime) -> timedelta:
    ''' Calculates the total time of arrival of a employee per `day`.'''

    person_time = timedelta()
    for start_time, end_time in times_of_visit:
        if start_time.date() == day:
            person_time += end_time - start_time
    return person_time


def get_persons_info(path: str):
    '''The function collects data about the visit time for each employee.'''
    
    persons = defaultdict(list)
    all_days_of_visits = set()

    for person in xml_to_dict_gen(path):
        start_time = person['start']
        end_time = person['end']
        persons[person['full_name']].append((start_time, end_time))
        all_days_of_visits.add(start_time.date())
    return persons, all_days_of_visits


def get_range_days_of_visits(
        start_day, end_day: datetime, all_days_of_visits: Set[datetime]) -> Set[datetime]:
    ''' Limits the originating set of `days` to a range of dates
    [`start_day`, `end_day`]. If only one of `start_day` or `end_day`
    return the given.
    '''

    days_of_visits = set()
    if start_day and end_day:
        if end_day < start_day:
            start_day, end_day = end_day, start_day
        delta = end_day - start_day

        for i in range(delta.days + 1):
            day = start_day + timedelta(i)
            if day in days:
                days_of_visits.add(day)
        return days_of_visits

    if start_day or end_day:
        days_of_visits.add(start_day or end_day)
        return actidays_of_visitsve_days

    return all_days_of_visits


def main(arguments: argparse.Namespace) -> None:
    persons, all_days_of_visits = get_persons_info(arguments.input_path)
    start_date, end_date = arguments.start_date, arguments.end_date
    days_of_visits = get_range_days_of_visits(start_date, end_date, all_days_of_visits)

    for date in sorted(days_of_visits):
        total_time, count = timedelta(), 1
        print(f'Дата: {date.strftime(DATE_FORMAT)}')

        for full_name, times_of_visit in sorted(persons.items()):
            time_running = get_total_time_person_for_date(times_of_visit, date)
            total_time += time_running
            if time_running and arguments.persons_info:
                print(f'{count}. {full_name} - {time_running}')
                count += 1
        print(f'Общее время прибывания работников: {total_time}')


def prepare_datetime(date: str) -> datetime:
    ''' Validate the value date of `--start_date`, `--end_date` command line argument.'''

    try:
        date = str_to_datetime(date, DATE_FORMAT)
    except ValueError as exc:
        logging.exception(exc)
        raise argparse.ArgumentTypeError(
            f'Non-existent date or invalid date date format [dd-mm-yyyy] - {date}.'
        )
    return date.date()


def prepare_input_path(path: str) -> str:
    ''' Validate the value of `--input_path` command line argument.'''

    if not os.path.exists(path):
        raise argparse.ArgumentTypeError('Invalid file path.')

    _, ext = os.path.splitext(path)
    if ext != FILE_EXTENSION:
        raise argparse.ArgumentTypeError('Invalid file extension.')

    return path


def get_arguments():
    args = argparse.ArgumentParser(
        description=(
            'The program calculates the total time of visits by all people for each'
            'number. Allows you to filter by date range and display the time of'
            'each person\'s stay.'),
        prog='python -m parse.py')

    args.add_argument(
        '--start_date', type=prepare_datetime,
        help='Start date of the time range.', default=None,
    )
    args.add_argument(
        '--end_date', type=prepare_datetime,
        help='End date of the time range.', default=None,
    )
    args.add_argument('-l', '--log', action='store', default=None)
    args.add_argument(
        '--persons_info', action='store_true',
        help='show the time of the person\'s visit.', default=False,
    )
    args.add_argument('--debug', action='store_true', default=False)
    args.add_argument(
        '--input_path',
        help='Path attached visit time information.',
        type=prepare_input_path, required=True,
    )
    return args.parse_args()


if __name__ == "__main__":
    arguments  = get_arguments()
    logging.basicConfig(filename=arguments.log,
                        level=logging.DEBUG if arguments.debug else logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y.%m.%d %H:%M:%S')

    try:
        main(arguments)
    except KeyboardInterrupt:
        logging.info('Parsing has been stopped')
    except Exception as exc:
        logging.exception(f'Unexpected error: {exc}')
