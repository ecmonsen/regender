# Regender

A project to flip the gender of characters in English text.

Uses the Python NLTK natural language processing library.

## Quick start

System requirements:

* Python 3 with pip
* virtualenv

Clone the [gendered words](https://github.com/ecmonsen/gendered_words) dictionary in a sibling directory to this one (to get the gendered_words.json file needed for translation):


```bash
cd ..
git clone git@github.com:ecmonsen/gendered_words.git
```

Create a Python 3 virtualenv and install requirements:

```bash
virtualenv -p $(which python3) venv
. venv/bin/activate
pip install -r requirements.txt
```

Regender a text:

```bash
python regender/regender.py -f [PATH_TO_FILE]
```

## More
We have a lot of work to do. Stay tuned!

Or, peruse the code.

Regendered, copyright-free texts can be found in the [regendered_ebooks](https://github.com/ecmonsen/regendered_ebooks) repo.

