import requests

def get_raw_xml():
    # 1. Search
    url_search = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params_search = {
        'db': 'pubmed',
        'term': 'COVID-19 vaccine',
        'retmax': 1,
        'retmode': 'json'
    }
    r = requests.get(url_search, params=params_search)
    data = r.json()
    id_list = data.get('esearchresult', {}).get('idlist', [])
    
    if not id_list:
        print("No IDs found")
        return

    print(f"Fetching summary for ID: {id_list[0]}")

    # 2. Summary
    url_summary = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params_summary = {
        'db': 'pubmed',
        'id': ",".join(id_list),
        'version': '2.0',
        'retmode': 'xml'
    }
    r = requests.get(url_summary, params=params_summary)
    print("\nRAW XML:")
    print(r.text)

if __name__ == "__main__":
    get_raw_xml()

