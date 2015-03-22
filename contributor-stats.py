

from glob import glob
from collections import Counter, defaultdict
from operator import itemgetter
import re
import matplotlib.pyplot as plt

# Match name, email and years in a line like this:
# # Kenneth Nielsen <k.nielsen81@gmail.com>, 2007-2012, 2015.
# NOTE: The email can also be encapsulated by ()
EMAIL = re.compile(r'# ?(.*) ?[<\(]([\w\.-]+@[\w\.-]+)[>\)](.*)')
YEARS = re.compile(r'[0-9]{2,5} ?-? ?[0-9]{0,5}')

#1998

def parse_year(year_str, years):
    if len(year_str) == 4:
        return int(year_str)

    # When in 2 digit version, look at the last year
    try:
        last_year = years[-1]
        for prefix in ['19', '20']:
            prefixed_year = int(prefix + year_str)
            if prefixed_year > last_year:
                return prefixed_year
        raise Exception('Could not prefix year')
    except IndexError:
        # Could do a fallback here: >95 then 1900 else 2000, but not necessary
        raise Exception('Short year {} at beginning of line'.format(year_str))


def parse_header_line(line, stats, contributors, statistics_by='contributor'):
    if "Copyright" in line:
        return
    match = EMAIL.match(line)
    if match:
        name, email, year_string = match.groups()
        if email not in contributors:
            contributors[email] = name

        years = []
        for year_str in YEARS.findall(year_string):
            if year_str == '':
                continue
            elif '-' in year_str:
                yearpair_strs = [year.strip() for year in year_str.split('-')]
                year1 = parse_year(yearpair_strs[0], years)
                year2 = parse_year(yearpair_strs[1], years + [year1])
                years += range(year1, year2 + 1)
            else:
                years.append(parse_year(year_str.strip(), years))
        for year in years:
            if statistics_by == 'contributor':
                stats[email][year] += 1
            else:
                stats[year][email] += 1

    
def gather_stats(statistics_by='contributor'):
    """Returns the year contributor statistics by contributor or year

    Args:
        statistics_by (str): States what the statistics should be organized by
            at the outer level. Can be 'contributor' or 'year'

    Returns:
        defaultdict: Returns a default dict of counters
    """
    stats = defaultdict(Counter)
    contributors = {}
    for filename in glob('*.po'):
        with open(filename) as file_:
            for line in file_:
                if line.startswith('#'):
                    parse_header_line(line.strip(), stats, contributors)
                else:
                    break

    return stats


def plot_contributors(stats):
    plots = []
    for email, counter in stats.items():
        if sum(counter.values()) > 9:
            data = sorted(counter.items(), key=itemgetter(0))
            x, y = zip(*data)
            plots.append((x, y, email))

    for x, y, label in plots:
        plt.plot(x, y, label=label)
    plt.legend()
    plt.show()


def main():
    stats = gather_stats()
    plot_contributors(stats)
            


if __name__ == '__main__':
    main()
