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
    vocabulary_file_path = os.path.join(vocabulary_path, "vocabulary.txt")
    assert os.path.exists(vocabulary_file_path), \
        "Missing {} for vocabulary '{}'".format(vocabulary_file_path, vocabulary_name)

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
def prepare_vocabulary_compilation(ctx, vocabulary_name, kaldi_path, model_directory):

    # First we do some transformations on the vocabulary directly
    with ctx.cd(os.path.join("vocabularies", vocabulary_name)):
        # Transform vocabulary to uppercase. Bash is assumed to be faster than Python
        ctx.run("cat vocabulary.txt | tr '[:lower:]' '[:upper:]' > vocabulary.upper.txt")
        # We're going to execute SRILM tools
        # Preparing the paths by sourcing the tool environment
        with ctx.prefix("source {}/tools/env.sh".format(kaldi_path)):
            ctx.run(
                "ngram-count -text vocabulary.upper.txt "
                "-order 1 -unk -map-unk \"\" "
                "-wbdiscount -interpolate -lm vocabulary.arpa"
            )

    # Now we merge the original vocabulary and language model with the new vocabulary and model
    # TODO: refactor merge_dicts to utils and call directly
    vocabulary_path = os.path.join("vocabularies", vocabulary_name)
    model_vocabulary = os.path.join(
        model_directory,
        "LG_KrantenTT.3gpr.kn.int_UTwente_HMI_lexicon",
        "words.dict"
    )
    model_arpa = os.path.join(
        model_directory,
        "KrantenTT.3gpr.kn.int.arpa"
    )

    vocabulary_file_path = os.path.join(vocabulary_path, "g2p-vocabulary.dict")
    vocabulary_arpa = os.path.join(vocabulary_path, "vocabulary.arpa")
    lexicon_file_path = os.path.join(vocabulary_path, "g2p-vocabulary.dict")
    lm_arpa = os.path.join(vocabulary_path, "lm.arpa")
    ctx.run(
        f"python merge_dicts.py {model_vocabulary} {model_arpa} "
        f"{vocabulary_file_path} {vocabulary_arpa} "
        f"{lexicon_file_path} {lm_arpa}"
    )
