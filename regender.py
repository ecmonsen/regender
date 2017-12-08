# Practicing tree traversal
# TODO: Clean up this code
# TODO Make code generic
# TODO A way to substitute names, e.g. Bob instead of Lizzy
# TODO Handle contractions like "I'm"
# TODO Find a better stemmer - Lancaster?

from nltk.tree import Tree
import trigram
import nltk
import argparse
import sys

# str = ''
#
#
# def append_str(x):
#     global str
#     str = str + ' ' + x


lone_her = 0


def traverseTree(tree, func=lambda x: x):
    global lone_her
    # print("tree:", tree)
    for subtree in tree:
        if type(subtree) == Tree:
            if len(subtree) == 1 and subtree[0][0].lower() == 'her':
                #print("lone 'her'")
                lone_her = lone_her + 1
                traverseTree(subtree, func)
            else:
                traverseTree(subtree, func)
        elif type(subtree) == tuple:
            func(subtree[0])
        else:
            #print(type(subtree))
            func(subtree)


# Now to reconstruct the text from the tree
# 1. read in yaml and construct the rules
import re
re.match("[Hh]er", "her")
rules_old = {
    # Regex to describe word
    ("[Hh]er", "PRP"): {
        "replacement": "him"
    },
    ("Her", "PRP"): {
        "replacement": "Him"
    },
    ("her", "PRP$"): {
        "replacement": "his"
    },
    ("Her", "PRP$"): {
        "replacement": "His"
    },
    ("She", "PRP"): {
        "replacement": "He"
    },
    ("she", "PRP"): {
        "replacement": "he"
    },
    ("him", "PRP"): {
        "replacement": "her"
    },
    ("Him", "PRP"): {
        "replacement": "Her"
    },
    ("He", "PRP"): {
        "replacement": "She"
    },
    ("he", "PRP"): {
        "replacement": "she"
    },
    ("his", "PRP$"): {
        "replacement": "her"
    },
    ("His", "PRP$"): {
        "replacement": "Her"
    },

}

rules_stem = {
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
    "lord": {"parts_of_speech": {"NNP": {"replacement": "lady"}}}
}

# TODO make configurable
stemmer = nltk.PorterStemmer()
import inflect
inflect_engine = inflect.engine()

# def get_replacement_rule(tpl, rules):
#     # Simplest:
#     return tpl in rules
#     # # Stem:
#     global stemmer
#     stemword = stemmer.stem(tpl[0])
#     return rules[stemword] if stemword in rules else None
#     # (p.stem(tpl[0]), tpl[1])
#     # re.match('^{0}$'.format())

def replace_word(tpl, rules):
    (word, pos) = tpl

    # Get the rule
    if word in rules:
        rule = rules[word.lower()]
    else:
        global stemmer
        stem = stemmer.stem(word)

        if stem in rules:
            rule = rules[stem]
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
        word2 = inflect_engine.plural(word2)

    return word2

def replace_text(tree, rules):
    for subtree in tree:
        if type(subtree) == Tree:
            replace_text(subtree, rules)


def reflatten_text(tree, rules, text=''):
    # print("tree:", tree)
    for subtree in tree:
        # If a tree, does it have a single leaf?
        if type(subtree) == Tree:
            text = reflatten_text(subtree, rules, text)
        elif type(subtree)==tuple:
            if subtree[0]=="''":
                # Remove space before end quote
                text = text.rstrip(" ")+'" '
            elif subtree[0]=="``":
                # Do not add space after start quote
                text = text + '"'
            elif subtree[0]==subtree[1] or subtree[1] in [".", ":", ","]: # end of sentence punctuation
                # add punctuation with no extra space
                text = text.rstrip(" ") + subtree[0]+ ' '
            else:
                text = text + replace_word(subtree, rules) + ' '
        else:
            pass
            # print(type(subtree))
            # print(subtree)
    return text

class GenderSwapper():
    def __init__(self, tokenize,tag, chunk, line_delimiter="\n"):
        self.tokenize = tokenize
        self.tag = tag
        self.chunk = chunk


    def swap_gender(self, stream):
        while True:
            line = stream.readline()
            if not line:
                break
            yield reflatten_text(
                self.chunk(
                    self.tag(
                        self.tokenize(line)
                    )
                ),
            rules_stem)

#todo rename, stream
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Text file to gender-swap")
    args = parser.parse_args()

    #print(dir(args))
    swapper = GenderSwapper(tokenize=lambda line: nltk.word_tokenize(line),
                            tag=lambda tok_line: nltk.pos_tag(tok_line),
                            chunk=lambda line: trigram.trigram_chunker.parse(line))

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

def pp(path):
    pp_text = open(path, 'r').read()
    # pp_tokens = nltk.word_tokenize(pp_text)
    # pp_tagged = nltk.pos_tag(pp_tokens)
    # pp_chunked = trigram.trigram_chunker.parse(pp_tagged)

    # Now to reconstruct the text from the tree
    global pp_text_split
    global pp_tokens_split
    global pp_tagged_split
    global pp_chunked_split

    #
    pp_text_split = pp_text.split("\n")
    pp_tokens_split = [nltk.word_tokenize(line) for line in pp_text_split]
    pp_tagged_split = [nltk.pos_tag(tokenized_line) for tokenized_line in pp_tokens_split]
    pp_chunked_split = [trigram.trigram_chunker.parse(line) for line in pp_tagged_split]

    return pp_chunked_split

def do_replacement():
    """
    Call this after pp()
    :return: 
    """
    replaced = [reflatten_text(chunk, rules_stem) for chunk in pp_chunked_split]
    with open("Ungendered.txt", "w") as f:
        f.write("\n".join(replaced))


    proper_nouns = [[tf[i][0] if i == 0 else "{0} {1}".format(tf[i-1][0], tf[i][0])  for i in range(0, len(tf)) if (i==0 and tf[i][1]=="NNP" and tf[i+1][1]!="NNP") or (i>0 and tf[i-1][1]=="NNP" and tf[i][1]=="NNP")] for tf in [t.flatten() for t in main.pp_chunked_split]]
    proper_nouns_flat = [item for sublist in proper_nouns for item in sublist]
    with open("ProperNames.txt", "w") as f:
        f.write("\n".join(sorted(set(proper_nouns_flat))))

if __name__ == "__main__":
    main()


#readline.get_current_history_length()
# readline.get_history_item()
#import readline
#with open("History.txt", "w") as f:
#    f.write("\n".join([readline.get_history_item() for i in range(0, readline.get_current_history_length())])+ "\n")
# proper_nouns = [[tf[i][0] if i == 0 else "{0} {1}".format(tf[i-1][0], tf[i][0])  for i in range(0, len(tf)) if (i==0 and tf[i][1]=="NNP" and tf[i+1][1]!="NNP") or (i>0 and tf[i-1][1]=="NNP" and tf[i][1]=="NNP")] for tf in [t.flatten() for t in pp.pp_chunked_split]]
