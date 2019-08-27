from django.apps import apps
from celery import current_app as app, chord

from datagrowth.configuration import load_config, DEFAULT_CONFIGURATION
from datagrowth.exceptions import DGResourceException
from datagrowth.utils import ibatch


@app.task(name="datagrowth.run")
@load_config(defaults=DEFAULT_CONFIGURATION)
def run(config, *args, **kwargs):
    # Set vars
    success = []
    errors = []
    Resource = apps.get_model(config.resource)
    cmd = Resource(config=config.to_dict(protected=True))
    # Run the command
    try:
        cmd = cmd.run(*args, **kwargs)
        cmd.clean()
        cmd.save()
        success.append(cmd.id)
    except DGResourceException as exc:
        cmd = exc.resource
        cmd.clean()
        cmd.save()
        errors.append(cmd.id)

    # Output results in simple type for json serialization
    return [success, errors]


@load_config(defaults=DEFAULT_CONFIGURATION)
def run_serie(config, args_list, kwargs_list):
    success = []
    errors = []
    for args, kwargs in zip(args_list, kwargs_list):
        scc, err = run(config=config, *args, **kwargs)
        success += scc
        errors += err
    return [success, errors]


@app.task(name="datagrowth.run_serie")
@app.task(name="datagrowth.send_mass_aggregate")
def run_mass_aggregate(batch_results):
    success = []
    error = []
    for batch in batch_results:
        scc, err = batch
        success += scc
        error += err
    return success, error


@load_config(defaults=DEFAULT_CONFIGURATION)
def run_mass(config, args_list, kwargs_list):

    assert args_list and kwargs_list, "No args list and/or kwargs list given to run mass"

    # Some commands allow batch processing using the concatenation of arguments in some way
    # Here we concatenate arguments using an arbitrary character unless the concat_args_size is 0 (the default)
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
        return run_serie.delay(
            prc_args_list,
            prc_kwargs_list,
            config=config.to_dict(protected=True, private=True)
        )

    # When dealing with multiple batches we create a chord out of these
    tasks = []
    for batch in ibatch(zip(prc_args_list, prc_kwargs_list), config.batch_size):
        batch_args_list, batch_kwargs_list = zip(*batch)
        tasks.append(run_serie.s(
            batch_args_list,
            batch_kwargs_list,
            config=config.to_dict(protected=True, private=True)
        ))
    return chord(tasks)(run_mass_aggregate.s())
