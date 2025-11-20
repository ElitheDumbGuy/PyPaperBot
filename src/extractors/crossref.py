import requests
from ..models.paper import Paper

def getPapersInfoFromDOIs(DOI, restrict):
    """
    Minimal replacement for Crossref.py.
    Fetches paper metadata from Crossref API.
    """
    paper = Paper(DOI=DOI)
    try:
        url = f"https://api.crossref.org/works/{DOI}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()['message']
            
            if 'title' in data:
                paper.title = data['title'][0]
            
            if 'created' in data:
                paper.year = str(data['created']['date-parts'][0][0])
                
            if 'author' in data:
                authors = []
                for a in data['author']:
                    name = f"{a.get('given', '')} {a.get('family', '')}"
                    authors.append(name.strip())
                paper.authors = ", ".join(authors)
                
            if 'container-title' in data:
                paper.jurnal = data['container-title'][0]
                
    except Exception as e:
        print(f"Error fetching Crossref data for {DOI}: {e}")
        
    return paper

