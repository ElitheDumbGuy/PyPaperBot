from analysis.openalex import OpenAlexClient

client = OpenAlexClient()
title = "Attention is all you need"
print(f"Searching for DOI for: {title}")
doi = client.get_doi_from_title(title)
print(f"Result: {doi}")

title2 = "Deep learning"
print(f"Searching for DOI for: {title2}")
doi2 = client.get_doi_from_title(title2)
print(f"Result: {doi2}")

