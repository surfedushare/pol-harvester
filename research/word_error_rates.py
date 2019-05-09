import string
import os

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

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
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


ref = 'Een tweede techniek die we zullen bestuderen om een integraalnummeriek op te lossen is met behulp van de zogenaamde Monte Carlo methode. Het belangrijkste element dat we daar voor nodig hebben is het random getal. Dat is het basis block waarmee we zullen gaan werken. Om een random getal tussen 0 en 1 te krijgen in pijpen kunnen we gebruik maken van de volgende constructie. X is random en als je dat een paar keer doet zie je dat dat getal inderdaad tussen 0 en 1 verdeeld is. Nou zoals in programmeren continu het geval is, is dit een basis block die je zelf kan uitbreiden. Als je bijvoorbeeld een getal tussen 0 en 2 dan is de enige goede manier om dat te doen het random getal met twee te vermenigvuldigen, overtuig jezelf daar ook van. Nou als je een random getal wilt tussen twee willekeurige getallen a en b kan je dat ook met behulp van dit doen bijvoorbeeld tussen -1 en 1 of 0 en Pi bijvoorbeeld. Bedenk zelf nou hoe je dat zou doen. Als je een integraal wil uitrekenen en in ons geval gaan we de integraal uitrekenen van sinus(x) tussen nul en Pi zijn er drie stappen die je moet doen. Eerst is dat je een boks definieerd dat is een rechthoek om het integratie gebied heen. Je moet zorgen dat je de oppervlakte hiervan kent. Nou in ons geval zou een mooi boks zijn, een boks tussen 0 en Pi op de X-as en tussen 0 en 1 op de y-as. Want we weten dat het integratiegebied hier binnenvalt. Namelijk het gebied onder de grafiek. De vraag is nu hoe groot is de oppervlakte daarvan. De twee stap is dat we random getallen gaan gooien in de box. Dus als je een random getal tussen 0 en Pi trekt en dat als X-waarde neemt en vervolgens een getal tussen 0 en 1 als Y-waarde, dan verschijnt er een punt in de grafiek. Dit kan je natuurlijk heel vaak doen en wat we zullen doen is voor elk punt afvragen of het een goed punt is of een fout punt. Een goed punt is een punt dat in het integratiegebied ligt en een fout punt dat buiten het integratiegebied ligt. Het punt dat we nu op het scherm getekend hebben ligt in het integratiegebied en is dus groen, is goed. Maar je zal ook punten genereren die fout zijn en die buiten het integratiegebied vallen. Als je dit een heleboel keer doet, kan je vervolgens de integraal schatten. Namelijk de fractie van de punten die goed zijn de fractie van de punten binnen het integratiegebied maal het oppervlakte van de box. Als bijvoorbeeld 60 procent van de punten in het integratiegebied valt, dan is je schatting van de integraal 60 procent van de oppervlakte van de box, dus 60 procent van Pi. Ik heb dit voorbeeld zelf even uitgewerkt met behulp van 2.000 punten. Links zie je de tekening van de goede en de slechte punten die ik getekend heb. Ik weet dat de box de oppervlakte Pi heeft, dat was stap 1. Stap 2 was 2000 random punten gooien. Daarvan heb ik geteld dat er 1289 goed zijn en daarmee kan ik de integraal schatten. Ik weet namelijk dat 1289 gedeelde door 2.000 van de punten goed waren. Dus ik schat daarmee de oppervlakte van het grafiekje op 1,9603. En natuurlijk kan ik dit ook met 2000 punten doen, maar ik kan het net zo goed met 200.000 punten doen. Hiermee kan je integrale oplossing, zelfs als de functie niet-analytisch bekend is. Twee tips die ik wil meegeven voordat jullie met de opgaves aan de gang gaan. Één, teken de grafiek altijd op het scherm. Dat geeft je heel snel inzicht in hoe de grafiek eruit ziet, maar ook of jij je punten wel precies goed gooit. Ten tweede, test je Met de opgravingen aan de gang één tekende ik altijd op het scherm. Wat heel snel inzicht in hoe de grafieken eruitziet maar ook of jij je punten wel goed gooit. En twee, test je programma altijd op een integraal waarvan je de uitkomst al weet'
ref = cleanstring(ref)
print(f"cleaned ref {ref}")
kaldi_hypothesis = 'Een tweede die we zullen bestuderen om een integraal numeriek op te lossen is met behulp van de zogenaamde monte carlo methode. Het belangrijkste element dat we daarvoor nodig en hebben is een renner getal dat onze baas bob waarmee we zullen gaan werken om rellen getal de eind te krijgen in kunnen wel gebruikmaken van de volgende constructie. X is random. En als je dat een paar keer doet dan zie je dat op inderdaad tussen nul en één verdeeld is. Nou zoals in continu gevallen is dit een basis blok die zelf kan uitbreiden als je getal zou willen tussen nul en twee dan is de enige dat is een goede manier om dat te doen om gewoon hè renner althans hun wel met twee vermenigvuldigen amputatie zelfs daar ook van. Getal wil tussen twee willekeurig getal aardbei kan je dat ook. Met behulp van dit doen bijvoorbeeld een één of tussen nul en bijvoorbeeld het beding zelf naar hoe je dat zou zou doen als je een integraal wel uitrekenen en in ons geval gaan we de integraal uit van chinas x tussen nul en. Dat zijn de drie stappen die je moet de eerste is dat je een box definieert ja dus een een een recht toe om de integratie gebiedt hij en je moet zorgen dat je een oppervlakte hiervan kent. Aan ons geval zouden een mooi boek zijn het bos tussen nul en op de x as en tussen nul en één op de ajacied want we weten dat dat integratiegebied je binnenvalt namelijk in het gebied onder de de vraag is nu hoe groot. Is de oppervlakte dat dan de tweede stap is dat men renner getallen gaan gooien in de als je een renner getal tussen nul en. En dat is waarneemt en vervolgens een getal tussen nul en één als waren dan verschijnt er een punt in de. Dit kan natuurlijk heel zou doen en wat een is voor elk punt punt is om een fout punt en een goed punt is een punt dat in het integratiegebied ligt en er gouden punten punten baan in het integratie- gebied ligt. Een punt dat we nu op het scherm getuigen hebben ligt in het integratiebeleid en is dus groen is goed maar je houdt punt te genereren die fout zijn die buiten het integratiegebied vallen. Als je een heleboel keer kan je het hoogste integraal schatten namen de fractie van het punten die goed zijn fractie van de punten binnen het integratiegebied. Maal de oppervlakte van den bosch als bijvoorbeeld zestig procent van de punten in het integratiegebied valt dan in zou schatting van integraal zestig procent van de oppervlakte van de box een zestig procent van ik heb dit voorbeeld zelf bij de uitwerking van tweeduizend punten. Links zie je de van goede en slechte punten die ik getekend. Ik weet dat dat boksen oppervlak pi heeft dat pas stap één stap twee was tweeduizend brenner puntig mooie dagen gebeld dat de twaalfhonderd negenentachtig een goed zijn en daarmee kan ik de integraal schatten wij namelijk dat. Twaalfhonderd negenentachtig gedeelde tweeduizend van de zes had daarmee de oppervlakte van een op één komma negen zes nul drie en natuurlijk kan tweeduizend kunt doen maar kan een les goed met tweehonderdduizend punten toe. Hiermee kan je in gauw oplossen zelfs als de functie niet analytisch bekend. Twee de aan de gang gaan één tekende altijd op een scherm geef je heel snel inzicht in hoe de eruitziet maar ook of jij je punten wel precies goed hoor en twee testjes allemaal nog van integraal waarvan je de uitkomst al bij.'
kaldi_hypothesis = cleanstring(kaldi_hypothesis)
print(f"cleaned hyp {kaldi_hypothesis}")
kaldi = wer(ref, kaldi_hypothesis, True)

print(f" Kaldi error:  { round(kaldi, 3) }")
