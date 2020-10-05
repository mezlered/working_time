### The program calculates the time of the visit


The program calculates the time of the visit of all employee at the workplace for a spesific
date. Allows you to filter by date range, and show the visit time for each employee. If the
`end_time` of an employee belongs to the next working day, then the working time will be taken
into account on the date corresponding to the `start_time`.

## Run

```bash
python -m working_time.py
```
## Tests
```bash
python -m tests.unit.test_unit
```

## To get help

```bash
python -m working_time.py --help
```
```
usage: python -m parse.py [-h] [--start_date START_DATE] [--end_date END_DATE]
                          [-l LOG] [--persons_info] [--debug] --input_path
                          INPUT_PATH

The program calculates the total time of visits by all people for eachnumber.
Allows you to filter by date range and display the time ofeach person's stay.

optional arguments:
  -h, --help            show this help message and exit
  --start_date START_DATE
                        Start date of the time range.
  --end_date END_DATE   End date of the time range.
  -l LOG, --log LOG
  --persons_info        show the time of the person's visit.
  --debug
  --input_path INPUT_PATH
                        Path attached visit time information.
```