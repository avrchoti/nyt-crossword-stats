import argparse
import json
import pathlib
import os
from csv import DictWriter, DictReader
from datetime import datetime, timedelta
import requests
import keyring
from tqdm import tqdm

BEGINNING_OF_TIME = datetime(year=2016, month=9, day=1)

FIELDS = [
    'date',
    'day',
    'elapsed_seconds',
    'solved',
    'checked',
    'revealed',
    'streak_eligible',
]

API_ROOT = 'https://nyt-games-prd.appspot.com/svc/crosswords'
PUZZLE_INFO = API_ROOT + '/v2/puzzle/daily-{date}.json'
SOLVE_INFO = API_ROOT + '/v2/game/{game_id}.json'
DATE_FORMAT = '%Y-%m-%d'

def create_parser():
   parser = argparse.ArgumentParser(description='Fetch NYT Crossword stats')
   parser.add_argument(
       '-u', '--username', help='NYT Account Email Address')
   parser.add_argument(
       '-p', '--password', help='NYT Account Password', required=False)
   parser.add_argument('-E', '--extend-file', action="store_true", help='Fetch records since last seen in CSV file and append to file')
   parser.add_argument('-C', '--use-cred-file',  action="store_true", help='Use credentials file')
   parser.add_argument('-K', '--keyring',  action="store_true", help='Use keyring for password (credname nytimes)')
   parser.add_argument(
       '-s', '--start-date',
       help='The first date to pull from, inclusive (defaults to 30 days ago)',
       default=datetime.strftime(datetime.now() - timedelta(days=30), DATE_FORMAT)
   )
   parser.add_argument(
       '-e', '--end-date',
       help='The last date to pull from, inclusive (defaults to today)',
       default=datetime.strftime(datetime.now(), DATE_FORMAT)
   )
   parser.add_argument(
       '-o', '--output-csv',
       help='The CSV file to write to',
       default=workdir() / 'data.csv'
   )
   parser.add_argument(
       '--strict',
       help='Don\'t allow missing puzzles or errors',
       action='store_true',
   )
   return parser


def login(username, password):
    """ Return the NYT-S cookie after logging in """
    login_resp = requests.post(
        'https://myaccount.nytimes.com/svc/ios/v2/login',
        data={
            'login': username,
            'password': password,
        },
        headers={
            'User-Agent': 'Mozilla/5.0',
            'client_id': 'ios.crosswords',
        }
    )
    login_resp.raise_for_status()
    for cookie in login_resp.json()['data']['cookies']:
        if cookie['name'] == 'NYT-S':
            return cookie['cipheredValue']
    raise ValueError('NYT-S cookie not found')


def get_puzzle_stats(date, cookie):
    puzzle_resp = requests.get(
        PUZZLE_INFO.format(date=date),
        cookies={
            'NYT-S': cookie,
        },
    )
    puzzle_resp.raise_for_status()
    puzzle_date = datetime.strptime(date, DATE_FORMAT)
    puzzle_info = puzzle_resp.json().get('results')[0]
    solve_resp = requests.get(
        SOLVE_INFO.format(game_id=puzzle_info['puzzle_id']),
        cookies={
            'NYT-S': cookie,
        },
    )
    solve_resp.raise_for_status()
    solve_info = solve_resp.json().get('results')

    solved = solve_info.get('solved', False)
    checked = 'firstChecked' in solve_info
    revealed = 'firstRevealed' in solve_info
    solve_date = datetime.fromtimestamp(solve_info.get('firstSolved', 0))
    # A puzzle is streak eligible if they didn't cheat and they solved it
    # before midnight PST (assume 8 hour offset for now, no DST)
    streak_eligible = solved and not checked and not revealed and (
        solve_date <= puzzle_date + timedelta(days=1) + timedelta(hours=8))

    return {
        'elapsed_seconds': solve_info.get('timeElapsed', 0),
        'solved': int(solved),
        'checked': int(checked),
        'revealed': int(revealed),
        'streak_eligible': int(streak_eligible),
    }


def fetch_and_write_to_csv(start_date, end_date, output_csv, strict):
    fields = FIELDS
    date = start_date
    write_header = not os.path.exists(output_csv)
    with open(output_csv, 'a', newline='') as csvfile, \
            tqdm(total=(end_date - start_date).days + 1) as pbar:
        writer = DictWriter(csvfile, fields)
        if write_header:
            writer.writeheader()
        count = 0
        while date <= end_date:
            date_str = datetime.strftime(date, DATE_FORMAT)
            try:
                solve = get_puzzle_stats(date_str, cookie)
                solve['date'] = date_str
                solve['day'] = datetime.strftime(date, '%a')
                writer.writerow(solve)
                count += 1
            except Exception:
                # Ignore missing puzzles errors in non-strict
                if strict:
                    raise
            pbar.update(1)
            date += timedelta(days=1)
    print("{} rows written to {}".format(count, output_csv))


def calc_start_date(args):
    if args.extend_file:
        start_date = read_last_date_from_file( args.output_csv) + timedelta(days=1)
    else:
        start_date = datetime.strptime(args.start_date, DATE_FORMAT)
    return start_date

def read_last_date_from_file(filename):
    try:
        with open( filename) as f:
            lines = f.readlines()
    except FileNotFoundError:
        # Start at the beginning of time
        return BEGINNING_OF_TIME

    fields = lines[-1].split(',')
    res = datetime.strptime(fields[0], DATE_FORMAT)
    return res

def read_credfile( ):
   with open( workdir() / "credentials.json", "r" ) as f:
      data = json.load( f )
      return data[ "username"],data[ "password" ]


def workdir():
    return pathlib.Path( os.path.expanduser("~" ) ) / "nyt-crossword-data"

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    if args.password:
        password = args.password
    elif args.keyring:
        password = keyring.get_password("nytimes", args.username)
    elif args.use_cred_file:
        username, password = read_credfile( )

    cookie = login(username, password)
    start_date = calc_start_date( args )
    end_date = datetime.strptime(args.end_date, DATE_FORMAT)
    print("Getting stats from {} until {}".format(
        datetime.strftime(start_date, DATE_FORMAT),
        datetime.strftime(end_date, DATE_FORMAT)))
    fetch_and_write_to_csv(start_date, end_date, args.output_csv, args.strict)
