from collections import defaultdict, namedtuple
import pandas as pd


Segment = namedtuple("Segment", ["source", "channel", "start", "length", "gender", "band", "segment_type", "label"])


class LIUMSegments(object):
    """
    Documentation on the LIUM format: https://projets-lium.univ-lemans.fr/spkdiarization/data/
    As well as: https://stackoverflow.com/questions/45309366/parsing-lium-speaker-diarization-output
    """
    def __init__(self):
        self.segments = None
        self.indices = None

    def load(self, file_path):
        self.segments = defaultdict(list)
        self.indices = {}
        with open(file_path, "r") as lium_file:
            for line in lium_file:
                if line.startswith(";;") or not line.strip():
                    continue
                segment_data = [int(column) if column.isnumeric() else column.strip() for column in line.split(" ")]
                segment = Segment(*segment_data)
                self.segments[segment.source].append(segment)
        for source, segments in self.segments.items():
            intervals = []
            for segment in segments:
                intervals.append((segment.start, segment.start+segment.length,))
            self.indices[source] = pd.IntervalIndex.from_tuples(intervals, name=source, closed="both")

    def get(self, video, sec=None, msec=None):
        time = msec if msec else int(sec*100)
        loc = self.indices[video].get_loc(time)
        return self.segments[video][loc[0]]
