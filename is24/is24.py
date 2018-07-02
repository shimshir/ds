import requests as r
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from pprint import pprint
from time import time
import pandas as pd
import utils


def fetch_expose_dict(page_number, page_size) -> dict:
    url = f'https://www.immobilienscout24.de/Suche/S-T/P-{page_number}/Wohnung-Miete/-/-/-/-/-/-/?pageSize={page_size}'
    print(f'Fetching page number: {page_number}, page size: {page_size}')
    json_str = r.request('POST', url)
    return json_str.json()['searchResponseModel']['resultlist.resultlist']


def extract_exposes(exposes_dict) -> list:
    result_list_entries = exposes_dict['resultlistEntries'][0]['resultlistEntry']
    real_estates = [result_list_entry['resultlist.realEstate']
                    for result_list_entry in result_list_entries]
    for real_estate in real_estates:
        try:
            del real_estate['galleryAttachments']
            del real_estate['contactDetails']
            del real_estate['titlePicture']
        except KeyError:
            pass
    return real_estates


def fetch_filtered(expose_count=1000, page_size=100, parallelism=5):
    expose_dict: dict = fetch_expose_dict(1, page_size)
    paging_data: dict = expose_dict['paging']
    pprint({'pagingData': paging_data})
    number_of_pages: int = paging_data['numberOfPages']
    exposes: list = extract_exposes(expose_dict)

    exposes_dict_futs = []

    with ThreadPoolExecutor(max_workers=parallelism) as executor:
        for page_to_fetch in range(2, min(int(expose_count / page_size), number_of_pages) + 1):
            cur_expose_dict_fut: Future = executor.submit(fetch_expose_dict, page_to_fetch, page_size)
            exposes_dict_futs.append(cur_expose_dict_fut)
        exposes_dicts = [exposes_dict_fut.result() for exposes_dict_fut in as_completed(exposes_dict_futs)]
        for exposes_dict in exposes_dicts:
            exposes.extend(extract_exposes(exposes_dict))
        return exposes[:expose_count]

def fetch_df(expose_count=1000, page_size=100, parallelism=5):
    exposes = fetch_filtered(expose_count, page_size, parallelism)
    flattened_exposes = [utils.flatten(expose) for expose in exposes]
    return pd.DataFrame.from_records(flattened_exposes, index='@id')
