import string
import os
import time
from typing import List

DEL_PENALTY = 1
INS_PENALTY = 1
SUB_PENALTY = 1

OP_OK = 0
OP_SUB = 1
OP_INS = 2
OP_DEL = 3

PUNCTUATION_TRANSLATOR = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # map punctuation to space


def wer(ref: str, hyp: str, debug=False) -> float:
    """ Calculates the Word Error Rate metric
    :param ref: The reference / gold standard text
    :param hyp: The hypothesis text
    :param debug: if True, prints a backtrace of operations performed to get from the hypothesis to the reference

    :return: wer-score [0.0, 1.0]. Where 0.0 indicates a perfect hypothesis and 1.0 indicates complete garbage:
            every word is incorrect or missing
    """
    r = ref.split()
    h = hyp.split()
    # costs will hold the costs, like in the Levenshtein distance algorithm
    costs = [[0 for inner in range(len(h) + 1)] for outer in range(len(r) + 1)]
    # backtrace will hold the operations we've done.
    # so we could later backtrace, like the WER algorithm requires us to.
    backtrace = [[0 for inner in range(len(h) + 1)] for outer in range(len(r) + 1)]

    # First column represents the case where we achieve zero
    # hypothesis words by deleting all reference words.
    for i in range(1, len(r) + 1):
        costs[i][0] = DEL_PENALTY * i
        backtrace[i][0] = OP_DEL

    # First row represents the case where we achieve the hypothesis
    # by inserting all hypothesis words into a zero-length reference.
    for j in range(1, len(h) + 1):
        costs[0][j] = INS_PENALTY * j
        backtrace[0][j] = OP_INS

    numbers = get_dutch_numbers()

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            # Here we check whether reference matches the hypothesis
            # We assume written numbers in the hypothesis are correct if the reference is numeric
            if r[i - 1] == h[j - 1] or contains_substring(h[j - 1], numbers) and r[j - 1].isnumeric():
                costs[i][j] = costs[i - 1][j - 1]
                backtrace[i][j] = OP_OK
            else:
                substitutionCost = costs[i - 1][j - 1] + SUB_PENALTY  # penalty is always 1
                insertionCost = costs[i][j - 1] + INS_PENALTY  # penalty is always 1
                deletionCost = costs[i - 1][j] + DEL_PENALTY  # penalty is always 1

                costs[i][j] = min(substitutionCost, insertionCost, deletionCost)
                if costs[i][j] == substitutionCost:
                    backtrace[i][j] = OP_SUB
                elif costs[i][j] == insertionCost:
                    backtrace[i][j] = OP_INS
                else:
                    backtrace[i][j] = OP_DEL

    # back trace though the best route:
    i = len(r)
    j = len(h)
    numSub = 0
    numDel = 0
    numIns = 0
    numCor = 0
    if debug:
        print("OP\tREF\tHYP")
        lines = []
    while i > 0 or j > 0:
        if backtrace[i][j] == OP_OK:
            numCor += 1
            i -= 1
            j -= 1
            if debug:
                lines.append("OK\t" + r[i] + "\t" + h[j])
        elif backtrace[i][j] == OP_SUB:
            numSub += 1
            i -= 1
            j -= 1
            if debug:
                lines.append("SUB\t" + r[i] + "\t" + h[j])
        elif backtrace[i][j] == OP_INS:
            numIns += 1
            j -= 1
            if debug:
                lines.append("INS\t" + "****" + "\t" + h[j])
        elif backtrace[i][j] == OP_DEL:
            numDel += 1
            i -= 1
            if debug:
                lines.append("DEL\t" + r[i] + "\t" + "****")
    if debug:
        lines = reversed(lines)
        for line in lines:
            print(line)
        print("#cor " + str(numCor))
        print("#sub " + str(numSub))
        print("#del " + str(numDel))
        print("#ins " + str(numIns))
    return (numSub + numDel + numIns) / (float)(len(r))


def cleanstring(input):
    input = input.lower()
    input = input.translate(PUNCTUATION_TRANSLATOR)
    return input


def werCompareFiles(refFile, compFile):
    with open(refFile, 'r') as reference:
        refstring = reference.read().replace('\n', ' ')
    refstring = cleanstring(refstring)

    with open(compFile, 'r') as compare:
        compstring = compare.read().replace('\n', ' ')
    compstring = cleanstring(compstring)

    return wer(refstring, compstring)


def werCompareDirectoryWithReference(directory):
    for file in os.listdir(directory):
        if file != "Reference.txt":
            wer = str(round(werCompareFiles(directory + "/Reference.txt", directory + "/" + file), 2))
            print(file + " WER: " + wer)


def werCompareDirectory(directory):
    rfilelist = list()
    tfilelist = list()
    for file in os.listdir(directory):
        if file.endswith(".wav"):
            pass
        else:
            if file.startswith("r"):
                rfilelist.append(file)
            if file.startswith("t"):
                tfilelist.append(file)

    # shortest file name is always the reference now #TODO
    rfilelist.sort(key=lambda x: len(x))
    rref = rfilelist.__getitem__(0)
    rfilelist.remove(rref)
    rfilelist.sort()
    tfilelist.sort(key=lambda x: len(x))
    tref = tfilelist.__getitem__(0)
    tfilelist.remove(tref)
    tfilelist.sort()

    rref = directory + "/" + rref
    tref = directory + "/" + tref
    for i in range(0, len(rfilelist)):
        rcompare = directory + "/" + rfilelist.__getitem__(i)
        tcompare = directory + "/" + tfilelist.__getitem__(i)
        rwer = str(round(werCompareFiles(rref, rcompare), 2))
        twer = str(round(werCompareFiles(tref, tcompare), 2))

        print(rcompare.split(" ", 1)[1].strip(".txt") + " R WER: " + rwer)
        print(tcompare.split(" ", 1)[1].strip(".txt") + " T WER: " + twer)


def runComparsion():
    folderlist = list()
    for file in os.listdir('ComparisonFolders'):
        folderlist.append(file)

    for i in range(0, len(folderlist)):
        print("Comparing Directory " + folderlist.__getitem__(i))
        werCompareDirectory('ComparisonFolders\\' + folderlist.__getitem__(i))
        print("#######################################")
        print()


def get_dutch_numbers():
    with open("pol_harvester/utils/numbers_dutch.txt") as f:
        numbers = f.readlines()
        # remove whitespace characters like `\n` at the end of each line
        numbers = [x.strip() for x in numbers]
    return numbers


def contains_substring(test: str, substrings: List[str]):
    for sub in substrings:
        if sub in test:
            return True

    return False
