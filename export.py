import argparse
import datetime
import bibtexparser as bp

from collections import defaultdict


def read_bib(filename):
    """
    Parse bibtex file
    """
    with open(filename, 'r') as bibtex_file:
        bib_database = bp.load(bibtex_file)
    print(f"Read {len(bib_database.entries)} bib entries")
    return bib_database


def parse_link(link_string):
    """
    Parse the URL in the bibtex entry to a resolvable one.
    """
    REMOVE_PATTERNS = ["\\", ":URL"]
    new_string = link_string
    if link_string[0] == ":":
        new_string = new_string[1:]
    for pattern in REMOVE_PATTERNS:
        new_string = new_string.replace(pattern, "")
    return new_string


def classify_venue(venue_string, manual=None):
    """
    Classify the venue string (conference or journal ..) to any of the
    categories prespecified.

    Categories:
     - AI
     - HI
     - Deliberation
     - NLProc
    """
    AI_VENUES = ['AAAI', 'IJCAI']
    NLP_VENUES = ['Computational Linguistics', 'Argument Mining']
    DELIB_VENUES = ['Public Deliberation']
    HI_VENUES = ['Computer Supported Cooperative Work']

    AI_BADGE = "![ai-badge](/images/ai-badge.png)"
    HI_BADGE = "![hi-badge](/images/hi-badge.png)"
    NLP_BADGE = "![nlp-badge](/images/nlp-badge.png)"
    DELIB_BADGE = "![deliberation-badge](/images/deliberation-badge.png)"
    if manual is None:
        if any([string in venue_string for string in AI_VENUES]):
            return AI_BADGE
        elif any([string in venue_string for string in HI_VENUES]):
            return HI_BADGE
        elif any([string in venue_string for string in NLP_VENUES]):
            return NLP_BADGE
        elif any([string in venue_string for string in DELIB_VENUES]):
            return DELIB_BADGE
        else:
            print(f"Venue {venue_string} not assigned")
    else:
        if manual == 'AI':
            return AI_BADGE
        elif manual == 'HI':
            return HI_BADGE
        elif manual == 'NLP':
            return NLP_BADGE
        elif manual == 'DELIB':
            return DELIB_BADGE


def extract_common_info(entry):
    """
    Extract information that all types of bibtex entries should have
    """
    authors = entry['author']
    title = entry['title']
    year = entry['year'] if 'year' in entry else entry['date'].split('-')[0]
    timestamp = datetime.datetime.strptime(entry['timestamp'], "%Y-%m-%d")
    if len(entry['url']) > 0:
        link_string = f"Find at: [LINK]({parse_link(entry['url'])})"
    else:
        print(f"No link for entry added on {str(timestamp.strftime('%Y-%m-%d'))}: {entry['title']}")
        link_string = ""
    return authors, title, year, link_string, timestamp


def write_md(bib_entries, outfile):
    """
    Write parsed bibtex to Markdown
    """
    # Sort on date added, most recent first
    bib_entries.sort(key=lambda x: datetime.datetime.strptime(x['timestamp'], "%Y-%m-%d"), reverse=True)

    with open(outfile, 'w') as f:
        f.write("# Papers\n")
        current_timestamp = datetime.datetime(2100,1,1)
        for entry in bib_entries:
            entry_dd = defaultdict(lambda: "", entry)
            authors, title, year, link, timestamp = extract_common_info(entry_dd)
            if 'journal' in entry_dd:
                badge = classify_venue(entry_dd['journal'])
            elif 'booktitle' in entry_dd:
                badge = classify_venue(entry_dd['booktitle'])
            else:
                print(f"No badges for entry type {entry_dd['ENTRYTYPE']} titled {entry_dd['title'][:20]}..")
                badge = None
            # Print a header for which date the paper was added on
            if timestamp < current_timestamp:
                f.write(f"## {timestamp.date()}\n\n")
                current_timestamp = timestamp

            # Write entry
            f.write(f"- {authors} ({year}): __{title}__ {link}\n")
            if badge is not None:
                f.write(f"{badge}\n")
            f.write("\n\n")
    print("Done exporting!")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(epilog='v{}')
        parser.add_argument('-v', '--version', action='version', version='0.1')
        parser.add_argument('file', help='Input bibtex file to render')
        parser.add_argument('--outfile', default='exported/papers.md', help='Output Markdown filename')
        args = parser.parse_args()
    except Exception as e:
        print(e)
        exit(1)

    config = vars(args)
    print("Parameters:")
    for k, v in config.items():
        print(f"  {k:>21} : {v}")
    bib_db = read_bib(args.file)
    write_md(bib_db.entries, outfile=args.outfile)