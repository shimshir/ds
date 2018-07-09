import requests as r
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from time import time
from models import Expose
import coloredlogs
import logging


logger = logging.getLogger('client')
coloredlogs.install(level='INFO', logger=logger)

filter_path = 'Wohnung-Miete/Berlin/Berlin/-/-/-/-/'


def fetch_total_entries():
    url = f'https://www.immobilienscout24.de/Suche/S-T/P-1/{filter_path}?pageSize=2'
    res = r.request('POST', url)
    pagind_data = res.json()[
        'searchResponseModel']['resultlist.resultlist']['paging']
    return int(pagind_data['numberOfListings'])


def fetch_expose_ids(page_number, page_size):
    url = f'https://www.immobilienscout24.de/Suche/S-T/P-{page_number}/{filter_path}?pageSize={page_size}'
    logger.debug(
        f'Fetching ids, page number: {page_number}, page size: {page_size}')
    res = r.request('POST', url)
    result_list = res.json()['searchResponseModel']['resultlist.resultlist']
    rl_entries = result_list['resultlistEntries'][0]['resultlistEntry']
    expose_ids = [result_list_entry['resultlist.realEstate']['@id']
                  for result_list_entry in rl_entries]
    return expose_ids


def fetch_html(id):
    url = f'https://www.immobilienscout24.de/expose/{id}'
    logger.debug(f'Fetching html for expose {id}')
    res = r.request('GET', url)
    return res.content.decode()


def fetch_all_expose_ids(page_size=4000):
    total = fetch_total_entries()
    logger.info(f'Fetching total of {total} expose ids')
    with ThreadPoolExecutor(max_workers=10) as executor:
        futs = []
        for page_to_fetch in range(1, int(total / page_size) + 2):
            ids_fut = executor.submit(
                fetch_expose_ids,
                page_to_fetch,
                page_size
            )
            futs.append(ids_fut)
        ids = [f.result() for f in as_completed(futs)]
    return [expose_id for chunk in ids for expose_id in chunk]


def fetch_expose(id):
    logger.debug(f'Fetching expose: {id}')
    html_doc = fetch_html(id)
    expose = Expose(id, html_doc)
    write_expose_to_file(expose)
    logger.info(f'Fetched expose: {id}:\n{expose}')
    return expose


def write_expose_to_file(expose):
    with open('data/exposes.csv', 'a') as cvs_file:
        expose_dict = vars(expose)
        cvs_header = ','.join([key for key in expose_dict.keys()])
        logger.debug(f'Writing header: {cvs_header}')
        cvs_line = ','.join([str(value) for value in expose_dict.values()])
        logger.debug(f'Writing values: {cvs_line}')
        cvs_file.write(cvs_line)
        cvs_file.write('\n')


#def fetch_exposes():
#    ids = sorted(fetch_all_expose_ids())
#    logger.info(f'Fetched {len(ids)} ids')
#    with ThreadPoolExecutor(max_workers=10) as executor:
#        futs = []
#        for id_to_fetch in ids:
#            expose_fut = executor.submit(
#                fetch_expose,
#                id_to_fetch
#            )
#            futs.append(expose_fut)
#        exposes = [f.result() for f in as_completed(futs)]
#    return exposes

def fetch_exposes():
    ids = sorted(fetch_all_expose_ids())
    logger.info(f'Fetched {len(ids)} ids')
    exposes = [fetch_expose(id) for id in ids]
    return exposes
