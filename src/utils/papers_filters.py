from rapidfuzz import fuzz

def filterJurnals(papers, filter_file):
    """
    Filters papers based on a journal list.
    This is a stub implementation based on the lost file.
    """
    # In a real implementation, this would read the CSV and filter
    # For now, we return all papers to avoid breaking the flow
    return papers

def filter_min_date(papers, min_date):
    """
    Filters papers by minimum publication year.
    """
    filtered = []
    for p in papers:
        try:
            if p.year and int(p.year) >= min_date:
                filtered.append(p)
        except ValueError:
            pass
    return filtered

def similarStrings(a, b):
    """
    Calculates similarity between two strings.
    """
    return fuzz.ratio(a.lower(), b.lower())

