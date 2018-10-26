from django.apps import apps

from datagrowth.configuration import load_config, DEFAULT_CONFIGURATION
from datagrowth.exceptions import DGResourceException


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
        print("ERROR")
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
    print(len(args_list), len(kwargs_list))
    for args, kwargs in zip(args_list, kwargs_list):
        print("STARTING")
        scc, err = run(config=config, *args, **kwargs)
        success += scc
        errors += err
    return [success, errors]
