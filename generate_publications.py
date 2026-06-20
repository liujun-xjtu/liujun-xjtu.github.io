#!/usr/bin/env python3
"""
Generate Hugo Blox publication pages from data/papers.yaml and output/papers-bibtex.json.
Creates:
  content/en/publication/<slug>/index.md + cite.bib
  content/zh/publication/<slug>/index.md + cite.bib
"""
import json, os, re, yaml
from pathlib import Path

# Load data
with open('data/papers.yaml', 'r', encoding='utf-8') as f:
    papers_data = yaml.safe_load(f)

with open('output/papers-bibtex.json', 'r', encoding='utf-8') as f:
    bibtex_data = json.load(f)

papers = papers_data.get('papers', [])

def slugify(title):
    """Create URL-safe slug from title."""
    # Remove special chars, keep alphanumeric and spaces
    s = re.sub(r'[^\w\s-]', '', title.lower())
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')[:100]

def parse_authors(author_str):
    """Parse author string like 'J. Zhang, Z. Wang, ...' into list of full names."""
    # Remove extra spaces around periods
    authors = [a.strip() for a in author_str.split(',')]
    result = []
    for a in authors:
        a = re.sub(r'\s+', ' ', a).strip()
        # Filter out "et al." entries which break Hugo author taxonomy on Windows
        if a and not re.match(r'^et\s+al\.?$', a, re.IGNORECASE):
            result.append(a)
    return result

def get_publication_type(venue):
    """Determine publication_type for Hugo Blox v2."""
    conference_keywords = [
        'AAAI', 'ACL', 'CVPR', 'NeurIPS', 'ICCV', 'EMNLP', 'SIGIR',
        'KDD', 'WWW', 'IJCAI', 'ACM MM', 'CIKM', 'COLING', 'NAACL',
        'ECML', 'APWeb', 'WSDM', 'ICSE', 'ICDE', 'ISWC', 'ISSRE',
        'ICBK', 'CCKS', 'NASAC',
        'Findings',
    ]
    for kw in conference_keywords:
        if kw.lower() in venue.lower():
            return ['paper-conference']
    return ['article-journal']

def match_bibtex(title):
    """Find matching BibTeX entry for a paper title."""
    # Exact match
    if title in bibtex_data:
        return bibtex_data[title]
    # Try stripped match
    clean = title.replace(':', '').replace('^', '').replace("'", '').strip()
    for k, v in bibtex_data.items():
        k_clean = k.replace(':', '').replace('^', '').replace("'", '').strip()
        if clean[:80].lower() == k_clean[:80].lower():
            return v
        if clean[:60].lower() in k_clean.lower() or k_clean[:60].lower() in clean.lower():
            return v
    return None

def create_publication_page(paper, bib_entry, lang='en'):
    """Create Hugo Blox publication index.md content."""
    title = paper[0]  # Title is first element
    authors = paper[1]  # Authors string
    venue = paper[2]  # Venue
    year = paper[3]  # Year

    # Parse authors into list
    author_list = parse_authors(authors)

    # Determine publication type
    pub_types = get_publication_type(venue)

    # Get DOI if available
    doi = bib_entry.get('doi') if bib_entry else None

    # Build frontmatter
    frontmatter = {
        'title': title,
        'authors': author_list,
        'date': f'{year}-01-01',
        'publishDate': f'{year}-01-01',
        'publication_types': pub_types,
        'publication': venue,
    }

    if doi:
        frontmatter['doi'] = doi

    # Abstract placeholder
    abstract = ''

    # Build YAML frontmatter manually for clean output
    lines = ['---']
    lines.append(f'title: "{title}"')
    lines.append('authors:')
    for a in author_list:
        lines.append(f'  - {a}')
    lines.append(f"date: '{year}-01-01'")
    lines.append(f"publishDate: '{year}-01-01'")
    lines.append('publication_types:')
    for pt in pub_types:
        lines.append(f'  - "{pt}"')
    lines.append('publication:')
    lines.append(f'  name: "{venue}"')
    if doi:
        lines.append('hugoblox:')
        lines.append('  ids:')
        lines.append(f'    doi: "{doi}"')
    if abstract:
        lines.append(f'abstract: "{abstract}"')
    lines.append('---')

    return '\n'.join(lines) + '\n'


# Create publication directories
base_dirs = {
    'en': Path('content/en/publication'),
    'zh': Path('content/zh/publication'),
}

for lang, base_dir in base_dirs.items():
    base_dir.mkdir(parents=True, exist_ok=True)

# Process all papers
created = 0
skipped = 0
errors = []

for paper in papers:
    title = paper[0]
    slug = slugify(title)
    bib_entry = match_bibtex(title)

    # Create page content
    page_content = create_publication_page(paper, bib_entry)

    # Write for both languages
    for lang, base_dir in base_dirs.items():
        pub_dir = base_dir / slug
        pub_dir.mkdir(parents=True, exist_ok=True)

        # Write index.md (overwrite to fix format)
        index_path = pub_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(page_content)

        # Write cite.bib if bibtex available
        if bib_entry and bib_entry.get('bibtex'):
            cite_path = pub_dir / 'cite.bib'
            with open(cite_path, 'w', encoding='utf-8') as f:
                f.write(bib_entry['bibtex'])

    created += 1
    if created % 20 == 0:
        print(f'  Created {created}/{len(papers)}...')

print(f'\nDone! Created {created} publication pages.')
print(f'Directories:')
print(f'  content/en/publication/ ({len(list(Path("content/en/publication").iterdir()))} entries)')
print(f'  content/zh/publication/ ({len(list(Path("content/zh/publication").iterdir()))} entries)')

# Count papers with cite.bib
en_bib = sum(1 for d in Path('content/en/publication').iterdir() if (d / 'cite.bib').exists())
zh_bib = sum(1 for d in Path('content/zh/publication').iterdir() if (d / 'cite.bib').exists())
print(f'Papers with cite.bib: {en_bib}')
