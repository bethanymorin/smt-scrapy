import os
import argparse

from scraper.utils import get_db_connection

def get_number_of_articles():
    db = get_db_connection()
    query = (
        "SELECT COUNT(*) FROM node n WHERE"
        " n.type = 'post' AND n.status = 1"
    )

    cursor = db.cursor()
    cursor.execute(query)

    num_articles = 0

    for count in cursor:
        num_articles = count[0]

    db.close()
    return num_articles


def main():

    DEFAULT_START = 0

    parser = argparse.ArgumentParser(
        description=(
            'Manager for running a scrapy script for SMT stories & authors'
        )
    )

    parser.add_argument(
        '--start',
        help='INT: start point',
        dest='start',
        type=int,
        required=False
    )

    args = parser.parse_args()

    start = int(args.start or DEFAULT_START)

    num_articles = get_number_of_articles()

    for offset in xrange(start, num_articles, 1000):
        os.system("python crawl_smt.py --limit=1000 --offset=%d" % offset)


if __name__ == "__main__":
    main()
