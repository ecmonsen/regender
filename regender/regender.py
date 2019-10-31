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
import io
from load_gendered_words import  load_gendered_words
DEFAULT_RULES = load_gendered_words()

class PatternGenderSwapper():
    """
    Swaps genders in each line of text, using the "pattern.en" library to tokenize and tag parts of speech.
    """
    def __init__(self, replacement_rules=DEFAULT_RULES, preprocess=None, postprocess=None,
                 postprocess_word=None):
        self.replacement_rules = replacement_rules
        self.preprocess = preprocess
        self.postprocess = postprocess
        self.postprocess_word = postprocess_word
        self.inflect_engine = inflect.engine()

    def get_proper_names(self, stream):
        """
        Extract the proper names from text
        :param stream:
        :return:
        """
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
        """
        Swap genders in lines of text. Lines of text are independent from each other
        (no context is saved)
        :param stream: Input stream with text
        :return: Array of lines of text with genders swapped
        """
        lines = 0
        try:
            while True:
                line0 = stream.readline()
                if not line0:
                    break
                line = self.preprocess(line0) if self.preprocess else line0
                line = self.replace_in_text(line, pattern.en.parsetree(line))
                line = self.postprocess(line) if self.postprocess else line
                lines = lines+1
                yield line
        except StandardError as e:
            print "Error in line {}. Text of line:"
            print line
            print sys.exc_info()
            raise e

    def replace_in_text(self, original_text, pattern_tree):
        """
        Swap genders in one line of text by replacing gender-specific words
        according to self.replacement_rules. Preserves all other parts of the
        original text including punctuation and whitespace if possible.

        :param original_text: The line of text
        :param pattern_tree: Tokenized, POS-tagged text in the format returned by
            the pattern.en library.
        :return:
        """
        text = ""
        index_in_original = 0

        for pattern_sentence in pattern_tree:
            for word in pattern_sentence:
                #print "'{0}' ({1})".format(word.string, word.pos)
                # Map the token to the original text
                start_index = original_text.find(word.string, index_in_original)
                # Preserve the original whitespace
                preceding_whitespace = original_text[index_in_original:start_index]
                index_in_original = start_index+len(word.string)
                text = text + preceding_whitespace + self.replace_word((word.string, word.pos))
        remaining_whitespace = original_text[index_in_original:len(original_text)]
        text = text + remaining_whitespace
        return text.rstrip("\n")

    def replace_word(self, tpl):
        (word, pos) = tpl
        # Get the singular form of the word
        s_word = (pattern.en.singularize(word) if pos == "NNS" else word).lower()

        # Get the rule
        if s_word in self.replacement_rules:
            rule = self.replacement_rules[s_word]
        else:
            # Look for a rule based on the word's stem
            stem = pattern.vector.stem(word, stemmer=pattern.vector.LEMMA).lower()

            if stem in self.replacement_rules:
                rule = self.replacement_rules[stem]
            else:
                return self.postprocess_word(word) if self.postprocess_word else word

        # Look for a rule specific to the part of speech, or if none, a rule for any POS (denoted "*")
        posrule = rule["parts_of_speech"].get(pos, rule["parts_of_speech"].get("*"))
        if not posrule:
            # Nothing to do
            #print("Warning: No posrule for {0}".format(tpl))
            return word

        word2 = posrule["replacement"].title() if word[:1].isupper() else posrule["replacement"]
        if pos=="NNS":
            # The word was originally plural, so reconstruct the plural gender-swapped word
            word2 = pattern.en.pluralize(word2)

        return self.postprocess_word(word2) if self.postprocess_word else word2

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Text file to gender-swap")
    args = parser.parse_args()

    swapper = PatternGenderSwapper()
    close_fp = False

    if not args.file:
        fp = sys.stdin
    else:
        fp = io.open(args.file, 'r', encoding='utf-8 sig')
        close_fp = True

    for line in swapper.swap_gender(fp):
        print(line.encode("utf-8"))

    if close_fp:
        fp.close()

if __name__ == "__main__":
    main()

