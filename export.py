import argparse
import bibtexparser as bp

from collections import defaultdict


def read_bib(filename):
    with open(filename, 'r') as bibtex_file:
        bib_database = bp.load(bibtex_file)
    print(f"Read {len(bib_database.entries)} bib entries")
    return bib_database


def parse_link(link_string):
    REMOVE_PATTERNS = ["\\", ":URL"]
    new_string = link_string[1:]
    for pattern in REMOVE_PATTERNS:
        new_string = new_string.replace(pattern, "")
    return new_string


def extract_common_info(entry):
    authors = entry['author']
    title = entry['title']
    year = entry['year'] if 'year' in entry else entry['date'].split('-')[0]
    link = parse_link(entry['file'])
    return authors, title, year, link


def write_md(bib_entries, outfile):
    with open(outfile, 'w') as f:
        f.write("# Papers\n")
        for entry in bib_entries:
            entry_dd = defaultdict(lambda: "", entry)
            authors, title, year, link = extract_common_info(entry_dd)
            publication = ""
            # if entry['ENTRYTYPE'] == 'article':
            #     publication = entry_dd['journal']
            # elif entry['ENTRYTYPE'] == 'inproceedings':
            #     publication = entry_dd['booktitle']
            # else:
            #     print(f"Unable to parse entry type: {entry['ENTRYTYPE']}")
            #     continue
            f.write(f"- {authors} ({year}): __{title}__ in {publication} Find at: [LINK]({link})\n\n")
    print("Done exporting!")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(epilog='v{}')
        parser.add_argument('-v', '--version', action='version', version='0.1')
        parser.add_argument('file', help='Input bibtex file to render')
        parser.add_argument('--outfile', default='papers.md', help='Output Markdown filename')
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