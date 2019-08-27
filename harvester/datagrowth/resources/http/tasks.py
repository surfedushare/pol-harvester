from time import sleep

from django.apps import apps
from celery import current_app as app, chord

from datagrowth.configuration import load_config, DEFAULT_CONFIGURATION
from datagrowth.exceptions import DGResourceException
from datagrowth.utils import ibatch


@app.task(name="datagrowth.send")
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


@app.task(name="datagrowth.send_serie")
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


@app.task(name="datagrowth.send_mass_aggregate")
def send_mass_aggregate(batch_results):
    success = []
    error = []
    for batch in batch_results:
        scc, err = batch
        success += scc
        error += err
    return success, error


@load_config(defaults=DEFAULT_CONFIGURATION)
def send_mass(config, args_list, kwargs_list, method=None):

    assert args_list and kwargs_list, "No args list and/or kwargs list given to send mass"

    # Some API's allow batch GET requests using the concatenation of parameters in some way
    # Here we concatenate arguments in a way that is compatible with the Wikipedia API and possibly others
    # Unless the concat_args_size is 0 (the default)
    if config.concat_args_size:
        # Set some vars based on config
        symbol = config.concat_args_symbol
        concat_size = config.concat_args_size
        args_list_size = int(len(args_list) / concat_size) + 1
        # Calculate new args_list and kwargs_list
        # Arg list that are of the form [[1],[2],[3], ...] should become [[1|2|3], ...]
        # Kwargs are assumed to remain similar across the list
        prc_args_list = []
        prc_kwargs_list = []
        for index in range(0, args_list_size):
            args_slice = args_list[index*concat_size:index*concat_size+concat_size]
            joined_slice = []
            for args in args_slice:
                joined = symbol.join(map(str, args))
                joined_slice.append(joined)
            prc_args_list.append([symbol.join(joined_slice)])
            prc_kwargs_list.append(kwargs_list[0])
    else:
        prc_args_list = args_list
        prc_kwargs_list = kwargs_list

    # If there is only one batch we return results immediately
    if config.batch_size == 0:
        return send_serie.delay(
            prc_args_list,
            prc_kwargs_list,
            config=config.to_dict(protected=True, private=True),
            method=method
        )

    # When dealing with multiple batches we create a chord out of these
    tasks = []
    for batch in ibatch(zip(prc_args_list, prc_kwargs_list), config.batch_size):
        batch_args_list, batch_kwargs_list = zip(*batch)
        tasks.append(send_serie.s(
            batch_args_list,
            batch_kwargs_list,
            config=config.to_dict(protected=True, private=True),
            method=method
        ))
    return chord(tasks)(send_mass_aggregate.s())
