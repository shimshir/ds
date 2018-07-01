import requests as r


def fetch_exposes(page_number, page_size):
    url = f'https://www.immobilienscout24.de/Suche/S-T/P-{page_number}/Wohnung-Miete/-/-/-/-/-/-/?pageSize={page_size}'
    print(f'Fetching page number: {page_number}, page size: {page_size}')
    json_str = r.request('POST', url)
    return json_str.json()['searchResponseModel']['resultlist.resultlist']

def filter_exposes(exposes_dict):
    result_list_entries = exposes_dict['resultlistEntries'][0]['resultlistEntry']
    real_estates = [result_list_entry['resultlist.realEstate'] for result_list_entry in result_list_entries]
    for real_estate in real_estates:
        try:
            del real_estate['galleryAttachments']
            del real_estate['contactDetails']
            del real_estate['titlePicture']
        except KeyError:
            pass
    return real_estates

def fetch_filtered(expose_size=1000, page_size=100):
    exposes_response = fetch_exposes(1, page_size)

    paging_data = exposes_response['paging']
    number_of_pages = paging_data['numberOfPages']

    exposes = filter_exposes(exposes_response)

    for page_to_fetch in range(2, min(int(expose_size / page_size), number_of_pages) + 1):
        next_exposes_response = fetch_exposes(page_to_fetch, page_size)
        exposes.extend(filter_exposes(next_exposes_response))

    return exposes[:expose_size]
