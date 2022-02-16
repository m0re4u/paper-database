import argparse
import datetime
import bibtexparser as bp

from collections import defaultdict, Counter

AI_VENUES = ['AAAI', 'IJCAI']
NLP_VENUES = [
    'Computational Linguistics',
    'Argument Mining',
    'Natural language learning',
    'Language resources and evaluation',
    'Joint Conference on Natural Language Processing',
    'COMMA',
    'Argument \\& Computation',
    'Empirical Methods in Natural Language Processing'
]
DELIB_VENUES = [
    'Public Deliberation',
    'Journal of E-Politics',
    'Administrative science',
    'Deliberative',
    'Government and Policy',
    'Comparative political studies',
    'Democratization',
    'Public Understanding of Science',
    'Political psychology',
    'Comparative European Politics',
    'Computer Supported Cooperative Work',
]
HI_VENUES = [
    'Computer Supported Cooperative Work'
    'human--computer interaction'
]

RL_VENUES = []

AI_BADGE = "![ai-badge](/images/ai-badge.png)"
HI_BADGE = "![hi-badge](/images/hi-badge.png)"
NLP_BADGE = "![nlp-badge](/images/nlp-badge.png)"
DELIB_BADGE = "![deliberation-badge](/images/deliberation-badge.png)"
RL_BADGE = "![rl-badge](/images/rl-badge.png)"


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
    badges_to_add = []
    if manual is None:
        # if any([string.lower() in venue_string.lower() for string in AI_VENUES]):
        #     badges_to_add.append(AI_BADGE)
        if any([string.lower() in venue_string.lower() for string in HI_VENUES]):
            badges_to_add.append(HI_BADGE)
        if any([string.lower() in venue_string.lower() for string in NLP_VENUES]):
            badges_to_add.append(NLP_BADGE)
        if any([string.lower() in venue_string.lower() for string in DELIB_VENUES]):
            badges_to_add.append(DELIB_BADGE)
        if any([string.lower() in venue_string.lower() for string in RL_VENUES]):
            badges_to_add.append(RL_BADGE)

    else:
        # if manual == 'AI':
        #     badges_to_add.append(AI_BADGE)
        if 'HI' in manual:
            badges_to_add.append(HI_BADGE)
        if 'NLP' in manual:
            badges_to_add.append(NLP_BADGE)
        if 'DELIB' in manual:
            badges_to_add.append(DELIB_BADGE)
        if 'RL' in manual:
            badges_to_add.append(RL_BADGE)
    return badges_to_add

def get_manual_badge(theme):
    tt = theme.strip().upper()
    if tt in 'AI':
        return AI_BADGE
    elif tt in 'DELIBERATION':
        return DELIB_BADGE
    elif tt in 'HI':
        return HI_BADGE
    elif tt in 'NLP':
        return NLP_BADGE
    elif tt in 'RL':
        return RL_BADGE
    else:
        print(f'Unknown badge for theme {theme} ({tt})')
        return None


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
        print(f"No link for entry added on: ({str(timestamp.strftime('%Y-%m-%d')):>12}) {entry['title'][:30]}..")
        link_string = ""
    if 'theme' in entry:
        themes = entry['theme'].split(',')
    else:
        themes = []
    return authors, title, year, link_string, timestamp, themes


def write_md(bib_entries, outfile):
    """
    Write parsed bibtex to Markdown
    """
    # Sort on date added, most recent first
    bib_entries.sort(key=lambda x: datetime.datetime.strptime(x['timestamp'], "%Y-%m-%d"), reverse=True)

    conf_list = []
    with open(outfile, 'w') as f:
        f.write("# Papers\n")
        current_timestamp = datetime.datetime(2100,1,1)
        for entry in bib_entries:
            entry_dd = defaultdict(lambda: "", entry)
            authors, title, year, link, timestamp, themes = extract_common_info(entry_dd)
            # Assign themes based on venue
            if 'journal' in entry_dd:
                badges = classify_venue(entry_dd['journal'])
                if len(badges) == 0:
                    conf_list.append(entry_dd['journal'].lower())
            elif 'booktitle' in entry_dd:
                badges = classify_venue(entry_dd['booktitle'])
                if len(badges) == 0:
                    conf_list.append(entry_dd['booktitle'].lower())
            else:
                print(f"No venue for entry type: ({entry_dd['ENTRYTYPE']:>15}) {entry_dd['title'][:30]}..")
                badges = []
            # Assign badges to manual themes
            for theme in themes:
                b = get_manual_badge(theme)
                if b is not None and b not in badges:
                    badges.append(b)
            # Print a header for which date the paper was added on
            if timestamp < current_timestamp:
                f.write(f"## {timestamp.date()}\n\n")
                current_timestamp = timestamp
            # Write entry
            f.write(f"- {authors} ({year}): __{title}__ ")
            for badge in badges:
                f.write(f"{badge}")
            f.write(f"{link}\n\n")
    print("---")
    print("Done exporting!")
    print("---")
    print("Unbadged venues mentioned more than twice: ")
    venues = '\n'.join({f'{v}: {k}' for k,v in Counter(conf_list).items() if v > 1})
    print(f"{venues}")


def check_duplicates(bib_db):
    all_ids = [x['ID'] for x in bib_db.entries]
    duplicates = set([x for x in all_ids if all_ids.count(x) > 1])
    print(f"Duplicate entries: {duplicates}")

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
    check_duplicates(bib_db)
    write_md(bib_db.entries, outfile=args.outfile)