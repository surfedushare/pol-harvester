from datagrowth.resources import ShellResource


class KaldiAspireResource(ShellResource):
    """
    Usage:

    resource = KaldiAspireResource().run(<file-path>)
    content_type, transcript = resource.content
    """

    CMD_TEMPLATE = [
        "online2-wav-nnet3-latgen-faster",
        "--online=false",
        "--do-endpointing=false",
        "–frame-subsampling-factor=3",
        "–config=exp/tdnn_7b_chain_online/conf/online.conf",
        "--max-active=7000",
        " --beam=15.0",
        "--lattice-beam=6.0",
        "–acoustic-scale=1.0",
        "–word-symbol-table=exp/tdnn_7b_chain_online/graph_pp/words.txt exp/tdnn_7b_chain_online/final.mdl exp/tdnn_7b_chain_online/graph_pp/HCLG.fst",
        "'ark:echo utterance-id1 utterance-id1|'",
        "'scp:echo utterance-id1 {}|'",
        "'ark:/dev/null'"
    ]
    FLAGS = {}
    CONTENT_TYPE = "text/plain"
    DIRECTORY_SETTING = "KALDI_ASPIRE_BASE_PATH"

    def transform(self, stdout):
        # TODO: clear LOG lines and strip "utterance-id1"
        return stdout
