# Practicing tree traversal
# TODO: Clean up this code
# TODO Make code generic
# TODO A way to substitute names, e.g. Bob instead of Lizzy
# TODO Handle contractions like "I'm"

import argparse
import sys
import pattern.en # parser
import pattern.vector # stemmer
import inflect

DEFAULT_RULES = {
    "her": {
        "parts_of_speech": {
            "PRP": {
                "replacement": "him"
            },
            "NN": {
                "replacement": "him"
            },
            "PRP$" : {
                "replacement": "his"
            },
            "NNP": {
                "replacement": "his"
            }
        }
    },
    "she": {"parts_of_speech": {"*": {"replacement": "he"}}},
    "he": {"parts_of_speech": {"*": {"replacement": "she"}}},
    "him": {"parts_of_speech": {"*": {"replacement": "her"}}},
    "his": {"parts_of_speech": {"*": {"replacement": "her"}}},
    "hers": {"parts_of_speech": {"*": {"replacement": "his"}}},
    "herself": {"parts_of_speech": {"*": {"replacement": "himself"}}},
    "himself": {"parts_of_speech": {"*": {"replacement": "herself"}}},
    "niece": {"parts_of_speech": {"*": {"replacement": "nephew"}}},
    "nephew": {"parts_of_speech": {"*": {"replacement": "niece"}}},
    "aunt": {"parts_of_speech": {"*": {"replacement": "uncle"}}},
    "uncle": {"parts_of_speech": {"*": {"replacement": "aunt"}}},
    "mother": {"parts_of_speech": {"*": {"replacement": "father"}}},
    "father": {"parts_of_speech": {"*": {"replacement": "mother"}}},
    "brother": {"parts_of_speech": {"*": {"replacement": "sister"}}},
    "sister": {"parts_of_speech": {"*": {"replacement": "brother"}}},
    "daughter": {"parts_of_speech": {"*": {"replacement": "son"}}},
    "son": {"parts_of_speech": {"*": {"replacement": "daughter"}}},
    "woman": {"parts_of_speech": {"*": {"replacement": "man"}}},
    "man": {"parts_of_speech": {"*": {"replacement": "woman"}}},
    "girl": {"parts_of_speech": {"*": {"replacement": "boy"}}},
    "boy": {"parts_of_speech": {"*": {"replacement": "girl"}}},
    "wife": {"parts_of_speech": {"*": {"replacement": "husband"}}},
    "husband": {"parts_of_speech": {"*": {"replacement": "wife"}}},
    "mr.": {"parts_of_speech": {"*": {"replacement": "ms."}}},
    "mrs.": {"parts_of_speech": {"*": {"replacement": "mr."}}},
    "ms.": {"parts_of_speech": {"*": {"replacement": "mr."}}},
    "sir": {"parts_of_speech": {"*": {"replacement": "madam"}}},
    "madam": {"parts_of_speech": {"*": {"replacement": "sir"}}},
    "ma'am": {"parts_of_speech": {"*": {"replacement": "sir"}}},
    "women": {"parts_of_speech": {"*": {"replacement": "men"}}},
    "men": {"parts_of_speech": {"*": {"replacement": "women"}}},
    "lady": {"parts_of_speech": {"NNP": {"replacement": "lord"}, "*": {"replacement": "gentleman"}}},
    "gentleman": {"parts_of_speech": {"*": {"replacement": "lady"}}},
    "gentlemen": {"parts_of_speech": {"*": {"replacement": "ladies"}}},
    "ladies": {"parts_of_speech": {"*": {"replacement": "gentlemen"}}},
    "lord": {"parts_of_speech": {"NNP": {"replacement": "lady"}}},
    "mamma": {"parts_of_speech": {"NNP": {"replacement": "pappa"}}}
}


class PatternGenderSwapper():
    def __init__(self, replacement_rules=DEFAULT_RULES, preprocess=None, postprocess=None):
        self.replacement_rules = replacement_rules
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.inflect_engine = inflect.engine()

    def get_proper_names(self, stream):
        proper_names=set()
        while True:
            line = stream.readline()
            if self.preprocess:
                line = self.preprocess(line)
            if not line:
                break
            proper_names = proper_names.union(set(self._proper_names(line, pattern.en.parsetree(line))))

        return proper_names

    def _proper_names(self, original_text, pattern_tree):
        pn = []
        for s in pattern_tree:
            for t in s.chunked():
                for w in t:
                    if w.pos=="NNP":
                        pn.append((w.string, t.string, s.string))

        return pn

    def swap_gender(self, stream):
        while True:
            line = stream.readline()
            if not line:
                break
            line = self.preprocess(line) if self.preprocess else line
            line = self.replace_in_text(line, pattern.en.parsetree(line))
            line = self.postprocess(line) if self.postprocess else line
            yield line

    def replace_in_text(self, original_text, pattern_tree):
        text = ""
        index_in_original = 0

        for pattern_sentence in pattern_tree:
            for word in pattern_sentence:
                #print "'{0}' ({1})".format(word.string, word.pos)
                start_index = original_text.find(word.string, index_in_original)
                preceding_whitespace = original_text[index_in_original:start_index]
                index_in_original = start_index+len(word.string)
                text = text + preceding_whitespace + self.replace_word((word.string, word.pos))
        remaining_whitespace = original_text[index_in_original:len(original_text)]
        text = text + remaining_whitespace
        return text.rstrip("\n")

    def replace_word(self, tpl):
        (word, pos) = tpl
        s_word = pattern.en.singularize(word) if pos == "NNS" else word

        # Get the rule
        if word in self.replacement_rules:
            rule = self.replacement_rules[s_word.lower()]
        else:
            stem = pattern.vector.stem(word, stemmer=pattern.vector.LEMMA).lower()

            if stem in self.replacement_rules:
                rule = self.replacement_rules[stem]
            else:
                return word

        posrule = rule["parts_of_speech"].get(pos, rule["parts_of_speech"].get("*"))
        if not posrule:
            # Nothing to do
            #print("Warning: No posrule for {0}".format(tpl))
            return word

        word2 = posrule["replacement"].title() if word[:1].isupper() else posrule["replacement"]
        if pos=="NNS":
            # The word was originally plural
            word2 = pattern.en.pluralize(word2)

        return word2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Text file to gender-swap")
    args = parser.parse_args()

    swapper = PatternGenderSwapper()
    close_fp = False

    if not args.file:
        fp = sys.stdin
    else:
        fp = open(args.file, 'r')
        close_fp = True

    for line in swapper.swap_gender(fp):
        print(line)

    if close_fp:
        fp.close()

if __name__ == "__main__":
    main()

