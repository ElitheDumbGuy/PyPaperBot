# REST API
Overview

The REST API gives anyone free, programmatic access to the Unpaywall database.

If you're using the API, we recommend you subscribe to the mailing list in order to stay up-to-date when there are changes or new features.
Schema

The API response uses the same shared schema as the database snapshot and Data Feed.
Authentication

Requests must include your email as a parameter at the end of the URL, like this: api.unpaywall.org/my/request?email=YOUR_EMAIL.
Rate limits

Please limit use to 100,000 calls per day. If you need faster access, you'll be better served by downloading the entire database snapshot for local access.
Versions

The current version of the API is Version 2, and this is the only version supported. Version updates are announced on the mailing list.
Alternatives

Depending on your use case, there are often easier ways to access the data than using the API. You can learn more about these in our brief Get Stated pages:

    Get started: Library
    Get started: Enterprise
    Get started: Research

Endpoints
GET /v2/:doi
Description 	Gets OA status and bibliographic info for an given DOI-assigned resource.
Accepts 	A valid DOI.
Returns 	DOI Object
Example 	https://api.unpaywall.org/v2/10.1038/nature12373?email=YOUR_EMAIL
GET /v2/search?query=:your_query[&is_oa=boolean][&page=integer]

Usage notes and additional examples are available in the Unpaywall FAQ.

This endpoint can be accessed through our Article Search tool.
Description 	Provides the full GET /v2/:doi responses for articles whose titles match your query. 50 results are returned per request and the page argument requests pages after the first.
Accepts 	

    query: The text to search for. Search terms are separated by whitespace and are AND-ed together by default. The title must contain all search terms to be matched. This behavior can be modified by:
        "quoted text" : words inside quotation marks must appear as a phrase to match
        OR : replaces the default AND between words, making a match on either word
        - : negation, only titles not containing this term will match
    is_oa: (Optional) A boolean value indicating whether the returned records should be Open Access or not.
        true: filter the results to OA articles
        false: filter the results to non-OA articles
        null/unspecified: return the most relevant results regardless of OA status
    page: (Optional) An integer indicating which page of results should be returned.
        1/unspecified: return results 1 to 50
        2: return results 51 to 100
        etc.

Returns 	An array of results sorted by the strength of the query match. Each result consists of:

    response: the full DOI Object for this match
    score: the numeric score used to rank the results
    snippet: An HTML-formatted string showing how the title matched the query. For example:

    "Single-<b>cell</b> photoacoustic <b>thermometry</b>"

Example 	https://api.unpaywall.org/v2/search?query=cell%20thermometry&is_oa=true&email=YOUR_EMAIL




# Data Format
Overview

The database snapshot, Simple Query Tool, REST API, and Data Feed products all return JSON-formatted data. For simplicity, that data is organized under the same schema in all cases; that schema is informally described on this page.

Regardless of the source, each record returned consists of one DOI Object, containing resource metadata. Each DOI Object in turn contains a list of zero or more OA Location Objects.

New fields may be added at any time. This won't be a problem for existing code in most cases since they will simply go unused, but you shouldn't rely on the number of fields being fixed.

Fields marked (beta) may have their behavior changed without warning. Changes to other fields will be announced on the Unpaywall mailing list.
DOI object

The DOI object is more or less a row in our main database...it's everything we know about a given DOI-assigned resource, including metadata about the resource itself, and information about its OA status. It includes a list of zero or more OA Location Objects, as well as a best_oa_location property that's probably the OA Location you'll want to use.
best_oa_locationObject|null	The best OA Location Object we could find for this DOI. 	The "best" location is determined using an algorithm that prioritizes publisher-hosted content first (eg Hybrid or Gold), then prioritizes versions closer to the version of record (PublishedVersion over AcceptedVersion), then more authoritative repositories (PubMed Central over CiteSeerX).

Returns null if we couldn't find any OA Locations.
data_standardInteger	Indicates the data collection approaches used for this resource. 	Possible values:

    1 First-generation hybrid detection. Uses only data from the Crossref API to determine hybrid status. Does a good job for Elsevier articles and a few other publishers, but most publishers are not checked for hybrid.
    2 Second-generation hybrid detection. Uses additional sources, checks all publishers for hybrid. Gets about 10x as much hybrid. data_standard==2 is the version used in the paper we wrote about the dataset. 

doiString	The DOI of this resource. 	This is always lowercase.
doi_urlString	The DOI in hyperlink form. 	This field simply contains "https://doi.org/" prepended to the doi field. It expresses the DOI in its correct format according to the Crossref DOI display guidelines.
genreString|null	The type of resource. 	Currently the genre is identical to the Crossref-reported type of a given resource. The "journal-article" type is most common, but there are many others.
is_paratextBoolean	Is the item an ancillary part of a journal, like a table of contents? 	See here for more information on how we determine whether an article is paratext.
is_oaBoolean	Is there an OA copy of this resource. 	Convenience attribute; returns true when best_oa_location is not null.
journal_is_in_doajBoolean	Is this resource published in a DOAJ-indexed journal. 	Useful for defining whether a resource is Gold OA (depending on your definition, see also journal_is_oa).
journal_is_oaBoolean	Is this resource published in a completely OA journal. 	Useful for defining whether a resource is Gold OA. Includes any fully-OA journal, regardless of inclusion in DOAJ. This includes journals by all-OA publishers and journals that would otherwise be all Hybrid or Bronze OA. See here for more information on OA journals.
journal_issnsString|null	Any ISSNs assigned to the journal publishing this resource. 	Separate ISSNs are sometimes assigned to print and electronic versions of the same journal. If there are multiple ISSNs, they are separated by commas. Example: 1232-1203,1532-6203
journal_issn_lString|null	A single ISSN for the journal publishing this resource. 	An ISSN-L can be used as a primary key for a journal when more than one ISSN is assigned to it. Resources' journal_issns are mapped to ISSN-Ls using the issn.org table, with some manual corrections.
journal_nameString|null	The name of the journal publishing this resource. 	The same journal may have multiple name strings (eg, "J. Foo", "Journal of Foo", "JOURNAL OF FOO", etc). These have not been fully normalized within our database, so use with care.
oa_locationsList	List of all the OA Location objects associated with this resource. 	This list is unnecessary for the vast majority of use-cases, since you probably just want the best_oa_location. It's included primarily for research purposes.
oa_locations_embargoed (beta)List	List of OA Location objects associated with this resource that are not yet available. 	This list includes locations that we expect to be available in the future based on information like license metadata and journals' delayed OA policies. They do not affect the resource's oa_status and cannot be the best_oa_location or first_oa_location.
first_oa_locationObject|null	The OA Location Object with the earliest oa_date. 	Returns null if we couldn't find any OA Locations.
oa_statusString	The OA status, or color, of this resource. 	Classifies OA resources by location and license terms as one of: gold, hybrid, bronze, green or closed. See here for more information on how we assign an oa_status.
has_repository_copyBoolean	Whether there is a copy of this resource in a repository. 	True if this resource has at least one OA Location with host_type = "repository". False otherwise.
published_dateString|null	The date this resource was published. 	As reported by the publishers, who unfortunately have inconsistent definitions of what counts as officially "published." Returned as an ISO8601-formatted timestamp, generally with only year-month-day.
publisherString|null	The name of this resource's publisher. 	Keep in mind that publisher name strings change over time, particularly as publishers are acquired or split up.
titleString|null	The title of this resource. 	It's the title. Pretty straightforward.
updatedString	Time when the data for this resource was last updated. 	Returned as an ISO8601-formatted timestamp. Example: 2017-08-17T23:43:27.753663
yearInteger|null	The year this resource was published. 	Just the year part of the published_date
z_authorsList of Author objects, or null	The authors of this resource. 	Each author object may have the following fields:

    author_position: string with possible values "first", "additional", "last".
    raw_author_name: string
    is_corresponding: boolean
    raw_affiliation_strings: string

OA Location object

The OA Location object describes particular place where we found a given OA article. The same article is often available from multiple locations, and there may be differences in format, version, and license depending on the location; the OA Location object describes these key attributes. An OA Location Object is always a Child of a DOI Object.
host_typeString	The type of host that serves this OA location. 	There are two possible values:

    publisher means this location is served by the article’s publisher (in practice, this usually means it is hosted on the same domain the DOI resolves to).
    repository means this location is served by an Open Access repository. Preprint servers are considered repositories even if the DOI resolves there. 

is_bestBoolean	Is this location the best_oa_location for its resource. 	See the DOI object's best_oa_location description for more on how we select which location is "best."
licenseString|null	The license under which this copy is published. 	We return several types of licenses:

    Creative Commons licenses are uniformly abbreviated and lowercased. Example: cc-by-nc
    Publisher-specific licenses are normalized using this format: acs-specific: authorchoice/editors choice usage agreement
    When we have evidence that an OA license of some kind was used, but it’s not reported directly on the webpage at this location, this field returns implied-oa
    If we are unable to determine a license, or it's not an OA license, this field is null. 

oa_dateString|null	When this document first became available at this location. 	oa_date is calculated differently for different host types and is not available for all oa_locations. See https://support.unpaywall.org/a/solutions/articles/44002063719 for details.
pmh_idString|null	OAI-PMH endpoint where we found this location. 	This is primarily for internal debugging. It's null for locations that weren't found using OAI-PMH.
urlString	The url_for_pdf if there is one; otherwise landing page URL. 	When we can't find a url_for_pdf (or there isn't one), this field uses the url_for_landing_page, which is a useful fallback for some use cases.
url_for_landing_pageString	The URL for a landing page describing this OA copy. 	When the host_type is "publisher" the landing page usually includes HTML fulltext.
url_for_pdfString|null	The URL with a PDF version of this OA copy. 	Pretty much what it says.
versionString	The content version accessible at this location. 	We use the DRIVER Guidelines v2.0 VERSION standard to define versions of a given article; see those docs for complete definitions of terms. Here's the basic idea, though, for the three version types we support:

    submittedVersion is not yet peer-reviewed.
    acceptedVersion is peer-reviewed, but lacks publisher-specific formatting.
    publishedVersion is the version of record.

evidenceString	Deprecated	This field will always be set to the string deprecated and will be removed soon.
updatedString	Deprecated	This field will always be set to the string deprecated and will be removed soon. 


# API
Unpywall Object

class unpywall.Unpywall

    Base class that contains useful functions for retrieving information from the Unpaywall REST API (https://api.unpaywall.org). This client uses version 2 of the API.

    static doi(dois: list, format: str = 'raw', progress: bool = False, errors: str = 'raise', force: bool = False, ignore_cache: bool = False)

        Parses information for a given DOI from the Unpaywall API service and returns it as a pandas DataFrame.
        Parameters:	

            dois (list) – A list of DOIs.
            format (str) – The format of the DataFrame.
            progress (bool) – Whether the progress of the API call should be printed out or not.
            errors (str) – Either ‘raise’ or ‘ignore’. If the parameter errors is set to ‘ignore’ than errors will not raise an exception.
            force (bool) – Whether to force the cache to retrieve a new entry.
            ignore_cache (bool) – Whether to use or ignore the cache.

        Returns:	

        A pandas DataFrame that contains information from the Unpaywall API service.
        Return type:	

        DataFrame

    static download_pdf_file(doi: str, filename: str, filepath: str = '.', progress: bool = False) → None

        This function downloads a PDF from a given DOI.
        Parameters:	

            doi (str) – The DOI of the requested paper.
            filename (str) – The filename for the PDF.
            filepath (str) – The path to store the downloaded PDF.
            progress (bool) – Whether the progress of the API call should be printed out or not.

    static download_pdf_handle(doi: str) → _io.BytesIO

        This function returns a file-like object containing the requested PDF.
        Parameters:	doi (str) – The DOI of the requested paper.
        Returns:	The handle of the PDF file.
        Return type:	BytesIO

    static get_all_links(doi: str) → list

        This function returns a list of URLs for all open-access copies listed in Unpaywall.
        Parameters:	doi (str) – The DOI of the requested paper.
        Returns:	A list of URLs leading to open-access copies.
        Return type:	list

    static get_doc_link(doi: str) → str

        This function returns a link to the best OA location (not necessarily a PDF).
        Parameters:	doi (str) – The DOI of the requested paper.
        Returns:	The URL of the best OA location (not necessarily a PDF).
        Return type:	str

    static get_json(doi: str = None, query: str = None, is_oa: bool = False, errors: str = 'raise', force: bool = False, ignore_cache: bool = False)

        This function returns all information in Unpaywall about the given DOI.
        Parameters:	

            doi (str) – The DOI of the requested paper.
            query (str) – The text to search for.
            is_oa (bool) – A boolean value indicating whether the returned records should be Open Access or not.
            errors (str) – Either ‘raise’ or ‘ignore’. If the parameter errors is set to ‘ignore’ than errors will not raise an exception.
            force (bool) – Whether to force the cache to retrieve a new entry.
            ignore_cache (bool) – Whether to use or ignore the cache.

        Returns:	

        A JSON data structure containing all information returned by Unpaywall about the given DOI.
        Return type:	

        JSON object
        Raises:	

        AttributeError – If the Unpaywall API did not respond with json.

    static get_pdf_link(doi: str) → str

        This function returns a link to an OA pdf (if available).
        Parameters:	doi (str) – The DOI of the requested paper.
        Returns:	The URL of an OA PDF (if available).
        Return type:	str

    static init_cache(cache=None) → None

        This method initilializes a cache that is used to store records from the Unpaywall database.
        Parameters:	cache (UnpywallCache) – A custom cache to be used instead of the standard cache.
        Raises:	AttributeError – If the custom cache is not of type UnpywallCache.

    static query(query: str, is_oa: bool = False, format: str = 'raw', errors: str = 'raise') → pandas.core.frame.DataFrame

        Parses information for a given query from the Unpaywall API service and returns it as a pandas DataFrame.
        Parameters:	

            query (str) – The text to search for.
            is_oa (bool) – A boolean value indicating whether the returned records should be Open Access or not.
            format (str) – The format of the DataFrame.
            errors (str) – Either ‘raise’ or ‘ignore’. If the parameter errors is set to ‘ignore’ than errors will not raise an exception.

        Returns:	

        A pandas DataFrame that contains information from the Unpaywall API service.
        Return type:	

        DataFrame

    static view_pdf(doi: str, mode: str = 'viewer', progress: bool = False) → None

        This function opens a local copy of a PDF from a given DOI.
        Parameters:	

            doi (str) – The DOI of the requested paper.
            mode (str) – The mode for viewing a PDF.
            progress (bool) – Whether the progress of the API call should be printed out or not.

Cache Object

class unpywall.cache.UnpywallCache(name: str = None, timeout=None)

    This class stores query results from Unpaywall. It has a configurable timeout that can also be set to never expire.

    name

        The filename used to save and load the cache by default.
        Type:	string

    content

        A dictionary mapping dois to requests.Response objects.
        Type:	dict

    access_times

        A dictionary mapping dois to the datetime when each was last updated.
        Type:	dict

    delete(doi: str) → None

        Remove an individual doi from the cache.
        Parameters:	doi (str) – The DOI to be removed from the cache.

    download(doi: str, errors: str)

        Retrieve a record from Unpaywall.
        Parameters:	

            doi (str) – The DOI to be retrieved.
            errors (str) – Whether to ignore or raise errors.

    get(doi: str, errors: str = 'raise', force: bool = False, ignore_cache: bool = False)

        Return the record for the given doi.
        Parameters:	

            doi (str) – The DOI to be retrieved.
            errors (str) – Whether to ignore or raise errors.
            force (bool) – Whether to force the cache to retrieve a new entry.
            ignore_cache (bool) – Whether to use or ignore the cache.

        Returns:	

        record – The response from Unpaywall.
        Return type:	

        requests.Response

    load(name=None) → None

        Load the cache from a file.
        Parameters:	name (str or None) – The filename that the cache will be loaded from. If None, self.name will be used.

    reset_cache() → None

        Set the cache to a blank state.

    save(name=None) → None

        Save the current cache contents to a file.
        Parameters:	name (str or None) – The filename that the cache will be saved to. If None, self.name will be used.

    timed_out(doi: str) → bool

        Return whether the record for the given doi has expired.
        Parameters:	doi (str) – The DOI to be removed from the cache.
        Returns:	is_timed_out – Whether the given entry has timed out.
        Return type:	bool

Utils

class unpywall.utils.UnpywallCredentials(email: str)

    This class provides tools for setting up an email for the Unpaywall service.

    email

        An email that is necessary for using the Unpaywall API service.
        Type:	str

    static validate_email(email: str) → str

        This method takes an email as input and raises an error if the email is not valid. Otherwise the email will be returned.
        Parameters:	email (str) – An email that is necessary for using the Unpaywall API service.
        Returns:	The email that was given as input.
        Return type:	str
        Raises:	ValueError – If the email parameter is empty or not valid.

class unpywall.utils.UnpywallURL(doi: str = None, query: str = None, is_oa: bool = False)

    This class provides the Unpaywall URL.

    doi

        The DOI of the requested paper.
        Type:	str

    query

        The text to search for.
        Type:	str

    is_oa

        A boolean value indicating whether the returned records should be Open Access or not.
        Type:	bool

    doi_url

        The URL for the DOI-Endpoint.
        Type:	str

    query_url

        The URL for the Query-Endpoint
        Type:	str