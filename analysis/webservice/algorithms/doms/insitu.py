"""
Module for querying CDMS In-Situ API
"""
import logging
import requests
from datetime import datetime
from webservice.algorithms.doms import config as insitu_endpoints


def query_insitu(dataset, variable, start_time, end_time, bbox, platform, depth_min, depth_max,
               items_per_page=1000, session=None):
    """
    Query insitu API, page through results, and aggregate
    """
    try:
        start_time = datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    except TypeError:
        # Assume we were passed a properly formatted string
        pass

    try:
        end_time = datetime.utcfromtimestamp(end_time).strftime('%Y-%m-%dT%H:%M:%SZ')
    except TypeError:
        # Assume we were passed a properly formatted string
        pass

    provider = insitu_endpoints.get_provider_name(dataset)

    params = {
        'itemsPerPage': items_per_page,
        'startTime': start_time,
        'endTime': end_time,
        'bbox': bbox,
        'minDepth': depth_min,
        'maxDepth': depth_max,
        'provider': provider,
        'project': dataset,
        'platform': platform,
    }

    if variable is not None:
        params['variable'] = variable

    insitu_response = {}

    # Page through all insitu results
    next_page_url = insitu_endpoints.getEndpoint()
    while next_page_url is not None and next_page_url != 'NA':
        logging.debug(f'Insitu request {next_page_url}')
        if session is not None:
            response = session.get(next_page_url, params=params)
        else:
            response = requests.get(next_page_url, params=params)

        response.raise_for_status()
        insitu_page_response = response.json()

        if not insitu_response:
            insitu_response = insitu_page_response
        else:
            insitu_response['results'].extend(insitu_page_response['results'])

        next_page_url = insitu_page_response.get('next', None)
        params = {}  # Remove params, they are already included in above URL

    return insitu_response
