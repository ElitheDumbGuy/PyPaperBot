Data Providers
Introduction

Data-providers entity gives access to the collection of sources that supply content to CORE. These include – Institutional repositories, disciplinary repositories, preprint servers, journals and publishers. Each data provider record includes details about the source, such as its name, OAI-PMH endpoint, metadata format, software used, institutional identifiers, and geographic location.

Data-providers response field descriptions is shown below:
Field Name 	Description 	Method for obtaining the value 	Searchable field 	Cardinality
'aliases' 	List of alternative names or acronyms for the institution. 	Research Organization Registry (ROR) 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=aliases:Lisboa 	multiple
'createdDate' 		Database 		single
'email' 	Contact email for the data provider. 	Manually curated and from oai-pmh 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=email:"napier.ac.uk" 	single
'homepageUrl' 	Homepage URL of the data provider. 	Manually curated and automatically detected 		single
'id' 	Unique identifier for the data provider. 	Database 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=id:"100"

Supports aggregation via POST.
Example - Body: { "aggregations": ["id"] } 	single
'institutionName' 	Name of the institution responsible for the repository or data provider. 	Research Organization Registry (ROR) 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=institutionName:Basel 	single
'location' 	Geographical location details about the data provider or repository, including country code, latitude, and longitude. Format -

"location":
 {
   "countryCode": "< ISO_country_code>",
   "latitude": < latitude_value>,
   "longitude": < longitude_value>
 }

	Manually curated or available at various repository sources 	Searchable with subfields via GET.
Example: https://api.core.ac.uk/v3/search/data-providers/?q=location.countryCode:se 	
'logo' 	CORE API URL to the logo image of the data provider. 	Manually curated 		single
'metadataFormat' 	Metadata format used. 	Automatically detected or manually curated 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=metadataFormat:"rioxx" 	single
'name' 	Name of the data provider. 	From db, manually curated and automated 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=name:Glasgow 	single
'oaiPmhUrl' 	Open Archives Initiative Protocol for Metadata Harvesting (OAI-PMH) endpoint URL of a repository. 	Manually curated and automatically added 		single
'openDoarId' 	Unique identifier of the repository from OpenDOAR. 	From matching with opendoar 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=openDoarId:1275

Supports aggregation via POST.
Example - Body: { "aggregations": ["openDoarId"] } 	single
'otherIdentifiers' 	External global identifiers for the institution including Global Research Identifier Database (GRID) ID. Format -

"otherIdentifiers":
   {
   "< identifier_type>": 
       {
       "preferred": "< preferred_identifier>",
       "all": "< all_identifiers>"
       }
   }

	Research Organization Registry (ROR) 		multiple
'rorId' 	Unique ROR (Research Organization Registry) identifier. 	Automatically detected by matching institutions and also manually curated 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/data-providers/?q=rorId:"https://ror.org/04ea70f07" 	single
'software' 	Software used by data-providers for managing digital repositories. Examples include - ‘EPrints’, ‘DSpace’, ‘WEKO’, ‘DigitalCommons / BEPress’, ‘ojs’, ‘Dataverse’ etc. 	Automatically detected 	Searchable using field lookup via GET.Example - https://api.core.ac.uk/v3/search/data-providers/?q=software:"DSpace" Supports aggregation via POST.Example - Body: { "aggregations": ["software"] } 	single
'type' 	Indicates the classification of the data provider. Possible values are REPOSITORY, JOURNAL 	Automatically detected based on repository features 		single

Authorizations:
NoneNone

Search Data Providers

Search through the CORE data providers entity using specific query parameters and fields. Below are detailed instructions and examples of how to perform targeted searches.

API Endpoint

GET https://api.core.ac.uk/v3/search/data-providers

Example Search

The following query retrieves all data providers in the US with "university" in the name of the data provider.

https: //api.core.ac.uk/v3/search/data-providers/?q=location.countryCode:us AND name:university

   def search_dp_by_id(id:str):
       url = "https://api.core.ac.uk/v3/search/data-providers"
       headers = {"Authorization": f"Bearer {apikey}"}
       params = {"q": f"id:"{id}"", "limit": 1}

           try:
               response = requests.get(url, headers=headers, params=params)
               if response.status_code == 200:
                   return response.json()
               else:
                   print(f"Error {response.status_code}: {response.text}")
                   return None
           except requests.exceptions.RequestException as e:
               print(f"Request failed: {e}")
               return None

More examples on data-providers field specific search is available here

Authorizations:
NoneNone

Search Data Providers using aggregation

POST request body example:

{
   "q": "climate change", 
   "aggregations": ["id"]
}

Example source code to aggregate results for outputs based on the above request body:

def search_with_aggregation(query):
   url = "https://api.core.ac.uk/v3/search/data-providers/aggregate"
   headers = {
       "Authorization": f"Bearer {apikey}",
       "Content-Type": "application/json"
   }

   data = {
       "q": query,
       "aggregations": ["id"]
   }

   try:
       response = requests.post(URL, json=data, headers=headers)
       if response.status_code == 200:
           print("Aggregation Results:")
           print(response.json())
       else:
           print(f"Error {response.status_code}: {response.text}")

   except requests.exceptions.RequestException as e:
       print(f"Request failed: {e}")

Authorizations:
NoneNone

Get a single data provider

Get a single data provider of CORE using the data provider id. Here you can see our data providers. If you add the prefix opendoar. You can also fetch data providers using the OpenDOARId. The API endpoint retrieves detailed metadata for a single data provider in CORE.

API Endpoint

GET https://api.core.ac.uk/v3/data-providers/{identifier}

where the {identifier} represents the data-provider id.

Example GET request - https://api.core.ac.uk/v3/data-providers/92
Example GET request By OpenDOAR ID - https://api.core.ac.uk/v3/data-providers/opendoar:1334

Authorizations:
NoneNone
path Parameters
identifier
required
	
integer

<DataProviderID> or opendoar:<OpenDOARId>
Responses

Response samples

    200

Content type
application/json
{

    "id": 86,
    "openDoarId": 300,
    "name": "Open Research Online",
    "email": "library-research-support@open.ac.uk",
    "uri": null,
    "oaiPmhUrl": "https://oro.open.ac.uk/cgi/oai2",
    "homepageUrl": "https://oro.open.ac.uk",
    "source": null,
    "software": "eprints",
    "metadataFormat": "rioxx",
    "createdDate": "2011-05-06T10:11:21+00:00",
    "location": 

{

    "countryCode": "gb",
    "latitude": 52.0333,
    "longitude": -0.7

},
"logo": "https://localhost:8000/data-providers/86/logo",
"type": "REPOSITORY",
"stats": null,
"rorId": "https://ror.org/05mzfcs16",
"institutionName": "The Open University",
"aliases": 
[

    "cy: Y Brifysgol Agored",
    "OU"

],
"otherIdentifiers": 
{

    "GRID": 

{},
"ISNI": 
{},
"FundRef": 
{},
"Wikidata": 

        {}
    }

}
Search outputs

Search through the outputs harvested from this data provider. The simple search is great for most of the queries but is limited to 10,000 items. See the section Querying large datasets to overcome this limit.
Authorizations:
NoneNone
path Parameters
identifier
required
	
integer\d+

The Data Provider ID
query Parameters
q
required
	
string
Default: ""

The query see the Query section on how to build a search query.
offset
required
	
integer
Default: "0"

The starting point in your search.
sort
required
	
string
Default: "relevance"

The way you want to sort the results. Recommended values are 'recency' and 'relevance'
limit
required
	
integer
Default: "10"

The size of your search, maximum size is 100 outputs per request.
Responses

Response samples

    200

Content type
application/json
{

    "totalHits": 10733,
    "limit": 1,
    "offset": 0,
    "scrollId": null,
    "results": [ ],
    "tooks": null,
    "esTook": null

}
Get statistics about a data provider

Get the aggregated data behind a Data Provider.

API Endpoint

GET https://api.core.ac.uk/v3/data-providers/{identifier}/stats

where the {identifier} represents the data-provider id. The statistics reflect the overall volume and status of content contributed by the data provider.

Example Request - https://api.core.ac.uk/v3/data-providers/122/stats

Authorizations:
NoneNone
path Parameters
identifier
required
	
integer\d+

The Data Provider ID
Responses

Response samples

    200

Content type
application/json
{

    "id": 86,
    "countMetadata": 47000,
    "countFulltext": 16795,
    "history": null

}
Statistics with options. OpenDOAR

Get the aggregated data behind a Data Provider and his history
Authorizations:
NoneNone
path Parameters
identifier
required
	
integer\d+

The Data Provider ID
Request Body schema: application/json
optional
identifier
required
	
integer
deposit_history
required
	
boolean
raw_stats
required
	
boolean
set
required
	
string
refresh
required
	
boolean
Responses

Request samples

    Payload

Content type
application/json
{

    "identifier": 0,
    "deposit_history": true,
    "raw_stats": true,
    "set": "string",
    "refresh": true

}
Response samples

    200

Content type
application/json
{

    "id": 0,
    "count_metadata": "string",
    "count_fulltext": "string",
    "history": 

[

    "string"

],
"source_stats": 
[

    "string"

],
"last_seen": 
[

    "string"

],
"set": 

    [
        "string"
    ]

}
Discovery
Discover full texts links.

This endpoint allows you to find links to full texts based on a DOI. The system will search through the CORE data and other external sources to provide you the best match.
Authorizations:
NoneNone
Request Body schema: application/json
required

Discovery parameters
doi
required
	
string
title
required
	
string
year
required
	
integer
eprints_id
required
	
string
plugin_id
required
	
string
referrer
required
	
string
Responses

Request samples

    Payload

Content type
application/json
{

    "doi": "string",
    "title": "string",
    "year": 0,
    "eprints_id": "string",
    "plugin_id": "string",
    "referrer": "string"

}
Response samples

    200

Content type
application/json
{

    "fullTextLink": "...",
    "source": "..."

}
Expert Finder
Expert finder

Expert finder
Authorizations:
NoneNone
Request Body schema: application/json
required

Recommendation parameters.
text
required
	
string
limit
required
	
string
identifier
required
	
string
abstract
required
	
string
authors
required
	
Array of strings
title
required
	
string
result_type
required
	
string
data_provider_id	
integer or null
Responses

Request samples

    Payload

Content type
application/json
{

    "text": "string",
    "limit": "string",
    "identifier": "string",
    "abstract": "string",
    "authors": 

    [
        "string"
    ],
    "title": "string",
    "result_type": "string",
    "data_provider_id": 0

}
Journals
Introduction

The Journals entity provides metadata about academic journals associated with the CORE collection. This includes journals directly supplied by CORE data providers and those referenced through metadata enrichment. Each journal object includes key information such as identifiers (e.g. ISSN, DOAJ ID), subject areas, language, publisher, and a link to a contributing data provider.

More details about the Journals response fields is as follows:
Field Name 	Description 	Method for obtaining the value 	Searchable field 	Cardinality
'dataProviderId' 	Unique identifier in CORE assigned for data-provider. 	Database 		single
'identifiers' 	List of unique identifiers associated with a journal, such as ISSNs, OAI identifiers, and URLs. Format -

"identifiers":
   [
   "< identifier_value>",
   "issn:< issn_value>",
   "oai:< oai_identifier>",
   "url:< journal_url>"
   ]

	From list 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/journals/?q="1744-9081" 	multiple
'language' 	Language used in the journal. 	Collected at submission time, either manually or automatically 		single
'publisher' 	Name of the publisher. 	Collected at submission time, either manually or automatically 		single
'subjects' 	List of domains associated with the journal. Possible values - ‘Medicine’, ‘Science’, ‘Social Sciences’, ‘Mathematics’, ‘Chemistry’, etc. 	Collected at submission time, either manually or automatically 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/journals/?q=subjects:Agriculture

Supports aggregation via POST.
Example - Body: { "aggregations": ["subjects"] } 	multiple
'title' 	Name of the journal. 	Collected at submission time, either manually or automatically 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/journals/?q=title:Revista 	single

Authorizations:
NoneNone

Search Journals

Search through the CORE data providers entity using specific query parameters and fields. Below are detailed instructions and examples of how to perform targeted searches.API Endpoint

GET https://api.core.ac.uk/v3/search/journals

Example Search
The following query retrieves 10 journals with "neuroscience" in the subject and "Brain" in the title:

https: //api.core.ac.uk/v3/search/journals?q=title:"Brain" AND subjects:"neuroscience"&limit=10

Example python source code to search journals by subject:

   def search_journal_by_subject(subject:str):
       url = "https://api.core.ac.uk/v3/search/journals"
       headers = {"Authorization": f"Bearer {apikey}"}
       params = {"q": f"subjects:"{subject}"", "limit": 1, "offset":1}

           try:
                   response = requests.get(url, headers=headers, params=params)
               if response.status_code == 200:
                   return response.json()
               else:
                   print(f"Error {response.status_code}: {response.text}")
                   return None
           except requests.exceptions.RequestException as e:
               print(f"Request failed: {e}")
               return None

More examples on journals field specific search is available here

Authorizations:
NoneNone

Search Journals using aggregation

POST request body example:

{
   "q": "climate change",
   "aggregations": ["subjects"]
}

def search_with_aggregation(query):
   url = "https://api.core.ac.uk/v3/search/journals/aggregate"
   headers = {
       "Authorization": f"Bearer {apikey}",
       "Content-Type": "application/json"
   }
   data = {
       "q": query,
       "aggregations": ["subjects"]
   }

   try:
       response = requests.post(url, json=data, headers=headers)

   if response.status_code == 200:
       print("Aggregation Results:")
       print(response.json())
   else:
       print(f"Error {response.status_code}: {response.text}")
   except requests.exceptions.RequestException as e:
       print(f"Request failed: {e}")

Aggregation response sample for query="climate change"

{'aggregations':
   {'subjects':
       {'climate change': 14,
       'Environmental sciences': 10,
       'GE1-350': 10,
       'Q': 7,
       'Science': 7,
       'G': 5,
       'Geography. Anthropology. Recreation': 5,
       'ecology': 4,
        .....................
       .....................
       'proteomics': 1,
       'renewable energies': 1,
       'risk management': 1,
       'sensors': 1,
       'social sustainability': 1}
    }
}

The journals API response fields that support aggregation can be viewed here.

Authorizations:
NoneNone

Get the Journal by identifier

Get a single journal based on its identifier in CORE. You can use the prefix issn: to search by ISSN. CORE journal data comes from multiple sources including members of the Directory of Open Access Journals (DOAJ) and Open Journal System repositories. We also aggregate open access content directly from publishers via our own custom solutions.
Authorizations:
NoneNone
path Parameters
identifier
required
	
string\w+:\d+.\d+

The Journal id in CORE. Use issn:ISSN to search by ISSN instead of the CORE identifier.
Responses

Response samples

    200

Content type
application/json
{

    "identifiers": 

[

    "oai:doaj.org/journal:fc6f85dc44ed458b983814eb3628da53",
    "issn:1179-1497",
    "url:http://doaj.org/toc/fc6f85dc44ed458b983814eb3628da53"

],
"language": "English",
"publisher": "Dove Medical Press",
"subjects": 

    [
        "neuropsychiatry",
        "behavioral complications",
        "HIV research",
        "AIDS research",
        "pathology",
        "LCC:Neurosciences. Biological psychiatry. Neuropsychiatry",
        "LCC:RC321-571",
        "LCC:Internal medicine",
        "LCC:RC31-1245",
        "LCC:Medicine",
        "LCC:R"
    ],
    "dataProviderId": "645",
    "title": "Neurobehavioral HIV Medicine"

}
Statistics

Get the aggregated data for the corresponding Journal. This data matches the data coming from the associated Data Provider.
Authorizations:
NoneNone
path Parameters
identifier
required
	
string\w+:\d+.\d+

The Journal ID use issn: for ISSNs.
Responses

Response samples

    200

Content type
application/json
{

    "identifier": 0,
    "count_metadata": "string",
    "count_fulltext": "string",
    "doi_count": "string"

}
Outputs
Introduction

Outputs are the raw, source-specific representations of research works as harvested directly from individual data providers (e.g., institutional repositories). Unlike Works, Outputs are not deduplicated or enriched — they reflect the original metadata exactly as provided by the source. Each Output is a single harvested item from a repository, preprint server, or journal and includes detailed metadata such as authors, identifiers, publication date, full text (when available), repository source information and more.

Outputs response field details are described in the following table.
Field Name 	Description 	Method for obtaining the value 	Searchable field 	Cardinality
'abstract' 	Abstract of the document. 	OAI-PMH 		single
'acceptedDate' 	Date when the article was accepted for publication. Format -

YYYY-MM-DDTHH:MM:SS

	Crossref 	Supports aggregation via POST.Example - Body: { "aggregations": ["acceptedDate"] } 	single
'authors' 	List of author 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=authors:Schmidt 	multiple
'contributors' 	List of entities (editors, translators, organisations etc.) responsible for making contributions to the resource. 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=contributors:Schmidt&limit=50 	multiple
'createdDate' 	Timestamp when the output record was initially created in CORE. Format -

YYYY-MM-DDTHH:MM:SS±HH:MM

	Database 		single
'deleted' 	Shows the status of the document, if it is accessible or not. Format - "deleted": "< status>", where status is ALLOWED (accessible) or DELETED (non-accessible). 	Database 	Supports aggregation via POST. Example - Body: { "aggregations": ["deleted"] } 	single
'depositedDate' 	The timestamp indicating when the article was initially deposited in the institutional repository. Format -

YYYY-MM-DDTHH:MM:SS±HH:MM

	OAI-PMH 	Supports aggregation via POST.Example - Body: { "aggregations": ["depositedDate"] } 	single
'disabled' 	Boolean flag (true / false) that shows if the document is disabled or restricted in the system. 	Database 		single
'documentType' 	List of types of the outputs. Example types are ‘research’, ‘thesis’, ‘unknown’, ‘slides’, ‘research article’, 'text', 'journal article', 'conference paper', 'review', 'book', 'other', 'report', 'project', 'doctoral thesis’, 'book part', 'working paper', 'dataset', 'master thesis', 'presentation', 'bachelor thesis', 'lecture', 'conference proceedings', 'image', 'software', 'conference object', 'patent', 'video', 'annotation', 'conference poster', 'musical notation', 'preprint', 'technical report', ‘interactive resource’, ‘research proposal’, ‘review article’. 	Using machine learning-based approach when full-text is available, otherwise with an interpretation of the values from dc.subject and dc.type 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=documentType:thesis
Supports aggregation via POST.
Example - Body: { "aggregations": ["documentType"] } 	multiple
'doi' 	DOI of the output. 	OAI-PMH and Crossref matching 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=doi:"10.1007/s002210100705"
Supports aggregation via POST.
Example - Body: { "aggregations": ["doi"] } 	single
'downloadUrl' 	Direct link to download the full-text document in PDF format (if available). More information about our PDF download policy can be viewed here 	Database 	Supports aggregation via POST.
Example - Body: { "aggregations": ["downloadUrl"] } 	
'fullText' 	Full-text of the output. 	From downloading and parsing the pdf 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=fullText:Ontario 	single
'fulltextStatus' 	Indicates whether full text is present (enabled) or not (disabled). 	Database 		single
'id' 	Unique CORE identifier (CORE_ID) 	Database 	Searchable using field lookup via GET.Example - https://api.core.ac.uk/v3/search/outputs/?q=id:216874849
Supports aggregation via POST. Example - Body: { "aggregations": ["id"] } 	single
'identifiers' 	External unique identifiers for the document, such as DOI and OAI. Format -

"identifiers":
{
   "doi": "< doi_value>",
   "oai": "< oai_identifier>"
}

	OAI-PMH, Crossref and any other identifier provider 		single
'journals' 	List of metadata (journal title and identifiers including issn) about the journal associated with the document. Format -

"journals": 
[{ 
   "title": "< journal_title>",
   "identifiers": 
       [ 
       "< identifier_1>", 
       "< identifier_2>", 
       ...
       ]
}]

	Issn matching and CORE records 		
'language' 	Language of the document including the name and code. Format -

“language”:
 {
   "code":"< ISO_639_language_code>",
   "name":"< name_of_the_language>"
 }

Example language codes: 'en' (English), 'es' (Spanish), 'pt' (Portuguese), etc. 	OAI-PMH and machine learning-based approach from fullText 	Supports aggregation via POST.
Example - Body: { "aggregations": ["language"] } 	single
'lastUpdate' 	Last update timestamp and follows the format -

YYYY-MM-DDTHH:MM:SS±HH:MM

	Database 		single
'license' 	License under which the document is published. Possible values - ‘http://creativecommons.org/licenses/by/2.0/’, ‘http://creativecommons.org/licenses/by/3.0/’, ‘http://creativecommons.org/licenses/by-nc-sa/3.0/’, ‘http://creativecommons.org/licenses/by/4.0/’, ‘https://creativecommons.org/licenses/by-sa/4.0’, ‘https://creativecommons.org/licenses/by-nc/4.0/’. Frequently used licenses are - CC-BY
CC-BY-SA
CC-BY-ND
CC-BY-NC
CC-BY-NC-SA 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=license:"http://creativecommons.org/licenses/by/3.0" 	single
'links' 	List of different types of CORE URLs associated with the document. Format -

"links":
 [
   { 
   "type": "< link_type>",
   "url": "< corresponding_url>"
   },
    ...
]

Example link types are 'download', 'reader', 'display', 'thumbnail_l', 'thumbnail_m'. 	CORE records 		multiple
'oai' 	OAI identifier. Format - oai:repository.domain.com:identifier 	OAI-PMH 	Searchable using field lookup via GET.Example - https://api.core.ac.uk/v3/search/outputs/?q=oai:"oai:researchonline.lshtm.ac.uk:3689"
Supports aggregation via POST.
Example - Body: { "aggregations": ["oai"] } 	single
'publishedDate' 	Timestamp when the output was first published. Format -

YYYY-MM-DDTHH:MM:SS+TZ

	OAI-PMH and Crossref 	Supports aggregation via POST.
Example - Body: { "aggregations": ["publishedDate"] } 	single
'publisher' 	Name of the publisher. 	OAI-PMH, Crossref, DOI prefixes. All made uniform using publisher names from crossref 		single
'references' 	List of references cited in the output. Each reference contains metadata such as id (CORE ID), title, authors, date, doi, raw (full citation text), and cites (outputs that cite the given document). 	From full-text parsing when available 		multiple
'repositories' 	Information about repositories holding the output. Format -

"repositories": 
 {
   "id": "< repository_id>",
   "openDoarId": < open_doar_id>,
   "name": "< repository_name>",
   "urlHomepage": "< homepage_url>,
   "uriJournals": "< journals_uri>",
   "physicalName": "< physical_repository_name>",
   "roarId": < roar_id>,
   "baseId": < base_id>,
   "pdfStatus": "< pdf_availability_status>",
   "nrUpdates": < number_of_updates>,
   "lastUpdateTime": "< last_update_timestamp>"
} 

	Database 		single
'repositoryDocument' 	Metadata information of the output including its id and different timestamps. Format -

"repositoryDocument":
 {
   "id": < CORE_ID>,
   "depositedDate": "< deposit_date>",
   "publishedDate": "< publication_date>",
   "updatedDate": "< last_updated_date>",
   "acceptedDate": "< acceptance_date>",
   "createdDate": "< record_creation_date>"
 } 

	Database 		single
'sdg' 	Multi-label Sustainable Development Goals (SDG) classification. Format -

[
   {
   "type": "< SDG_Class>",
   "score": "< confidence_score>"
   },
   ...
]

Example SDG_Class is ‘SDG04’ 	From multi-label machine learning-based SDG classifier 		multiple
'setSpecs' 	List of IDs used to filter metadata records based on predefined groupings or categories within a repository. 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=setSpecs:7374617475733D707562 	multiple
'sourceFulltextUrls' 	List of URLs to view the full-text of the document. 	Database 		multiple
'subjects' 	List with possible values - ''Article', 'Text', 'NonPeerReviewed', 'Thesis', 'PeerReviewed’, 'Peer-reviewed Article', 'Journal', 'Journal Article', 'posted-content', ''publication-article', 'preprint', 'Student thesis', 'Peer reviewed', 'Book'' 	OAI-PMH 	Supports aggregation via POST.
Example - Body: { "aggregations": ["subjects"] } 	multiple
'tags' 	List of topical labels associated with the article 	OAI-PMH 		multiple
'title' 	Title of the article. 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=title:"sustainable development goals" 	single
'updatedDate' 	Date in which the article was updated in CORE. Format -

YYYY-MM-DDTHH:MM:SS±HH:MM

	Database 		single
'urls' 	List of URLs pointing to resources related to the output. 	OAI-PMH 		multiple
'yearPublished' 	Year the document was published. 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/outputs/?q=yearPublished:2016 	single

Authorizations:
NoneNone

Search Outputs

Search through the CORE outputs entity using specific query parameters and fields. Below are detailed instructions and examples of how to perform targeted searches.

API Endpoint

GET https://api.core.ac.uk/v3/search/outputs

Example Search

The following query retrieves up to 25 outputs that meet the following conditions: The documentType is "research" and the output contains license information (i.e., the license field is not empty).

https://api.core.ac.uk/v3/search/outputs/?q=documentType:"research" AND exists:license&limit=25

Example python source code to search outputs full text by keywords:

   def search_outputs_by_keywords(keywords:str):
       url = "https://api.core.ac.uk/v3/search/outputs"
       headers = {"Authorization": f"Bearer {apikey}"}
       params = {"q": f"fullText:"{keywords}"", "limit": 5}

           try:
               response = requests.get(url, headers=headers, params=params)
               if response.status_code == 200:
                   return response.json()
               else:
                   print(f"Error {response.status_code}: {response.text}")
                   return None
           except requests.exceptions.RequestException as e:
               print(f"Request failed: {e}")
               return None

More examples on field specific search is available here

Authorizations:
NoneNone

Search Outputs using aggregation

POST request body example:

{
"q": "climate change",
"aggregations": ["documentType"]
}

Example source code to aggregate results for outputs based on the above request body:

def search_with_aggregation(query):
   url = "https://api.core.ac.uk/v3/search/outputs/aggregate"
   headers = {
       "Authorization": f"Bearer {apikey}",
       "Content-Type": "application/json"
   }

   data = {
       "q": query,
       "aggregations": ["documentType"]
   }

   try:
       response = requests.post(URL, json=data, headers=headers)

       if response.status_code == 200:
           print("Aggregation Results:")
           print(response.json())
       else:
           print(f"Error {response.status_code}: {response.text}")
   except requests.exceptions.RequestException as e:
       print(f"Request failed: {e}")

Aggregation response sample for query="climate change"

{
   'aggregations':
       {'documentType':
           {'thesis': 356641,
           'research article': 306314,
           'research': 297313,
           'text': 202666,
           'review': 124039,
           'journal article': 88727,
           'unknown': 56630,
           'book': 31395,
           ................... 
           ................... 
           'data paper': 7,
           'project deliverable': 4,
           'sound': 2,
           'technical documentation': 2,
           'musical notation': 1,
           'website': 1}
       }
}

Authorizations:
NoneNone

Get a single Output

The API endpoint retrieves a single Output from the CORE database using its unique identifier.

API Endpoint

GET https://api.core.ac.uk/v3/outputs/{identifier}

where {identifier} corresponds to the CORE ID of the output.

Example GET Request - https://api.core.ac.uk/v3/outputs/80549003

Authorizations:
NoneNone
path Parameters
identifier
required
	
string\w+

The CORE ID of the output.
Responses

Response samples

    200

Content type
application/json
{

    "accepted_date": "2019-08-24T14:15:22Z",
    "authors": 

[

    "string"

],
"contributors": 
[

    "string"

],
"created_date": "2019-08-24T14:15:22Z",
"data_provider": 
[

    "string"

],
"deposited_date": "2019-08-24T14:15:22Z",
"abstract": "string",
"document_type": 
[

    "string"

],
"versions": 
[

    "string"

],
"doi": "string",
"oai": "string",
"download_url": "string",
"full_text": "string",
"id": 0,
"identifiers": 
[

    {}

],
"title": "string",
"language": { },
"published_date": "2019-08-24T14:15:22Z",
"publisher": { },
"references": 
[

    {}

],
"source_fulltext_urls": 
[

    "string"

],
"updated_date": "2019-08-24T14:15:22Z",
"year_published": "string",
"links": 
[

    "string"

],
"tags": 
[

    "string"

],
"set_specs": 
[

    "string"

],
"fulltext_status": "string",
"subjects": 
[

    "string"

],
"deleted": "string",
"journals": 
[

    { }

],
"repositories": 
[

    { }

],
"repository_document": { },
"urls": 
[

    "string"

],
"license": "string",
"orcids": 
[

    null

],
"disabled": 0,
"last_update": "2019-08-24T14:15:22Z",
"sdg": 

    [
        "string"
    ]

}
Download output file

The API endpoint allows you to download the binary file (e.g., PDF) associated with a specific output in the CORE repository.

API Endpoint

GET https://api.core.ac.uk/v3/outputs/{identifier}/download

where {identifier} is the CORE ID of the output.

Example GET Request - https://api.core.ac.uk/v3/outputs/80549003/download
More details regarding the PDF download policy is available here

Authorizations:
NoneNone
path Parameters
format	
string
Enum: "tei" "pdf" "txt" "raw"

The format of the download. Currently only PDF is supported.
identifier
required
	
string\w+
Responses

Response samples

    200

Content type
application/pdf

...%PDF%...

Historical data for an output

The API endpoint retrieves the historical OAI-PMH XML records for a specific output. This includes all available versions of the metadata for that output since the beginning of CORE harvesting.

API Endpoint

GET https://api.core.ac.uk/v3/outputs/{identifier}/history

where {identifier} is the CORE ID of the output.

Example GET Request - https://api.core.ac.uk/v3/outputs/80549003/history

Authorizations:
NoneNone
path Parameters
identifier
required
	
string\w+
Responses

Response samples

    200

Content type
application/json
{

    "accepted_date": "2019-08-24T14:15:22Z",
    "authors": 

[

    "string"

],
"contributors": 
[

    "string"

],
"created_date": "2019-08-24T14:15:22Z",
"data_provider": 
[

    "string"

],
"deposited_date": "2019-08-24T14:15:22Z",
"abstract": "string",
"document_type": 
[

    "string"

],
"versions": 
[

    "string"

],
"doi": "string",
"oai": "string",
"download_url": "string",
"full_text": "string",
"id": 0,
"identifiers": 
[

    {}

],
"title": "string",
"language": { },
"published_date": "2019-08-24T14:15:22Z",
"publisher": { },
"references": 
[

    {}

],
"source_fulltext_urls": 
[

    "string"

],
"updated_date": "2019-08-24T14:15:22Z",
"year_published": "string",
"links": 
[

    "string"

],
"tags": 
[

    "string"

],
"set_specs": 
[

    "string"

],
"fulltext_status": "string",
"subjects": 
[

    "string"

],
"deleted": "string",
"journals": 
[

    { }

],
"repositories": 
[

    { }

],
"repository_document": { },
"urls": 
[

    "string"

],
"license": "string",
"orcids": 
[

    null

],
"disabled": 0,
"last_update": "2019-08-24T14:15:22Z",
"sdg": 

    [
        "string"
    ]

}
Download raw XML record for an output

The API endpoint retrieves the raw XML metadata record associated with a specific output.

API Endpoint

GET https://api.core.ac.uk/v3/outputs/{identifier}/raw

where {identifier} is the CORE ID of the output.

Example GET Request - https://api.core.ac.uk/v3/outputs/80549003/raw

Authorizations:
NoneNone
path Parameters
identifier
required
	
string\w+
Responses

Response samples

    200

Content type
application/xml

...<records>...

Get statistics about an output

This API endpoint retrieves statistical and date-related metadata associated with a specific output. It includes information such as the published date, deposited date, updated date, accepted date and created date.

API Endpoint

GET https://api.core.ac.uk/v3/outputs/{identifier}/stats

where {identifier} is the CORE ID of the output.

Example GET Request - https://api.core.ac.uk/v3/outputs/80549003/stats

Authorizations:
NoneNone
path Parameters
identifier
required
	
string\w+

The CORE ID
Responses

Response samples

    200

Content type
application/json
{

    "id": 0,
    "deposited_date": "2019-08-24T14:15:22Z",
    "published_date": "2019-08-24T14:15:22Z",
    "updated_date": "2019-08-24T14:15:22Z",
    "accepted_date": "2019-08-24T14:15:22Z",
    "created_date": "2019-08-24T14:15:22Z"

}
Recommender
Recommend.

Recommends records in the CORE collection related to the input. You can request recommendations for a specific CORE record using the core: prefix or by passing any identifier. You can also request recommendations based on a more generic text entry. The more information you send to the recommender engine the more accurate the recommendation will be.
Authorizations:
NoneNone
Request Body schema: application/json
required

Recommendation parameters.
text
required
	
string
limit
required
	
string
identifier
required
	
string
abstract
required
	
string
authors
required
	
Array of strings
title
required
	
string
result_type
required
	
string
data_provider_id	
integer or null
Responses

Request samples

    Payload

Content type
application/json
{

    "text": "string",
    "limit": "string",
    "identifier": "string",
    "abstract": "string",
    "authors": 

    [
        "string"
    ],
    "title": "string",
    "result_type": "string",
    "data_provider_id": 0

}
Response samples

    200404

Content type
application/json
{

    "accepted_date": "2019-08-24T14:15:22Z",
    "authors": 

[

    "string"

],
"contributors": 
[

    "string"

],
"created_date": "2019-08-24T14:15:22Z",
"data_provider": 
[

    "string"

],
"deposited_date": "2019-08-24T14:15:22Z",
"abstract": "string",
"document_type": 
[

    "string"

],
"versions": 
[

    "string"

],
"doi": "string",
"oai": "string",
"download_url": "string",
"full_text": "string",
"id": 0,
"identifiers": 
[

    {}

],
"title": "string",
"language": { },
"published_date": "2019-08-24T14:15:22Z",
"publisher": { },
"references": 
[

    {}

],
"source_fulltext_urls": 
[

    "string"

],
"updated_date": "2019-08-24T14:15:22Z",
"year_published": "string",
"links": 
[

    "string"

],
"tags": 
[

    "string"

],
"set_specs": 
[

    "string"

],
"fulltext_status": "string",
"subjects": 
[

    "string"

],
"deleted": "string",
"journals": 
[

    { }

],
"repositories": 
[

    { }

],
"repository_document": { },
"urls": 
[

    "string"

],
"license": "string",
"orcids": 
[

    null

],
"disabled": 0,
"last_update": "2019-08-24T14:15:22Z",
"sdg": 

    [
        "string"
    ]

}
Search
CORE API Query Language

The CORE API query language allows users to explore the CORE collection and construct complex queries using various operators. The following table outlines the available operators and their usage:
Operator 	Accepted symbols 	Meaning
And 	AND, +, space 	Logical binary AND. Used to retrieve results matching all conditions.
Or 	OR 	Logical binary OR. Used to retrieve results matching at least one condition.
Grouping 	(...) 	Used to prioritize and group elements of the query.
Field lookup 	field_name:value 	Used to search specific fields (e.g., title:"Artificial Intelligence").
Range queries 	fieldName(>, <, >=, <=) value 	For numeric and date fields, specifies a range of values.
Exists queries 	_exists_:fieldName 	Returns all items where the specified field is not empty.
Examples of Query Usage
1. Field lookup: Search for works with "Machine Learning" in the title

q=title:"Machine Learning"


2. Range queries: Search for works published after 2018

q=yearPublished>2018


3. AND: Search for works by multiple authors

q=authors:"Jane Doe" AND authors:"John Smith"


4. OR: Search works with "AI" in the title or "Deep Learning" in the full-text

q=title:"AI" OR fullText:"Deep Learning"


5. Exists queries: Find works with full-text available

q=exists:fullText


6. Grouping: Search works using multiple conditions

q=(title:"Artificial Intelligence" OR title:"Machine Learning") AND yearPublished>"2020"

Authorizations:
NoneNone

Keyword Queries and Phrase Matching

The CORE API allows flexible text matching through both keyword queries and phrase searches:

1. Keyword search (unquoted): When search terms are unquoted, CORE will match documents where the field contains any or all of the words, in any order.

q=title:Attention is all you need

This returns documents where the title contains any or all of the words: 'Attention', 'is', 'all', 'you', 'need'.

q=title:attention-is-all-you-need

This returns documents where the title contains all of the words: 'Attention', 'is', 'all', 'you', 'need' and the order does not matter.

2. Phrase search (quoted): When the search term is wrapped in double quotes, CORE matches documents containing that exact phrase, in order.

q=title:"Attention is all you need"

This returns documents where the title exactly matches that phrase.

Authorizations:
NoneNone

Free Text Search - Searching without field lookup

If no search lookup field is specified, the query is processed through all searchable fields.

q=scientometrics

This retrieves results where the term 'scientometrics' appears anywhere in the document’s metadata, enabling broad and flexible discovery across the complete CORE collection.

Authorizations:
NoneNone

Search using aggregation

The CORE API provides an aggregation feature to summarise and group search results based on specific fields. Aggregation queries differ from normal search queries as they provide summarised counts instead of detailed individual document records. To get the details of records, please check the CORE API Query Language page.
Aggregation Endpoint Structure

POST https://api.core.ac.uk/v3/search/{entityType}/aggregate

Replace {entityType} with one of the supported entities.
Request Body Format

{
   "q": "< search_query>", 
   "aggregations": ["< field_1>", "< field_2>", "..."]
}

Field	Type	Description
q	string	The query string is written using CORE’s query language.
aggregations	List	A list of fields to aggregate results by. Only supported fields are allowed.
Note: The aggregation feature does not support all fields returned by the API entity responses. Only certain fields can be used effectively.

For instance, you can aggregate works using the following fields:

"yearPublished"
"authors"
"dataProvider"
"documentType"
"publishedDate"
"updatedDate"
"language"
"publisher"
"fieldOfStudy"


Outputs can be aggregated using the following fields:

"acceptedDate"
"authors"
"contributors"
"depositedDate"
"documentType"
"language"
"publishedDate"
"subjects"


Data-providers entity supports following aggregations:

"software"


Following fields from Journals entity supports aggregation:

"subjects"

Refer to the entity-specific documentation for more information.

Authorizations:
NoneNone

Search through all CORE entities using HTTP Post

The CORE API also supports searching entities using POST requests, which allows complex queries to be passed in the JSON request body. This is functionally equivalent to using the GET search endpoint but is especially useful for more advanced use cases, such as:

    Long or complex query strings that exceed URL length limits
    Automated systems and UI integrations that build dynamic queries
    Filtering with precise, structured JSON payloads

API Endpoint

POST https://api.core.ac.uk/v3/search/{entityType}

Replace {entityType} with one of the supported entities.

Authorizations:
NoneNone
path Parameters
entityType
required
	
string
Enum: "works" "outputs" "data-providers" "journals"

Type of the entity
Request Body schema: application/json
required

Search parameters in JSON format.
q
required
	
string

Search query (use specific fields like doi, title, authors, etc.)
scroll	
boolean

Enable scroll pagination for large result sets.
offset	
integer
Default: 0

Offset for pagination.
limit	
integer
Default: 10

Maximum number of results to return.
stats	
boolean
Default: false

Include search statistics (can slow down the response).
Responses

Request samples

    Payload

Content type
application/json
{

    "q": "machine learning",
    "scroll": false,
    "offset": 0,
    "limit": 10,
    "stats": false

}
Response samples

    200

Content type
application/json
{

    "total_hits": 0,
    "limit": 0,
    "offset": 0,
    "scroll_id": "string",
    "results": 

[

    { }

],
"tooks": 

    [
        "string"
    ],
    "es_took": 0,
    "search_id": "string"

}
Search through all CORE entities

The CORE API search allows you to perform comprehensive searches across multiple entities, including works, outputs, data-providers, and journals.
Authorizations:
NoneNone
path Parameters
entityType
required
	
string
Enum: "works" "outputs" "data-providers" "journals"

Type of the entity
query Parameters
q
required
	
string

Search query (use specific fields like doi, title, authors, etc.)
scroll	
boolean

This parameter is useful for results sets bigger than 10.000 items. By setting it to true you enable the scroll pagination.
offset	
integer
Default: 0

The offset from the result set where you want the result to start. Needed for pagination.
limit	
integer
Default: 10

The maximum size of your search results. The result set may be smaller than the limit.
stats	
bool
Default: false

If set to true the search results will include statistics related to the entity. This property has an impact on the response speed.
Responses

Response samples

    200

Content type
application/json
{

    "total_hits": 0,
    "limit": 0,
    "offset": 0,
    "scroll_id": "string",
    "results": 

[

    { }

],
"tooks": 

    [
        "string"
    ],
    "es_took": 0,
    "search_id": "string"

}
Aggregate CORE entities based on a search query

The CORE API provides an aggregation feature to summarise and group search results based on specific fields. Aggregation queries differ from normal search queries as they provide summarised counts instead of detailed individual document records. To get the details of records, please check the CORE API Query Language page.
Aggregation Endpoint Structure

POST   https://api.core.ac.uk/v3/search/{entityType}/aggregate

Replace {entityType} with one of the supported entities.
Authorizations:
NoneNone
path Parameters
entityType
required
	
string
Enum: "works" "outputs" "data-providers" "journals"

Type of the entity
Request Body schema: application/json
required

Search parameters in JSON format.
q	
string or null
scroll	
boolean or null
offset	
integer or null
limit	
integer or null
scroll_id	
string or null
entity_id	
string or null
entity_type
required
	
string
stats
required
	
bool

If set to true the search results will include statistics related to the entity. This property has an impact on the response speed.
raw_stats
required
	
bool

If set to true the search results will include statistics related to the raw datasource of the entity if available. This property has an impact on the response speed.
exclude
required
	
Array of strings

Fields to exclude from the response.
sort
required
	
string

Fields to sort the results by. FIELD_NAME:asc|desc
accept
required
	
string

Download CSV file. text\/csv
measure
required
	
boolean
Responses

Request samples

    Payload

Content type
application/json
{

    "q": "string",
    "scroll": true,
    "offset": 0,
    "limit": 0,
    "scroll_id": "string",
    "entity_id": "string",
    "entity_type": "string",
    "stats": null,
    "raw_stats": null,
    "exclude": 

    [
        "string"
    ],
    "sort": "string",
    "accept": "string",
    "measure": true

}
Response samples

    200

Content type
application/json
{

    "total_hits": 0,
    "limit": 0,
    "offset": 0,
    "scroll_id": "string",
    "results": 

[

    { }

],
"tooks": 

    [
        "string"
    ],
    "es_took": 0,
    "search_id": "string"

}
Works
Introduction

Works represent individual pieces of scholarly research, such as research articles, theses, preprints, conference papers, and more. Each Work in CORE is a deduplicated and enriched representation of one or more underlying Outputs that have been harvested from different sources (repositories or journals).

The following table describes the Works API response fields:
Field Name 	Description 	Method for obtaining the value 	Searchable field 	Cardinality
'abstract' 	A summary of the work. 	OAI-PMH. The value is populated from the output with abstract != NULL. 	Searchable using field lookup via GET.Example - https://api.core.ac.uk/v3/search/works/?q=abstract:"bibliometrics" 	single
'acceptedDate' 	Date when the record was accepted for publication. Format -

YYYY-MM-DDTHH:MM:SS

	Crossref 	Supports aggregation via POST.Example - Body: { "aggregations": ["acceptedDate"] } 	single
'arxivId' 	Unique identifier assigned to the record in arXiv. Format -

YYMM.number

	Obtained from arXiv or retrieved from the deduplicated group if any of the output includes a relation to an ArXiv URL. 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=arxivId:1905.13497

Supports aggregation via POST.
Example - Body: { "aggregations": ["arxivId"] } 	single
'authors' 	List of author names. Format -

[
   {"name": < author_name>},
   ...
]

	OAI-PMH or enriched by obtaining values from output with the most number of authors from the deduplicated group. 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=authors:David

Supports aggregation via POST.
Example - Body: { "aggregations": ["authors"] } 	multiple
'citationCount'* 	Number of citations received. 	Microsoft Academic Graph (MAG) 	Supports aggregation via POST.

Example - Body: { "aggregations": ["citationCount"] } 	single
'contributors' 	List of entities (editors, translators, organisations etc.) responsible for making contributions to the resource. 	OAI-PMH 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=contributors:CiteSeerX

Supports aggregation via POST.

Example - Body: { "aggregations": ["contributors"] } 	multiple
'createdDate' 	Timestamp when the record was initially created in CORE. Format -

YYYY-MM-DDTHH:MM:SS

	Database 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=createdDate:"2016-06-16T16:34:27"

Supports aggregation via POST.

Example - Body: { "aggregations": ["createdDate"] } 	single
'dataProviders' 	List of data-provider information. Format -

"dataProviders": 
[{ 
   "id": < data_provider_id>, 
   "name": "< name_of_data_provider>",
   "url": "< API_endpoint>",
   "logo": "< URL_of_the_logo>" 
}]

	Database 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=dataProviders:103

Supports aggregation via POST.

Example - Body: { "aggregations": ["dataProviders"] } 	multiple
'depositedDate' 	Date when the record was deposited to the repository and follows the format -

YYYY-MM-DDTHH:MM:SS

	Crossref 	Searchable using field lookup via GET.Example - https://api.core.ac.uk/v3/search/works/?q=depositedDate:"2001-06-01T00:00:00"

Supports aggregation via POST.

Example - Body: { "aggregations": ["depositedDate"] } 	single
'documentType' 	List of types of the record. Example types are ‘research’, ‘thesis’, ‘unknown’, ‘slides’, ‘research article’, 'text', 'journal article', 'conference paper', 'review', 'book', 'other', 'report', 'project', 'doctoral thesis’, 'book part', 'working paper', 'dataset', 'master thesis', 'presentation', 'bachelor thesis', 'lecture', 'conference proceedings', 'image', 'software', 'conference object', 'patent', 'video', 'annotation', 'conference poster', 'musical notation', 'preprint', 'technical report', ‘interactive resource’, ‘research proposal’, ‘review article’. 	From a machine learning tool when possible with full-text, otherwise with an interpretation of the values from OAI-PMH dc.subject and dc.type 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=documentType:thesis

Supports aggregation via POST.

Example - Body: { "aggregations": ["documentType"] } 	multiple
'doi' 	DOI of the record. 	OAI-PMH and Crossref 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=doi:10.26153/tsw/52804

Supports aggregation via POST.

Example - Body: { "aggregations": ["doi"] } 	single
'downloadUrl' 	Download URL of the work. 	Database 		single
'fieldOfStudy'* 	Subject area or discipline related to the work. 	Obtained from Microsoft Academic Graph (MAG) 		single
'fullText' 	Full-text of the work. 	Using the download URL from OAI-PMH, the PDF is crawled and value is obtained from PDF using Apache PDFBox. 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=fullText:political-science 	single
'id' 	Unique Work identifier 	Database 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=id:152480964

Supports aggregation via POST.
Example - Body: { "aggregations": ["id"] } 	single
'identifiers' 	List of CORE_IDs and external identifiers (ARXIV_ID, DOI, OAI_ID) associated with the record. Identifiers follows the structure -

"identifiers": 
[{
 "identifier": "< identifier_value>",
 "type": "< identifier_type>
 },
 ... 
]

	Crossref, OAI-PMH and any additional sources identifying the work. CORE_ID is obtained from the database. 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=identifiers:oai:arxiv.org:2310.16146 	multiple
'journals' 	List of metadata (journal title and identifiers including issn) about the journal associated with the record. Format -

"journals":
[{
"title": "< journal_title>", 
"identifiers":
   [
   "< identifier_1>",
   "< identifier_2>",
   ...
   ]
}]

	From issn resolution and journal identifiers 		multiple
'links' 	List of different types of CORE URLs associated with the record. Format -

"links":
[{
   "type": "< link_type>",
   "url": "< corresponding_url>"
 },
 ...
]

Example link types are 'download', 'reader', 'display', 'thumbnail_l', 'thumbnail_m'. 	CORE records 		multiple
'magId'* 	Unique identifier assigned to the work in Microsoft Academic Graph. 	Obtained from Microsoft Academic Graph (MAG). 	Searchable using field lookup via GET.Example - https://api.core.ac.uk/v3/search/works/?q=magId:2139460650

Supports aggregation via POST.

Example - Body: { "aggregations": ["magId"] } 	single
'oaiIds' 	List of OAI identifiers for the work and follows the structure: oai:repository.domain.com:identifier
- oai: fixed prefix indicating that this is an OAI identifier.
- repository.domain.com : domain name of the repository.
- identifier : unique identifier assigned by the repository to the specific record. 	OAI-PMH 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=oaiIds:"oai:nrl.northumbria.ac.uk:522"

Supports aggregation via POST.

Example - Body: { "aggregations": ["oaiIds"] } 	multiple
'outputs' 	List of URLs, pointing to a specific output in CORE. 	List of CORE IDs of the deduplicated outputs this work represents. 	Searchable via works identifier. Example - https://api.core.ac.uk/v3/works/{identifier}/outputs 	multiple
'publishedDate' 	Date, the record is published and follows the format -

YYYY-MM-DDTHH:MM:SS

	Crossref and OAI-PMH. The date that is earliest is selected. 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=publishedDate:"2009-10-18T00:00:00"

Supports aggregation via POST.

Example - Body: { "aggregations": ["publishedDate"] } 	single
'publisher' 	Name of the publisher. 	OAI-PMH, Crossref, DOI prefixes. Normalised using publisher names from crossref 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=publisher:Nature

Supports aggregation via POST.

Example - Body: { "aggregations": ["publisher"] } 	single
'pubmedId' 	Unique identifier assigned to the record in PubMed. 	PubMed 	Searchable using field lookup via GET.

Example - https://api.core.ac.uk/v3/search/works/?q=pubmedId:2844484

Supports aggregation via POST.
Example - Body: { "aggregations": ["pubmedId"] } 	single
'references' 	List of references cited in the work. Each reference contains metadata such as id (CORE ID), title, authors, date, doi, raw (full citation text), and cites (works that cite the given document) 	From full-text parsing (when available) 		multiple
'sourceFulltextUrls' 	List of URLs where full-text is available. 	OAI-PMH metadata 		multiple
'title' 	Title of the work. 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/works/?q=title:retrieval-augmented-generation 	single
'updatedDate' 	Date when the work was last updated in CORE 	Database 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/works/?q=updatedDate:"2024-08-16T00:03:23"
Supports aggregation via POST.
Example - Body: { "aggregations": ["updatedDate"] } 	single
'yearPublished' 	Year the document was published. 	OAI-PMH 	Searchable using field lookup via GET.
Example - https://api.core.ac.uk/v3/search/works/?q=yearPublished:2024
Supports aggregation via POST.
Example - Body: { "aggregations": ["yearPublished"] } 	single
* - deprecated (This information is no longer updated.)

Authorizations:
NoneNone

Search Works

This section provides details about how to use the CORE API query language for more complex searches within the works entity.

API Endpoint

GET https://api.core.ac.uk/v3/search/works

Example Search

Search for works published between 2015 and 2024, that contain either "machine learning" or "artificial intelligence" in the title and have full text.

https://api.core.ac.uk/v3/search/works?q=(title:"machine learning" OR title:"artificial intelligence") AND yearPublished>="2015" AND yearPublished<="2024" AND _exists_:fullText&limit=5

This query retrieves up to 5 works that meet all of the above conditions.
Example python source code to search works by DOI:

   def search_works_by_doi(doi:str):
       url = "https://api.core.ac.uk/v3/search/works"
       headers = {"Authorization": f"Bearer {apikey}"}
       params = {"q": f"doi:"{doi}"", "limit": 1}

           try:
               response = requests.get(url, headers=headers, params=params)
               if response.status_code == 200:
                   return response.json()
               else:
                   print(f"Error {response.status_code}: {response.text}")
                   return None
           except requests.exceptions.RequestException as e:
               print(f"Request failed: {e}")
               return None

More examples on field specific search is available here

Authorizations:
NoneNone

Search Works using aggregation

POST request body example:

{
"q": "climate change",
"aggregations": ["yearPublished", "authors"]
}


Example source code to aggregate results for works based on the above request body:

def search_with_aggregation(query):
   url = "https://api.core.ac.uk/v3/search/works/aggregate"
   headers = {
       "Authorization": f"Bearer {apikey}",
       "Content-Type": "application/json"
   }
   data = {
       "q": query,
       "aggregations": ["yearPublished", "authors"]
   }
   try:
       response = requests.post(url, json=data, headers=headers)

       if response.status_code == 200:
           print("Aggregation Results:")
           print(response.json())
       else:
           print(f"Error {response.status_code}: {response.text}")
 
   except requests.exceptions.RequestException as e:
       print(f"Request failed: {e}") 


Aggregation response sample for query="climate change"

{
"aggregations": {
  "yearPublished": {
    "2025": 4116,
    "2024": 108312,
    "2023": 151061,
    "2022": 151742,
    "2021": 135433,
    "2020": 132744,
    .....................
    .....................
    "1897": 605,
    "1896": 664,
    "1892": 543
  },
  "authors": {
    "Wang": 5319,
    "Smith": 4805,
    "Zhang": 4524,
    "IPCC": 4397,
    ......................
    ......................
    "Campbell": 1101,
    "Hu": 1101,
    "Wood": 1100
  }
}
}


The works fields that support aggregation can be viewed here

Authorizations:
NoneNone

Get single Work

The API endpoint retrieves a single Work from the CORE database using its unique identifier.

API Endpoint

GET https://api.core.ac.uk/v3/works/{identifier}

where the {identifier} corresponds to the work ID.

Example GET request - https://api.core.ac.uk/v3/works/267312

Authorizations:
NoneNone
path Parameters
identifier
required
	
string(\d+|\w+:\d+|\w+:\d+.\d+|\w+:[a-z0-9.]+:\d+|\...

The Work ID
Responses

Response samples

    200

Content type
application/json
{

    "accepted_date": "2019-08-24T14:15:22Z",
    "arxiv_id": "string",
    "authors": 

[

    "string"

],
"citation_count": 0,
"contributors": 
[

    "string"

],
"outputs": 
[

    "string"

],
"created_date": "2019-08-24T14:15:22Z",
"data_providers": 
[

    "string"

],
"deposited_date": "2019-08-24T14:15:22Z",
"abstract": "string",
"document_type": "string",
"doi": "string",
"download_url": "string",
"field_of_study": "string",
"full_text": "string",
"id": 0,
"identifiers": 
[

    {}

],
"title": "string",
"language": { },
"mag_id": "string",
"oai_ids": 
[

    "string"

],
"published_date": "2019-08-24T14:15:22Z",
"publisher": { },
"pubmed_id": { },
"references": 
[

    {}

],
"source_fulltext_urls": 
[

    "string"

],
"journals": 
[

    {}

],
"updated_date": "2019-08-24T14:15:22Z",
"year_published": 0,
"links": 

    [
        "string"
    ]

}
Get outputs related to Work

The API endpoint retrieves the list of Outputs associated with a specific Work. Each output represents an individual version or source-specific instance of the Work, typically harvested from repositories, journals, or other data providers.

API Endpoint

GET https://api.core.ac.uk/v3/works/{identifier}/outputs

where the {identifier} corresponds to the work ID.

Example GET request - https://api.core.ac.uk/v3/works/58/outputs
Sample source code for retrieving outputs related to a specific work is as follows:

def get_outputs_by_work_id(work_id: str):
    url = f"https://api.core.ac.uk/v3/works/{work_id}/outputs"
    headers = {"Authorization": f"Bearer {apikey}"}
    params = {"limit": 10, "offset": 0}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

Authorizations:
NoneNone
path Parameters
identifier
required
	
string(\d+|\w+:\d+|\w+:\d+.\d+|\w+:[a-z0-9.]+:\d+|\...

The Work ID
Responses

Response samples

    200

Content type
application/json
{

    "accepted_date": "2019-08-24T14:15:22Z",
    "authors": 

[

    "string"

],
"contributors": 
[

    "string"

],
"created_date": "2019-08-24T14:15:22Z",
"data_provider": 
[

    "string"

],
"deposited_date": "2019-08-24T14:15:22Z",
"abstract": "string",
"document_type": 
[

    "string"

],
"versions": 
[

    "string"

],
"doi": "string",
"oai": "string",
"download_url": "string",
"full_text": "string",
"id": 0,
"identifiers": 
[

    {}

],
"title": "string",
"language": { },
"published_date": "2019-08-24T14:15:22Z",
"publisher": { },
"references": 
[

    {}

],
"source_fulltext_urls": 
[

    "string"

],
"updated_date": "2019-08-24T14:15:22Z",
"year_published": "string",
"links": 
[

    "string"

],
"tags": 
[

    "string"

],
"set_specs": 
[

    "string"

],
"fulltext_status": "string",
"subjects": 
[

    "string"

],
"deleted": "string",
"journals": 
[

    { }

],
"repositories": 
[

    { }

],
"repository_document": { },
"urls": 
[

    "string"

],
"license": "string",
"orcids": 
[

    null

],
"disabled": 0,
"last_update": "2019-08-24T14:15:22Z",
"sdg": 

    [
        "string"
    ]

}
Get statistics about Work

The API endpoint retrieves key lifecycle dates for a specific Work, such as when it was deposited, accepted, published, and last updated.

API Endpoint

GET https://api.core.ac.uk/v3/works/{identifier}/stats

where the {identifier} corresponds to the work ID.

Example Request - https://api.core.ac.uk/v3/works/267312/stats

Authorizations:
NoneNone
path Parameters
identifier
required
	
string(\d+|\w+:\d+|\w+:\d+.\d+|\w+:[a-z0-9.]+:\d+|\...

The Work ID
Responses

Response samples

    200

Content type
application/json
{

    "id": 0,
    "deposited_date": "2019-08-24T14:15:22Z",
    "published_date": "2019-08-24T14:15:22Z",
    "updated_date": "2019-08-24T14:15:22Z",
    "accepted_date": "2019-08-24T14:15:22Z"

}
Download the parsed Work - TEI file

Download the structured data for the pdf file associated with the work.

API Endpoint

https://api.core.ac.uk/v3/works/tei/{identifier}

where the {identifier} corresponds to the work ID.

Example Request - https://api.core.ac.uk/v3/works/tei/127610059 will download the work with ID 127610059.

Authorizations:
NoneNone
path Parameters
identifier
required
	
string(\d+|\w+:\d+|\w+:\d+.\d+|\w+:[a-z0-9.]+:\d+|\...
Responses

Response samples

    200

Content type
application/xml

...<tei>...

Download the Work file

Download the binary file associated with the work.

API Endpoint

https://api.core.ac.uk/v3/works/{identifier}/download

where the {identifier} corresponds to the work ID.

Example Request - https://api.core.ac.uk/v3/works/127610059/download will download the work with ID 127610059 as a TEI file.

Authorizations:
NoneNone
path Parameters
format	
string
Enum: "tei" "pdf" "txt" "raw"

The format of the download. Currently only PDF is supported.
identifier
required
	
string\w+
header Parameters
accept
required
	
string
Enum: "application/pdf" "application/msword"

Possible format it will go in the accept header, if empty will return the PDF file.
Responses

Response samples

    200

Content type
application/pdf

...%PDF%...

Entities
Introduction

The CORE API provides convenient and comprehensive access to global research results. CORE is based on the global repositories network and collects, aggregates and expands the metadata provided and the associated full texts. The API allows access to the data summarised in the search index.
Authorizations:
NoneNone

CORE data model

The following diagram depicts the primary entities and their main attributes (the full list is in the documentation below)

Works
Works provide a representation of a research work in a way that is independent of its manifestations. Each research work can have one or more manifestations (Outputs) available from any data provider. Works refer to a deduplicated and harmonised meta-entity describing the research work and connecting its Outputs.

Outputs
Outputs refer to specific manifestations of a research work (Works).

Data Providers
The Data Provider entity represents the data sources from which Outputs are collected. These sources include but are not limited to institutional, subject, preprint, repositories and journals or their collections.
Authorizations:
NoneNone

Rate limits
Common

Access to the CORE API is free and requires no authentication. Providing free access to general users is part of our mission. Being a sustainable scholarly infrastructure is also part of our mission. As a result, we offer better performance to registered users. The below table provides information about our rate limits depending on your situation.

To control the load on our systems we use a rate-limiting technology based on tokens. Each user has access to a certain number of tokens at the start of their session and they can use them to perform their queries.

Certain calls in CORE are more computationally expensive than others, therefore some calls such as recommender, scroll search and bulk queries will cost you more tokens than others. As a rule of thumb, a simple query will cost you 1 token while more complex queries will cost you between 3 to 5 tokens.

We are monitoring the load on our servers and at some point we might decide to increase or decrease the “cost” of certain operations to control the overall load. The best way to keep on top of your API usage is to use the HTTP headers included in every API call response (see below for details about the headers).

User type	How to obtain	Rate limit	Support
Unauthenticated users	No registration required, just start using the API.	100 tokens per day, maximum 10 per minute.	No support
Registered Personal users	Registration through the CORE API form	1,000 tokens per day, maximum 25 per minute.	Best effort
Registered academic users NOT affiliated with Supporting or Sustaining institutions.	Registration through the CORE API form	5,000 tokens per day, maximum 10 per minute. 	Best effort
Registered academic users affiliated with Supporting or Sustaining institutions and Non-academic organisation users	Registration through the CORE API form	The API limits are designed to allow reasonable usage and we will change them depending on the load on our servers. However, on average, we estimate this plan should be good for up to about 200k tokens per day. You are able to monitor your current API limit by looking for our customised HTTP headers: X-RateLimitRemaining X-RateLimit-Retry-After X-RateLimit-Limit	Dedicated support
VIP	Contact us to discuss a dedicated plan to upgrade your registration. 	Sky is the limit. We can support your needs. Just let us know and we will find a way to accommodate your usage needs. 	Unlimited priority support

Authorizations:
NoneNone

How to monitor your API rate limits

To ensure fair usage and maintain API stability, CORE implements rate limits. These limits may be adjusted dynamically based on server load and usage patterns.

You can monitor your current rate usage by checking the following custom HTTP response headers included in every API response:
Header	Description
X-RateLimit-Limit	The total number of requests allowed within the current rate-limiting window. This represents your maximum quota before the limit resets.
X-RateLimit-Remaining	The number of requests you still have available in the current window. Once this value reaches zero, additional requests will be blocked until the window resets.
X-RateLimit-Retry-After	Indicates when you can safely make another request after hitting the rate limit.

Authorizations:
NoneNone

Querying large datasets

The API is great to use for small queries and fast access to the CORE data. For bigger queries we recommend you using the CORE dataset.The maximum size for a result set using the API is 10,000 results, to get bigger datasets the search endpoints offer the possibility of scroll queries.By appending a parameter called scroll the system will provide you an id that you can use to perform bigger queries.Our example will show you how to use it. Please keep in mind that performing these queries has a bigger performance impact and we are limiting them more strictly than the normal queries.
Authorizations:
NoneNone

How to call the API

There are a few ways you can perform API requests using your API Key. Request an API key here. Please do not disclose your API key. It is for your use only.

    preferred You can embed the API Key in the header. This keeps the authorisation separated from the requests parameters. Add the header Authorization: Bearer [API_KEY]
    If you cannot set your headers you can also use the API key as a parameter in your requests including it like this: api_key=[API_KEY] . 

Authorizations:
NoneNone

PDF download policy

    Outputs PDF downloads are possible via the original ‘downloadUrl’ supplied link, if a URL exists. This is the preferred method.
    Where users are prevented, restricted or blocked from reaching the resource specified in the ‘downloadUrl’, then CORE API users can also use the GET request endpoint -

    GET https://api.core.ac.uk/v3/outputs/{identifier}/download

    for downloading PDFs directly from CORE. This request counts against your API tokens allowance and is generally more expensive, because it has more significant data implications.
    IMPORTANT: Systematic harvesting of PDFs from CORE outside that circumvents the API, e.g. via https://files.core.ac.uk/download/{identifier}.pdf or other methods is unacceptable. Such usage will be blocked and associated API keys will be disabled.