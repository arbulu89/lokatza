"""
:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2023-01-31
"""

import logging
import argparse

from lokatza import db
from lokatza import player
from lokatza import baseline as baseline_module
from lokatza import detector

PROG = 'lokatza'
LOGGING_FORMAT = '%(message)s'


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(PROG)

    parser.add_argument(
        '-l', '--learn', action='store_true')

    parser.add_argument(
        '-u', '--url', type=str,
        help='IP webcam application url')

    parser.add_argument(
        '-c', '--cyclist-number', type=int,
        help='Cyclists number in the race')

    parser.add_argument(
        '-v', '--verbosity',
        help='Python logging level. Options: DEBUG, INFO, WARN, ERROR (INFO by default)')

    args = parser.parse_args()
    return parser, args


def setup_logger(level):
    """
    Setup logging
    """
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOGGING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level=level)
    return logger

# pylint:disable=W0212
def run():
    """
    Main execution
    """
    parser, args = parse_arguments()
    logger = setup_logger(args.verbosity or logging.DEBUG)

    db_object = db.Database()
    players_manager = player.Players(db_object)
    baselines_manager = baseline_module.Baselines(db_object)
    det = detector.Detector(args.url, args.cyclist_number)

    if args.learn:
        b = det.learn()
        baselines_manager.add_baseline_from_object(b)

    try:
        baseline = baselines_manager.get_baseline(1)
    except baseline_module.BaselineNotFound:
        print("Baseline not found, run the the app using the -l flag")
        db_object.close()
        return

    while True:
        det.find_template()
        p = det.run(baseline.baseline)
        p.print()
        players_manager.add_player_from_object(p)
    
    # for p in players_manager.get_players():
    #     p.print()

    db_object.close()

if __name__ == "__main__": # pragma: no cover
    run()
