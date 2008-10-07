# Copyright (c) 2008 Michael Dirolf (mike at dirolf dot com)

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

"""pyporter2: An implementation of the Porter2 stemming algorithm.

See http://snowball.tartarus.org/algorithms/english/stemmer.html"""
import unittest, re

regexp = re.compile(r"[^aeiouy]*[aeiouy]+[^aeiouy](\w*)")
def get_r1(word):
    # exceptional forms
    if word.startswith('gener') or word.startswith('arsen'):
        return 5
    if word.startswith('commun'):
        return 6

    # normal form
    match = regexp.match(word)
    if match:
        return match.start(1)
    return len(word)

def get_r2(word):
    match = regexp.match(word, get_r1(word))
    if match:
        return match.start(1)
    return len(word)

def ends_with_short_syllable(word):
    if len(word) == 2:
        if re.match(r"^[aeiouy][^aeiouy]$", word):
            return True
    if re.match(r".*[^aeiouy][aeiouy][^aeiouywxY]$", word):
        return True
    return False

def is_short_word(word):
    if ends_with_short_syllable(word):
        if get_r1(word) == len(word):
            return True
    return False

def remove_initial_apostrophe(word):
    if word.startswith("'"):
        return word[1:]
    return word

def capitalize_consonant_ys(word):
    if word.startswith('y'):
        word = 'Y' + word[1:]
    return re.sub(r"([aeiouy])y", '\g<1>Y', word)

def step_0(word):
    if word.endswith("'s'"):
        return word[:-3]
    if word.endswith("'s"):
        return word[:-2]
    if word.endswith("'"):
        return word[:-1]
    return word

def step_1a(word):
    if word.endswith('sses'):
        return word[:-4] + 'ss'
    if word.endswith('ied') or word.endswith('ies'):
        if len(word) > 4:
            return word[:-3] + 'i'
        else:
            return word[:-3] + 'ie'
    if word.endswith('us') or word.endswith('ss'):
        return word
    if word.endswith('s'):
        preceding = word[:-1]
        if re.search(r"[aeiouy].", preceding):
            return preceding
        return word
    return word

def step_1b(word, r1):
    if word.endswith('eedly'):
        if len(word) - 5 >= r1:
            return word[:-3]
        return word
    if word.endswith('eed'):
        if len(word) - 3 >= r1:
            return word[:-1]
        return word

    def ends_with_double(word):
        doubles = ['bb', 'dd', 'ff', 'gg', 'mm', 'nn', 'pp', 'rr', 'tt']
        for double in doubles:
            if word.endswith(double):
                return True
        return False

    def step_1b_helper(word):
        if word.endswith('at') or word.endswith('bl') or word.endswith('iz'):
            return word + 'e'
        if ends_with_double(word):
            return word[:-1]
        if is_short_word(word):
            return word + 'e'
        return word

    suffixes = ['ed', 'edly', 'ing', 'ingly']
    for suffix in suffixes:
        if word.endswith(suffix):
            preceding = word[:-len(suffix)]
            if re.search(r"[aeiouy]", preceding):
                return step_1b_helper(preceding)
            return word

    return word

def step_1c(word):
    if word.endswith('y') or word.endswith('Y'):
        if word[-2] not in 'aeiouy':
            if len(word) > 2:
                return word[:-1] + 'i'
    return word

def step_2(word, r1):
    def step_2_helper(end, repl, prev):
        if word.endswith(end):
            if len(word) - len(end) >= r1:
                if prev == []:
                    return word[:-len(end)] + repl
                for p in prev:
                    if word[:-len(end)].endswith(p):
                        return word[:-len(end)] + repl
            return word
        return None

    triples = [('ization', 'ize', []),
               ('ational', 'ate', []),
               ('fulness', 'ful', []),
               ('ousness', 'ous', []),
               ('iveness', 'ive', []),
               ('tional', 'tion', []),
               ('biliti', 'ble', []),
               ('lessli', 'less', []),
               ('entli', 'ent', []),
               ('ation', 'ate', []),
               ('alism', 'al', []),
               ('aliti', 'al', []),
               ('ousli', 'ous', []),
               ('iviti', 'ive', []),
               ('fulli', 'ful', []),
               ('enci', 'ence', []),
               ('anci', 'ance', []),
               ('abli', 'able', []),
               ('izer', 'ize', []),
               ('ator', 'ate', []),
               ('alli', 'al', []),
               ('bli', 'ble', []),
               ('ogi', 'og', ['l']),
               ('li', '', ['c', 'd', 'e', 'g', 'h', 'k', 'm', 'n', 'r', 't'])]

    for trip in triples:
        attempt = step_2_helper(trip[0], trip[1], trip[2])
        if attempt:
            return attempt

    return word

def step_3(word, r1, r2):
    def step_3_helper(end, repl, r2_necessary):
        if word.endswith(end):
            if len(word) - len(end) >= r1:
                if not r2_necessary:
                    return word[:-len(end)] + repl
                else:
                    if len(word) - len(end) >= r2:
                        return word[:-len(end)] + repl
            return word
        return None

    triples = [('ational', 'ate', False),
               ('tional', 'tion', False),
               ('alize', 'al', False),
               ('icate', 'ic', False),
               ('iciti', 'ic', False),
               ('ative', '', True),
               ('ical', 'ic', False),
               ('ness', '', False),
               ('ful', '', False)]

    for trip in triples:
        attempt = step_3_helper(trip[0], trip[1], trip[2])
        if attempt:
            return attempt

    return word

def step_4(word, r2):
    delete_list = ['al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent', 'ism', 'ate', 'iti', 'ous', 'ive', 'ize']

    for end in delete_list:
        if word.endswith(end):
            if len(word) - len(end) >= r2:
                return word[:-len(end)]
            return word

    if word.endswith('sion') or word.endswith('tion'):
        if len(word) - 3 >= r2:
            return word[:-3]

    return word

def step_5(word, r1, r2):
    if word.endswith('l'):
        if len(word) - 1 >= r2 and word[-2] == 'l':
            return word[:-1]
        return word

    if word.endswith('e'):
        if len(word) - 1 >= r2:
            return word[:-1]
        if len(word) - 1 >= r1 and not ends_with_short_syllable(word[:-1]):
            return word[:-1]

    return word

def normalize_ys(word):
    return word.replace('Y', 'y')

exceptional_forms = {'skis': 'ski',
                    'skies': 'sky',
                    'dying': 'die',
                    'lying': 'lie',
                    'tying': 'tie',
                    'idly': 'idl',
                    'gently': 'gentl',
                    'ugly': 'ugli',
                    'early': 'earli',
                    'only': 'onli',
                    'singly': 'singl',
                    'sky': 'sky',
                    'news': 'news',
                    'howe': 'howe',
                    'atlas': 'atlas',
                    'cosmos': 'cosmos',
                    'bias': 'bias',
                    'andes': 'andes'}

exceptional_early_exit_post_1a = ['inning', 'outing', 'canning', 'herring', 'earring', 'proceed', 'exceed', 'succeed']

def stem(word):
    """The main entry point in the old version of the API."""
    raise DeprecationWarning('stem() is deprecated starting with v1.0.0')

def algorithms():
    """Get a list of the names of the available stemming algorithms.

    The only algorithm currently supported is the "english", or porter2,
    algorithm.
    """
    return ['english']

def version ():
    """Get the version number of the stemming module.

    This is the version number of the Stemmer module as a whole (not for an
    individual algorithm).
    """
    return '1.0.0'

class Stemmer:
    """An instance of a stemming algorithm.

    When creating a Stemmer object, there is one required argument:
    the name of the algorithm to use in the new stemmer. A list of the
    valid algorithm names may be obtained by calling the algorithms()
    function in this module. In addition, the appropriate stemming algorithm
    for a given language may be obtained by using the 2 or 3 letter ISO 639
    language codes.
    """
    max_cache_size = 10000

    def __init__ (self, algorithm, cache_size=None):
        if algorithm not in ['english', 'eng', 'en']:
            raise KeyError("Stemming algorithm '%s' not found" % algorithm)
        if cache_size:
            self.max_cache_size = cache_size

    def stemWord(self, word):
        """Stem a word.

        This takes a single argument, word, which should either be a UTF-8
        encoded string, or a unicode object.

        The result is the stemmed form of the word. If the word supplied
        was a unicode object, the result will be a unicode object: if the
        word supplied was a string, the result will be a UTF-8 encoded string.
        """
        return Stemmer._stem(word)

    def stemWords(self, words):
        """Stem a list of words.

        This takes a single argument, words, which must be a sequence,
        iterator, generator or similar.

        The entries in words should either be UTF-8 encoded strings,
        or a unicode objects.

        The result is a list of the stemmed forms of the words. If the word
        supplied was a unicode object, the stemmed form will be a unicode
        object: if the word supplied was a string, the stemmed form will
        be a UTF-8 encoded string.
        """
        return [self.stemWord(word) for word in words]

    @classmethod
    def _stem(cls, word):
        was_unicode = False

        if isinstance(word, unicode):
            was_unicode = True
            word = word.encode('utf-8')

        if len(word) <= 2:
            return word
        word = remove_initial_apostrophe(word)

        # handle some exceptional forms
        if word in exceptional_forms:
            return exceptional_forms[word]

        word = capitalize_consonant_ys(word)
        r1 = get_r1(word)
        r2 = get_r2(word)
        word = step_0(word)
        word = step_1a(word)

        # handle some more exceptional forms
        if word in exceptional_early_exit_post_1a:
            return word

        word = step_1b(word, r1)
        word = step_1c(word)
        word = step_2(word, r1)
        word = step_3(word, r1, r2)
        word = step_4(word, r2)
        word = step_5(word, r1, r2)
        word = normalize_ys(word)

        if was_unicode:
            return word.decode('utf-8')
        return word

class TestPorter2(unittest.TestCase):
    def setUp(self):
        pass

    def testModule(self):
        self.assertEqual(algorithms(), ['english'])
        self.assertEqual(version(), '1.0.0')
        self.assertRaises(KeyError, Stemmer, 'porter')
        self.assertRaises(KeyError, Stemmer, 'random')
        stemmer = Stemmer('english')
        stemmer = Stemmer('en')
        stemmer = Stemmer('eng')

    def testDeprecation(self):
        self.assertRaises(DeprecationWarning, stem, 'stemming')

    def testGetR1(self):
        self.assertEqual(get_r1('beautiful'), 5)
        self.assertEqual(get_r1('beauty'), 5)
        self.assertEqual(get_r1('beau'), 4)
        self.assertEqual(get_r1('animadversion'), 2)
        self.assertEqual(get_r1('sprinkled'), 5)
        self.assertEqual(get_r1('eucharist'), 3)

        # test exceptional forms
        self.assertEqual(get_r1('gener'), 5)
        self.assertEqual(get_r1('generous'), 5)
        self.assertEqual(get_r1('generousity'), 5)
        self.assertEqual(get_r1('general'), 5)
        self.assertEqual(get_r1('generally'), 5)
        self.assertEqual(get_r1('generality'), 5)
        self.assertEqual(get_r1('commun'), 6)
        self.assertEqual(get_r1('communist'), 6)
        self.assertEqual(get_r1('communal'), 6)
        self.assertEqual(get_r1('communistic'), 6)
        self.assertEqual(get_r1('arsen'), 5)
        self.assertEqual(get_r1('arsenic'), 5)
        self.assertEqual(get_r1('arsenal'), 5)
        self.assertEqual(get_r1('arsenality'), 5)

    def testGetR2(self):
        self.assertEqual(get_r2('beautiful'), 7)
        self.assertEqual(get_r2('beauty'), 6)
        self.assertEqual(get_r2('beau'), 4)
        self.assertEqual(get_r2('animadversion'), 4)
        self.assertEqual(get_r2('sprinkled'), 9)
        self.assertEqual(get_r2('eucharist'), 6)

    def testEndsWithShortSyllable(self):
        self.assertEqual(ends_with_short_syllable(''), False)
        self.assertEqual(ends_with_short_syllable('rap'), True)
        self.assertEqual(ends_with_short_syllable('trap'), True)
        self.assertEqual(ends_with_short_syllable('entrap'), True)
        self.assertEqual(ends_with_short_syllable('ow'), True)
        self.assertEqual(ends_with_short_syllable('on'), True)
        self.assertEqual(ends_with_short_syllable('at'), True)
        self.assertEqual(ends_with_short_syllable('uproot'), False)
        self.assertEqual(ends_with_short_syllable('bestow'), False)
        self.assertEqual(ends_with_short_syllable('disturb'), False)

    def testIsShortWord(self):
        self.assertEqual(is_short_word(''), False)
        self.assertEqual(is_short_word('bed'), True)
        self.assertEqual(is_short_word('shed'), True)
        self.assertEqual(is_short_word('shred'), True)
        self.assertEqual(is_short_word('bead'), False)
        self.assertEqual(is_short_word('embed'), False)
        self.assertEqual(is_short_word('beds'), False)

    def testRemoveInitialApostrophe(self):
        self.assertEqual(remove_initial_apostrophe(''), '')
        self.assertEqual(remove_initial_apostrophe('mike'), 'mike')
        self.assertEqual(remove_initial_apostrophe('\'mike'), 'mike')
        self.assertEqual(remove_initial_apostrophe('\'mi\'e'), 'mi\'e')
        self.assertEqual(remove_initial_apostrophe('\'til'), 'til')

    def testCapitalizeConsonantYs(self):
        self.assertEqual(capitalize_consonant_ys(''), '')
        self.assertEqual(capitalize_consonant_ys('mike'), 'mike')
        self.assertEqual(capitalize_consonant_ys('youth'), 'Youth')
        self.assertEqual(capitalize_consonant_ys('boy'), 'boY')
        self.assertEqual(capitalize_consonant_ys('boyish'), 'boYish')
        self.assertEqual(capitalize_consonant_ys('fly'), 'fly')
        self.assertEqual(capitalize_consonant_ys('flying'), 'flying')
        self.assertEqual(capitalize_consonant_ys('syzygy'), 'syzygy')
        self.assertEqual(capitalize_consonant_ys('sayyid'), 'saYyid')

    def testStep0(self):
        self.assertEqual(step_0(''), '')
        self.assertEqual(step_0('mike'), 'mike')
        self.assertEqual(step_0('dog\'s'), 'dog')
        self.assertEqual(step_0('dog\'s\''), 'dog')
        self.assertEqual(step_0('dog\''), 'dog')

    def testStep1a(self):
        self.assertEqual(step_1a(''), '')
        self.assertEqual(step_1a('caresses'), 'caress')
        self.assertEqual(step_1a('sses'), 'ss')
        self.assertEqual(step_1a('ssesmike'), 'ssesmike')
        self.assertEqual(step_1a('tied'), 'tie')
        self.assertEqual(step_1a('cries'), 'cri')
        self.assertEqual(step_1a('ties'), 'tie')
        self.assertEqual(step_1a('hurried'), 'hurri')
        self.assertEqual(step_1a('gas'), 'gas')
        self.assertEqual(step_1a('this'), 'this')
        self.assertEqual(step_1a('gaps'), 'gap')
        self.assertEqual(step_1a('kiwis'), 'kiwi')
        self.assertEqual(step_1a('bus'), 'bus')
        self.assertEqual(step_1a('mikeus'), 'mikeus')
        self.assertEqual(step_1a('mikess'), 'mikess')
        self.assertEqual(step_1a('truss'), 'truss')

    def testStep1b(self):
        self.assertEqual(step_1b('', 0), '')
        self.assertEqual(step_1b('ed', 0), 'ed')
        self.assertEqual(step_1b('eed', 1), 'eed')
        self.assertEqual(step_1b('ing', 0), 'ing')
        self.assertEqual(step_1b('heed', 2), 'heed')
        self.assertEqual(step_1b('coheed', 2), 'cohee')
        self.assertEqual(step_1b('coheed', 3), 'cohee')
        self.assertEqual(step_1b('heedly', 3), 'heedly')
        self.assertEqual(step_1b('heedly', 0), 'hee')
        self.assertEqual(step_1b('shred', 0), 'shred')
        self.assertEqual(step_1b('luxuriated', 0), 'luxuriate')
        self.assertEqual(step_1b('luxuriatedly', 0), 'luxuriate')
        self.assertEqual(step_1b('luxuriating', 0), 'luxuriate')
        self.assertEqual(step_1b('luxuriatingly', 0), 'luxuriate')
        self.assertEqual(step_1b('disabled', 0), 'disable')
        self.assertEqual(step_1b('disablingly', 0), 'disable')
        self.assertEqual(step_1b('cauterizedly', 0), 'cauterize')
        self.assertEqual(step_1b('cauterizing', 0), 'cauterize')
        self.assertEqual(step_1b('hopped', 0), 'hop')
        self.assertEqual(step_1b('clubbing', 0), 'club')
        self.assertEqual(step_1b('troddedly', 0), 'trod')
        self.assertEqual(step_1b('puffingly', 0), 'puf')
        self.assertEqual(step_1b('hagged', 0), 'hag')
        self.assertEqual(step_1b('spamming', 0), 'spam')
        self.assertEqual(step_1b('shunnedly', 0), 'shun')
        self.assertEqual(step_1b('torred', 0), 'tor')
        self.assertEqual(step_1b('catted', 0), 'cat')
        self.assertEqual(step_1b('exazzedly', 0), 'exazz')
        self.assertEqual(step_1b('hoped', 0), 'hope')
        self.assertEqual(step_1b('hopedly', 0), 'hope')
        self.assertEqual(step_1b('hoping', 0), 'hope')
        self.assertEqual(step_1b('hopingly', 0), 'hope')
        self.assertEqual(step_1b('coped', 0), 'cope')

    def testStep1c(self):
        self.assertEqual(step_1c(''), '')
        self.assertEqual(step_1c('cry'), 'cri')
        self.assertEqual(step_1c('by'), 'by')
        self.assertEqual(step_1c('say'), 'say')
        self.assertEqual(step_1c('crY'), 'cri')
        self.assertEqual(step_1c('bY'), 'bY')
        self.assertEqual(step_1c('saY'), 'saY')

    def testStep2(self):
        self.assertEqual(step_2('', 0), '')
        self.assertEqual(step_2('mike', 0), 'mike')
        self.assertEqual(step_2('emotional', 2), 'emotion')
        self.assertEqual(step_2('emotional', 4), 'emotional')
        self.assertEqual(step_2('fenci', 1), 'fence')
        self.assertEqual(step_2('fenci', 2), 'fenci')
        self.assertEqual(step_2('necromanci', 3), 'necromance')
        self.assertEqual(step_2('necromanci', 7), 'necromanci')
        self.assertEqual(step_2('disabli', 3), 'disable')
        self.assertEqual(step_2('disabli', 4), 'disabli')
        self.assertEqual(step_2('evidentli', 2), 'evident')
        self.assertEqual(step_2('evidentli', 5), 'evidentli')
        self.assertEqual(step_2('kaizer', 2), 'kaize')
        self.assertEqual(step_2('kaizer', 3), 'kaizer')
        self.assertEqual(step_2('kaization', 2), 'kaize')
        self.assertEqual(step_2('kaization', 8), 'kaization')
        self.assertEqual(step_2('operational', 2), 'operate')
        self.assertEqual(step_2('operational', 5), 'operational')
        self.assertEqual(step_2('operation', 2), 'operate')
        self.assertEqual(step_2('operation', 5), 'operation')
        self.assertEqual(step_2('operator', 2), 'operate')
        self.assertEqual(step_2('operator', 5), 'operator')
        self.assertEqual(step_2('rationalism', 3), 'rational')
        self.assertEqual(step_2('rationalism', 7), 'rationalism')
        self.assertEqual(step_2('rationaliti', 3), 'rational')
        self.assertEqual(step_2('rationaliti', 7), 'rationaliti')
        self.assertEqual(step_2('rationalli', 3), 'rational')
        self.assertEqual(step_2('rationalli', 7), 'rationalli')
        self.assertEqual(step_2('gratefulness', 4), 'grateful')
        self.assertEqual(step_2('gratefulness', 6), 'gratefulness')
        self.assertEqual(step_2('obviousli', 2), 'obvious')
        self.assertEqual(step_2('obviousli', 5), 'obviousli')
        self.assertEqual(step_2('obviousness', 2), 'obvious')
        self.assertEqual(step_2('obviousness', 5), 'obviousness')
        self.assertEqual(step_2('responsiveness', 7), 'responsive')
        self.assertEqual(step_2('responsiveness', 8), 'responsiveness')
        self.assertEqual(step_2('responsiviti', 3), 'responsive')
        self.assertEqual(step_2('responsiviti', 10), 'responsiviti')
        self.assertEqual(step_2('abiliti', 1), 'able')
        self.assertEqual(step_2('abiliti', 2), 'abiliti')
        self.assertEqual(step_2('cebli', 2), 'ceble')
        self.assertEqual(step_2('cebli', 3), 'cebli')
        self.assertEqual(step_2('apogi', 2), 'apogi')
        self.assertEqual(step_2('illogi', 2), 'illog')
        self.assertEqual(step_2('illogi', 4), 'illogi')
        self.assertEqual(step_2('gracefulli', 4), 'graceful')
        self.assertEqual(step_2('gracefulli', 6), 'gracefulli')
        self.assertEqual(step_2('classlessli', 4), 'classless')
        self.assertEqual(step_2('classlessli', 6), 'classlessli')
        self.assertEqual(step_2('cali', 0), 'cali')
        self.assertEqual(step_2('acli', 0), 'ac')
        self.assertEqual(step_2('acli', 3), 'acli')
        self.assertEqual(step_2('adli', 0), 'ad')
        self.assertEqual(step_2('beli', 0), 'be')
        self.assertEqual(step_2('agli', 2), 'ag')
        self.assertEqual(step_2('agli', 3), 'agli')
        self.assertEqual(step_2('thli', 0), 'th')
        self.assertEqual(step_2('likli', 0), 'lik')
        self.assertEqual(step_2('homili', 0), 'homili')
        self.assertEqual(step_2('tamli', 2), 'tam')
        self.assertEqual(step_2('openli', 0), 'open')
        self.assertEqual(step_2('earli', 3), 'ear')
        self.assertEqual(step_2('earli', 4), 'earli')
        self.assertEqual(step_2('tartli', 2), 'tart')

    def testStep3(self):
        self.assertEqual(step_3('', 0, 0), '')
        self.assertEqual(step_3('mike', 0, 0), 'mike')
        self.assertEqual(step_3('relational', 3, 0), 'relate')
        self.assertEqual(step_3('relational', 4, 9), 'relational')
        self.assertEqual(step_3('emotional', 2, 9), 'emotion')
        self.assertEqual(step_3('emotional', 4, 0), 'emotional')
        self.assertEqual(step_3('rationalize', 3, 0), 'rational')
        self.assertEqual(step_3('rationalize',7, 9), 'rationalize')
        self.assertEqual(step_3('intricate', 2, 9), 'intric')
        self.assertEqual(step_3('intricate', 7, 0), 'intricate')
        self.assertEqual(step_3('intriciti', 2, 0), 'intric')
        self.assertEqual(step_3('intriciti', 5, 9), 'intriciti')
        self.assertEqual(step_3('intrical', 4, 9), 'intric')
        self.assertEqual(step_3('intrical', 5, 0), 'intrical')
        self.assertEqual(step_3('youthful', 4, 0), 'youth')
        self.assertEqual(step_3('youthful', 6, 0), 'youthful')
        self.assertEqual(step_3('happiness', 3, 0), 'happi')
        self.assertEqual(step_3('happiness', 6, 0), 'happiness')
        self.assertEqual(step_3('decorative', 3, 5), 'decor')
        self.assertEqual(step_3('decorative', 3, 6), 'decorative')
        self.assertEqual(step_3('decorative', 6, 5), 'decorative')

    def testStep4(self):
        self.assertEqual(step_4('', 0), '')
        self.assertEqual(step_4('mike', 0), 'mike')
        self.assertEqual(step_4('penal', 3), 'pen')
        self.assertEqual(step_4('penal', 4), 'penal')
        self.assertEqual(step_4('pance', 1), 'p')
        self.assertEqual(step_4('pance', 2), 'pance')
        self.assertEqual(step_4('dence', 0), 'd')
        self.assertEqual(step_4('dence', 4), 'dence')
        self.assertEqual(step_4('header', 3), 'head')
        self.assertEqual(step_4('header', 5), 'header')
        self.assertEqual(step_4('graphic', 5), 'graph')
        self.assertEqual(step_4('graphic', 6), 'graphic')
        self.assertEqual(step_4('table', 0), 't')
        self.assertEqual(step_4('table', 2), 'table')
        self.assertEqual(step_4('quible', 1), 'qu')
        self.assertEqual(step_4('quible', 3), 'quible')
        self.assertEqual(step_4('recant', 1), 'rec')
        self.assertEqual(step_4('recant', 5), 'recant')
        self.assertEqual(step_4('lement', 0), 'l')
        self.assertEqual(step_4('lement', 2), 'lement')
        self.assertEqual(step_4('ment', 0), '')
        self.assertEqual(step_4('ment', 1), 'ment')
        self.assertEqual(step_4('ent', 0), '')
        self.assertEqual(step_4('ent', 2), 'ent')
        self.assertEqual(step_4('schism', 3), 'sch')
        self.assertEqual(step_4('schism', 4), 'schism')
        self.assertEqual(step_4('kate', 1), 'k')
        self.assertEqual(step_4('kate', 2), 'kate')
        self.assertEqual(step_4('citi', 0), 'c')
        self.assertEqual(step_4('citi', 3), 'citi')
        self.assertEqual(step_4('lous', 1), 'l')
        self.assertEqual(step_4('lous', 2), 'lous')
        self.assertEqual(step_4('hive', 0), 'h')
        self.assertEqual(step_4('hive', 3), 'hive')
        self.assertEqual(step_4('ize', 0), '')
        self.assertEqual(step_4('ize', 1), 'ize')

    def testStep5(self):
        self.assertEqual(step_5('mik', 0, 0), 'mik')
        self.assertEqual(step_5('mike', 5, 3), 'mik')
        self.assertEqual(step_5('mike', 5, 4), 'mike')
        self.assertEqual(step_5('mike', 3, 4), 'mike')
        self.assertEqual(step_5('mixe', 3, 4), 'mix')
        self.assertEqual(step_5('recall', 7, 5), 'recal')
        self.assertEqual(step_5('recal', 0, 4), 'recal')
        self.assertEqual(step_5('recall', 0, 6), 'recall')

    def testNormalizeYs(self):
        self.assertEqual(normalize_ys(''), '')
        self.assertEqual(normalize_ys('mike'), 'mike')
        self.assertEqual(normalize_ys('syzygy'), 'syzygy')
        self.assertEqual(normalize_ys('sYzygY'), 'syzygy')
        self.assertEqual(normalize_ys('MiKe'), 'MiKe')
        self.assertEqual(normalize_ys('MDirYol'), 'MDiryol')

    def testStem(self):
        stemmer = Stemmer('english')
        self.assertEqual(stemmer.stemWord(''), '')

        # some normal case tests
        self.assertEqual(stemmer.stemWord('mike'), 'mike')
        self.assertEqual(stemmer.stemWord('consign'), 'consign')
        self.assertEqual(stemmer.stemWord('consigned'), 'consign')
        self.assertEqual(stemmer.stemWord('consigning'), 'consign')
        self.assertEqual(stemmer.stemWord('consignment'), 'consign')
        self.assertEqual(stemmer.stemWord('consist'), 'consist')
        self.assertEqual(stemmer.stemWord('consisted'), 'consist')
        self.assertEqual(stemmer.stemWord('consistency'), 'consist')
        self.assertEqual(stemmer.stemWord('consistent'), 'consist')
        self.assertEqual(stemmer.stemWord('consistently'), 'consist')
        self.assertEqual(stemmer.stemWord('consisting'), 'consist')
        self.assertEqual(stemmer.stemWord('consists'), 'consist')

        # exceptionalWord form tests
        self.assertEqual(stemmer.stemWord('skis'), 'ski')
        self.assertEqual(stemmer.stemWord('skies'), 'sky')
        self.assertEqual(stemmer.stemWord('dying'), 'die')
        self.assertEqual(stemmer.stemWord('lying'), 'lie')
        self.assertEqual(stemmer.stemWord('tying'), 'tie')
        self.assertEqual(stemmer.stemWord('idly'), 'idl')
        self.assertEqual(stemmer.stemWord('gently'), 'gentl')
        self.assertEqual(stemmer.stemWord('ugly'), 'ugli')
        self.assertEqual(stemmer.stemWord('early'), 'earli')
        self.assertEqual(stemmer.stemWord('only'), 'onli')
        self.assertEqual(stemmer.stemWord('singly'), 'singl')
        self.assertEqual(stemmer.stemWord('sky'), 'sky')
        self.assertEqual(stemmer.stemWord('news'), 'news')
        self.assertEqual(stemmer.stemWord('howe'), 'howe')
        self.assertEqual(stemmer.stemWord('atlas'), 'atlas')
        self.assertEqual(stemmer.stemWord('cosmos'), 'cosmos')
        self.assertEqual(stemmer.stemWord('bias'), 'bias')
        self.assertEqual(stemmer.stemWord('andes'), 'andes')
        self.assertEqual(stemmer.stemWord('innings'), 'inning')
        self.assertEqual(stemmer.stemWord('outing'), 'outing')
        self.assertEqual(stemmer.stemWord('canninger'), 'canning')
        self.assertEqual(stemmer.stemWord('herrings'), 'herring')
        self.assertEqual(stemmer.stemWord('earring'), 'earring')
        self.assertEqual(stemmer.stemWord('proceeder'), 'proceed')
        self.assertEqual(stemmer.stemWord('exceeding'), 'exceed')
        self.assertEqual(stemmer.stemWord('succeeds'), 'succeed')

        # hardcore test
        infile = open('./voc.txt', 'r')
        outfile = open('./stemmedvoc.txt', 'r')
        while True:
            word = infile.readline()
            output = outfile.readline()
            if word == '':
                break
            word = word[:-1]
            output = output[:-1]
            self.assertEqual(stemmer.stemWord(word), output)

if __name__ == '__main__':
    unittest.main()
