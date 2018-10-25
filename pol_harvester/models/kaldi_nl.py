import hashlib

from django.conf import settings

from datagrowth.resources import ShellResource


class KaldiNLResource(ShellResource):
    """
    Usage:

    resource = KaldiNLResource().run(<file-path>)
    content_type, transcript = resource.content
    """

    CMD_TEMPLATE = [
        "bash",
        "kaldi_nl.bash",  # NB: copy this file into the Kaldi NL directory
        "{}"
    ]
    FLAGS = {}
    VARIABLES = {
        "KALDI_ROOT": settings.KALDI_BASE_PATH,
        "OUTPUT_PATH": None  # gets set at runtime
    }
    CONTENT_TYPE = "text/plain"
    DIRECTORY_SETTING = "KALDI_NL_BASE_PATH"

    def environment(self, *args, **kwargs):
        env = super().environment()
        hsh = hashlib.sha1()
        vars = self.variables(*args)
        hsh.update(" ".join(vars["input"]))
        env["OUTPUT_PATH"] = hsh.hexdigest()
        return env

    def transform(self, stdout):
        is_transcript = False
        out = []
        for line in stdout.split("\n"):
            if line == "=== TRANSCRIPTION ===":
                is_transcript = True
            elif line == "=== END TRANSCRIPTION ===":
                is_transcript = False
            elif is_transcript:
                out.append(line)
        return "\n".join(out)
