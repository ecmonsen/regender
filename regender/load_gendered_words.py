import json
import os

def load_gendered_words(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "gendered_words.json")

    new_words = {}
    with open(path,"r") as f:
        j = json.load(f)
        # Transform for use in regender code
        for old_obj in j:
            from_word = old_obj["word"]
            new_obj = new_words.get(from_word, False)
            if not new_obj:
                new_obj = { } # TODO

            # if new_obj["gender"]!=old_obj.get("gender", new_obj["gender"]):
            #     raise Exception("Found opposing genders for word '{}'".format(from_word))
            #

            if "gender_map" in old_obj:
                new_pos_obj = new_obj.get("parts_of_speech", False)
                if not new_pos_obj:
                    new_pos_obj = new_obj["parts_of_speech"] = {}
                gm = old_obj.get("gender_map", {})
                poslist = gm.get("m", gm.get("f", []))
                for positem in poslist:
                    poss = positem["parts_of_speech"].split(",")
                    for pos in poss:
                        new_pos_obj[pos] = {"replacement": positem["word"]}

                new_words[from_word] = new_obj

        return new_words





# From:
# {"word":"her", "gender": "f", "gender_map": {"m": [{"parts_of_speech": "PRP,NN", "word": "him"}]}},
# {"word":"her", "gender": "f", "gender_map": {"m": [{"parts_of_speech": "PRP$,NNP", "word": "his"}]}},

# To:
# DEFAULT_RULES = {
#     "her": {
#         "parts_of_speech": {
#             "PRP": { "replacement": "him" },
#             "NN": { "replacement": "him" },
#             "PRP$" : { "replacement": "his" },
#             "NNP": { "replacement": "his" }
#         }
#     },
#     "she": {"parts_of_speech": {"*": {"replacement": "he"}}},