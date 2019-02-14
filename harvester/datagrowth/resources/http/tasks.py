from time import sleep

from django.apps import apps

from datagrowth.configuration import load_config, DEFAULT_CONFIGURATION
from datagrowth.exceptions import DGResourceException


@load_config(defaults=DEFAULT_CONFIGURATION)
def send(config, *args, **kwargs):
    # Set vars
    method = kwargs.pop("method", None)
    Resource = apps.get_model(config.resource)
    success = []
    errors = []
    has_next_request = True
    current_request = {}
    count = 0
    limit = config.continuation_limit or 1
    # Continue as long as there are subsequent requests
    while has_next_request and count < limit:
        # Get payload
        link = Resource(config=config.to_dict(protected=True))
        link.request = current_request
        try:
            link = link.send(method, *args, **kwargs)
            link.clean()
            link.save()
            success.append(link.id)
        except DGResourceException as exc:
            link = exc.resource
            link.clean()
            link.save()
            errors.append(link.id)
        # Prepare next request
        has_next_request = current_request = link.create_next_request()
        count += 1
    # Output results in simple type for json serialization
    return [success, errors]


@load_config(defaults=DEFAULT_CONFIGURATION)
def send_serie(config, args_list, kwargs_list, method=None):
    success = []
    errors = []
    for args, kwargs in zip(args_list, kwargs_list):
        # Get the results
        scc, err = send(method=method, config=config, *args, **kwargs)
        success += scc
        errors += err
        # Take a break for scraping if configured
        interval_duration = config.interval_duration / 1000
        if interval_duration:
            sleep(interval_duration)
    return [success, errors]
