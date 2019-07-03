import os
import random
import time

import clam.common.client
import clam.common.data
import clam.common.status
from invoke import task


def assert_clam_response(client, session_id, response, message, wait=False):
    if response.errors:
        print("An error occured: " + response.errormsg)
        for parametergroup, paramlist in response.parameters:
            for parameter in paramlist:
                if parameter.error:
                    print("Error in parameter " + parameter.id + ": " + parameter.error)
        client.delete(session_id)
        raise RuntimeError("CLAM response error: {}".format(message))

    while wait and response.status != clam.common.status.DONE:
        time.sleep(2)
        response = client.get(session_id)  # get status again
        print("\tRunning: " + str(response.completion) + '% -- ' + response.statusmessage)

    return response


@task
def create_phonemes(ctx, vocabulary_name, g2pservice="https://webservices-lst.science.ru.nl/g2pservice"):

    vocabulary_path = os.path.join("vocabularies", vocabulary_name)
    vocabulary_file_path = os.path.join(vocabulary_path, "vocabulairy.txt")
    assert os.path.exists(vocabulary_file_path), \
        "Missing {} for vocabulairy '{}'".format(vocabulary_file_path, vocabulary_name)

    username = os.environ.get("G2PSERVICE_USERNAME")
    password = os.environ.get("G2PSERVICE_PASSWORD")
    assert username and password, "Missing credentials for the G2P Service"

    client = clam.common.client.CLAMClient(g2pservice, user=username, password=password, basicauth=True)
    session_id = "{}_{}".format(vocabulary_name, str(random.getrandbits(64)))
    print("Getting phonemes for {} under {}".format(vocabulary_name, session_id))

    client.create(session_id)
    response = client.get(session_id)
    assert_clam_response(client, session_id, response, "Failed to get a new session/project")

    client.addinputfile(session_id, response.inputtemplate("wordlist"), vocabulary_file_path)
    response = client.start(session_id)
    response = assert_clam_response(
        client, session_id, response,
        "Failed to start session/project {}".format(session_id),
        wait=True
    )

    for output_file in response.output:
        file_name = "g2p-" + os.path.basename(str(output_file))
        output_file.copy(os.path.join(vocabulary_path, file_name))

    client.delete(session_id)


@task
def prepare_vocabulary_merge(ctx, vocabulary_name):
    with ctx.cd(os.path.join("vocabularies", vocabulary_name)):
        ctx.run("cat vocabulary.txt | tr '[:lower:]' '[:upper:]' > vocabulary.upper.txt")
        ctx.run("ngram-count -text vocabulary.upper.txt -order 3 -unk -map-unk "" -wbdiscount -interpolate -lm lm.arpa")
