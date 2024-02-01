
import copy
import re


def clean_body_text(body_text, comp_name, contains_verb, lang):
    deleted_sentences = []
    if type(body_text) is str:
        body_text = [body_text]

    # Remove special characters
    pattern = re.compile(r"\(\*\)")
    body_text = [pattern.sub("", sentence) for sentence in body_text]
    # Remove CET/CEST
    pattern = re.compile(r"CET\s?/\s?CEST", re.IGNORECASE)
    body_text = [pattern.sub("", sentence) for sentence in body_text]
    # Remove Date
    pattern1 = r'^(.{0,30}(\,|\-|\.)\s*(den)?\s*\d{1,2}\.?\s*' + \
        r'(?:j[a]n|feb|m[ä]r|apr|ma[i]|juni|juli|aug|sep|o[k]t|nov|de[z])' + \
        r'\w*(?:\s*\d{4}|\d{2})\.*)'
    pattern2 = r'^(.{0,30}(\,|\-|\.)\s*(den)?\s*\d{1,2}\s*' + \
        r'\.\s*\d{1,2}\s*\.\s*(\d{4}|\d{2})\W+)'
    pattern3 = r'^(.{0,30}\(.*/\s*\d{1,2}\s*\.\s*\d{1,2}\s*' + \
        r'\.\s*(\d{4}|\d{2})\s*(/\s*\d{1,2}\s*\:\s*\d{1,2})?\s*\))'
    pattern = re.compile(
        "("+pattern1+"|"+pattern2+"|"+pattern3+")",
        re.IGNORECASE)
    body_text = [pattern.sub("", sentence) for sentence in body_text]
    pattern = re.compile(r'^(\W{1,5})', re.IGNORECASE)
    body_text = [pattern.sub("", sentence) for sentence in body_text]

    pattern = re.compile("(\n|\r){2,}", re.IGNORECASE)
    body_text = [pattern.sub("", sentence) for sentence in body_text]

    # Delete part of sentences starting with
    # "Diese Mitteilung ist kein Prospekt"
    if lang == "de":
        pattern = "diese mitteilung ist kein prospekt"
    else:
        pattern = "this publication is not a prospectus"
    for sent_idx, sentence in enumerate(body_text):
        if pattern in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "DIESE MITTEILUNG" (case sensitive)
    if lang == "de":
        pattern = "DIESE MITTEILUNG"
    else:
        pattern = "THIS RELEASE"
    for sent_idx, sentence in enumerate(body_text):
        if pattern in sentence:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete all sentences including and following
    # "Ende der (Ad-Hoc)-Mitteilung".
    if lang == "de":
        pattern = re.compile(
            r"ende der (ad(-)?hoc)?[- ]?(mitteilung|meldung)",
            re.IGNORECASE)
    else:
        pattern = re.compile(
            r"end of (the)? (ad(-)?hoc)?[- ]?(notification|note)",
            re.IGNORECASE)
    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.search(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete all sentences including and following sentences
    # which tell about the purpose of the company
    pattern = re.compile(
        r' AG| Aktiengesellschaft| REIT-AG| AG & CO. KGAA| AG I.L|  AG I. I.',
        re.IGNORECASE)
    comp_name = pattern.split(comp_name)[0]

    if lang == "de":
        pattern = re.compile("^( )?Über (die )?"+comp_name, re.IGNORECASE)
    else:
        pattern = re.compile("^( )?About (the )?"+comp_name, re.IGNORECASE)
    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.search(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)
    if lang == "de":
        pattern = re.compile(
            r"Die (börsennotierte )?" + comp_name +
            r"(( AG)|( Aktiengesellschaft)|( REIT-AG)|( AG & CO. KGAA)|" +
            r"( AG I.L)|(  AG I. I.))? ist ein",
            re.IGNORECASE)
    else:
        pattern = re.compile(
            r"(The )?(stock market listed )?(company )?" + comp_name +
            r"(( AG)|( Aktiengesellschaft)|( REIT-AG)|( AG & CO. KGAA)|" +
            r"( AG I.L)|(  AG I. I.))? is a",
            re.IGNORECASE)
    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.search(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete all sentences including and following sentences
    # which include "Für weitere Informationen"
    if lang == "de":
        pattern = re.compile(
            r"^( )?(Für )?Weitere Informationen",
            re.IGNORECASE)
    else:
        pattern = re.compile(
            r"^( )?(For )?Further information",
            re.IGNORECASE)
    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.search(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete all sentences including and following sentences
    # which include "Das Unternehmen in Kürze" at the beginning of a sentence
    pattern = re.compile(
        r"^Das Unternehmen in Kürze",
        re.IGNORECASE)
    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.match(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete all sentences including and following
    # "Zukunftsgerichtete Aussagen" at the beginning of a sentence
    if lang == "de":
        pattern = re.compile(
            r"(^Zukunftsgerichtete Aussagen|^Risikohinweis(e)?" +
            r"zu den Zukunftsaussagen)",
            re.IGNORECASE)
    else:
        pattern = re.compile(
            r"(^Zukunftsgerichtete Aussagen|" +
            r"^Note about risk for future predictions)",
            re.IGNORECASE)

    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.match(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete all sentences including and following
    # "Ursprüngliche Mitteilung" or "Disclaimer" or
    # "Wichtiger Hinweis" if it occurs in the lower part of the news
    if lang == "de":
        pattern = ["diese mitteilung",
                   "dieses dokument",
                   "diese veröffentlichung"]
    else:
        pattern = ["this release",
                   "this document",
                   "this publication"]
    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if (
                (pattern[0] in sentence.lower() or
                 pattern[1] in sentence.lower() or
                 pattern[2] in sentence.lower()) and
                sent_idx / len(body_text) > 0.5
            ):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete all sentences including and following
    # "Ursprüngliche Mitteilung" or "Disclaimer" or "Wichtiger Hinweis"
    if lang == "de":
        pattern = ["ursprüngliche mitteilung",
                   "disclaimer",
                   "wichtiger hinweis"]
    else:
        pattern = ["original announcement",
                   "disclaimer",
                   "important notice",
                   "important note"]

    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if (
                    pattern[0] in sentence.lower() or
                    pattern[1] in sentence.lower() or
                    pattern[2] in sentence.lower()
            ):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Match all sentences with
    # "Informationen und Erläuterungen des Emittenten"
    # at the beginning of a sentence
    if lang == "de":
        pattern = re.compile(
            r"^Informationen und Erläuterungen des Emittenten",
            re.IGNORECASE)
    else:
        pattern = re.compile(
            r"^Information and Explaination of the Issuer",
            re.IGNORECASE)

    delete_flag = False
    for sent_idx, sentence in enumerate(body_text):
        if delete_flag:
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)
        else:
            if pattern.match(sentence):
                delete_flag = True
                body_text[sent_idx] = ""
                deleted_sentences.append(sentence)

    # Delete sentences which just state formalities
    # of the news ("§ 15b WpHG or "Artikel 17")
    pattern = re.compile(
        r"(§( )?15( )?(abs\.?\s?\d{1,3})?\s?WpHG)|" +
        r"(Artikel 17)|(Article 17)|(Art 17)",
        re.IGNORECASE)
    for sent_idx, sentence in enumerate(body_text):
        if pattern.search(sentence):
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "DGAP"
    pattern = "dgap"
    for sent_idx, sentence in enumerate(body_text):
        if pattern in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Bei weiteren Rückfragen"
    if lang == "de":
        pattern = "bei weiteren rückfragen"
    else:
        pattern = "for further information"

    for sent_idx, sentence in enumerate(body_text):
        if pattern in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Börsen: Regulierter Markt"
    if lang == "de":
        pattern = "börsen: regulierter markt"
    else:
        pattern = "stock exchanges: regulated market"

    for sent_idx, sentence in enumerate(body_text):
        if pattern in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include
    # "Für den Inhalt der Mitteilung ist der Emittent verantwortlich"
    if lang == "de":
        pattern = "für den inhalt der mitteilung " + \
            "ist der emittent verantwortlich"
    else:
        pattern = "the issuer is solely responsible " + \
            "for the content of this announcement."
    for sent_idx, sentence in enumerate(body_text):
        if pattern in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Bericht" & "Download"
    if lang == "de":
        pattern = ["bericht", "download"]
    else:
        pattern = ["report", "download"]
    for sent_idx, sentence in enumerate(body_text):
        if pattern[0] in sentence.lower() and pattern[1] in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Inhalt der Mitteilung" & "Emittent"
    if lang == "de":
        pattern = ["inhalt der mitteilung", "emittent"]
    else:
        pattern = ["the content of this announcement", " issuer"]

    for sent_idx, sentence in enumerate(body_text):
        if pattern[0] in sentence.lower() and pattern[1] in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Prognose" &  "künftig"
    if lang == "de":
        pattern = ["prognose", "künftig"]
    else:
        pattern = ["projections", "future"]
    for sent_idx, sentence in enumerate(body_text):
        if pattern[0] in sentence.lower() and pattern[1] in sentence.lower():
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Nicht" &  "Veröffentlichung" & "Länder"
    if lang == "de":
        pattern = ["nicht", "veröffentlichung", "länder"]
    else:
        pattern = ["not", "release",  "jurisdiction"]
    for sent_idx, sentence in enumerate(body_text):
        if (
                pattern[0] in sentence.lower() and
                pattern[1] in sentence.lower() and
                pattern[2] in sentence.lower()
        ):
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include
    #  "Nicht" &  "Veröffentlichung" & "Weitergabe"
    if lang == "de":
        pattern = ["nicht", "veröffentlichung", "weitergabe"]
    else:
        pattern = ["not", "release", "transmission"]
    for sent_idx, sentence in enumerate(body_text):
        if (
                pattern[0] in sentence.lower() and
                pattern[1] in sentence.lower() and
                pattern[2] in sentence.lower()
        ):
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include
    # "Länder" &  "Veröffentlichung" & "Weitergabe"
    if lang == "de":
        pattern = ["länder", "veröffentlichung", "weitergabe"]
    else:
        pattern = ["jurisdiction", "release", "transmission"]
    for sent_idx, sentence in enumerate(body_text):
        if (
                pattern[0] in sentence.lower() and
                pattern[1] in sentence.lower() and
                pattern[2] in sentence.lower()
        ):
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete sentences which include "Angebot" &  "Aufforderung" &  "Verkauf"
    if lang == "de":
        pattern = ["angebot", "aufforderung", "verkauf"]
    else:
        pattern = ["offer", "solicitation", "sell"]
    for sent_idx, sentence in enumerate(body_text):
        if (
                pattern[0] in sentence.lower() and
                pattern[1] in sentence.lower() and
                pattern[2] in sentence.lower()
        ):
            body_text[sent_idx] = ""
            deleted_sentences.append(sentence)

    # Delete all sentences without a verb
    for sent_idx, sentContVerb in enumerate(contains_verb):
        if not sentContVerb:
            deleted_sentences.append(body_text[sent_idx])
            body_text[sent_idx] = ""

    body_text = [sentence for sentence in body_text if sentence.strip() != ""]
    deleted_sentences = \
        [sentence for sentence in deleted_sentences if sentence.strip() != ""]
    return body_text, deleted_sentences


def extract_brackets(text, lang):
    # Function the exctract the text between the outermost
    # brackets in a string, if they exist. The text in brackets is
    # first sored in another list and is then replaced by a
    # specified placeholder-word in the input string
    if lang == "de":
        placeholder_text = "Platzhalter"
    else:
        placeholder_text = "placeholder"
    text_in_brackets = []
    text_in_brackets_act = ""
    open_counter = 0
    close_counter = 0
    for char in text:
        if open_counter > close_counter:
            text_in_brackets_act = "".join((text_in_brackets_act, char))
        if char == "(" or char == "{" or char == "[":
            open_counter += 1
        elif char == ")" or char == "}" or char == "]":
            close_counter += 1
        if close_counter > 0 and open_counter == close_counter:
            text_in_brackets.append(text_in_brackets_act[:-1])
            text_in_brackets_act = ""
            open_counter = 0
            close_counter = 0
        elif close_counter > open_counter:
            close_counter = open_counter
    if text_in_brackets:
        for idx, textInBracket in enumerate(text_in_brackets):
            text = text.replace(
                "(" + textInBracket + ")",
                "(" + placeholder_text + str(idx) + ")",
                1)
            text = text.replace(
                "{" + textInBracket + "}",
                "{" + placeholder_text + str(idx) + "}",
                1)
            text = text.replace(
                "[" + textInBracket + "]",
                "[" + placeholder_text + str(idx) + "]",
                1)
    return [text, text_in_brackets]


def sentence_split(document_dict, nlpDe, nlpEn):
    # Function for splitting sentences of a text. Pleaase note:
    # To run it on a GPU, please run first "spacy.require_gpu()"
    # before calling this function
    document_dict_new = copy.deepcopy(document_dict)

    # Identify language if missing
    if document_dict_new["language"] == "":
        nlpEn.enable_pipe("language_detector")
        nlpEn.disable_pipe("transformer")
        nlpEn.disable_pipe("parser")
        nlpEn.disable_pipe("tagger")
        nlpEn.disable_pipe("attribute_ruler")
        th = min(5, len(document_dict_new["body_text"]))
        lang = \
            nlpEn(
                " ".join(
                    document_dict_new["body_text"][:th]
                    )
                )
        if lang._.language == "en":
            document_dict_new["language"] = "en"
        elif lang._.language == "de":
            document_dict_new["language"] = "de"
        nlpEn.enable_pipe("transformer")
        nlpEn.enable_pipe("parser")
        nlpEn.enable_pipe("tagger")
        nlpEn.enable_pipe("attribute_ruler")
        nlpEn.disable_pipe("language_detector")

    # Prepare Text (Replace company names and text in
    # brackets before sentence segmentation. Replace ; with ,)
    if document_dict_new["language"] == "de":
        comp_placeholder = "Augenweide"
        bracket_placeholder = "Platzhalter"
    else:
        comp_placeholder = "eyecandy"
        bracket_placeholder = "placeholder"
    src_str = re.compile(document_dict_new["comp_name"], re.IGNORECASE)
    bracket_text_document = []
    for para_idx in range(len(document_dict_new["body_text"])):
        # Avoid sentence split within company names
        # (Replace comp name with some arbitrary word that
        # is unlikely to occur elsewhere in the text)
        if document_dict_new["comp_name"] != "":
            document_dict_new["body_text"][para_idx] = \
                src_str.sub(
                    comp_placeholder,
                    document_dict_new["body_text"][para_idx]
                    )
        # Avoid sentence split after ";"
        document_dict_new["body_text"][para_idx] = \
            document_dict_new["body_text"][para_idx].replace(";", ",")
        # Avoid sentence split within brackets
        [document_dict_new["body_text"][para_idx], bracketText] = \
            extract_brackets(
                document_dict_new["body_text"][para_idx],
                lang=document_dict_new["language"])
        bracket_text_document.append(bracketText)

    # Split paragraph by paragraph
    # A paragraph is a string which contains one or more sentences.
    # The goal is to split the sentences in all paragraphs
    # and write them all in one list. Additionally, the information whether
    # a verb is in a sentence or not is additionally stored.
    if document_dict_new["language"] == "Englisch":
        document_dict_new["language"] = "en"
    if "en" in document_dict_new["language"]:
        parsed_document = nlpEn.pipe(document_dict_new["body_text"])
    elif "de" in document_dict_new["language"]:
        parsed_document = nlpDe.pipe(document_dict_new["body_text"])
    else:
        document_dict_new["contains_verb"] = []
        return document_dict_new
    # Store all sentences of one document after splitting
    sentences_document = []
    # Store all verb info of all sentences of one document after splitting
    contains_verb_document = []
    for parIdx, paragraph in enumerate(parsed_document):
        # Store all sentences of one paragraph after splitting
        sentences_paragraph = []
        # Contains for a specific paragraph of a
        # document the texts in brackets (simple list)
        bracket_text_paragraph = bracket_text_document[parIdx]
        # Counts how many brackets were reimplemented
        # (necessary since we might sentences with no brackets and
        # sentences with 2 or more brackets within one paragraph)
        bracket_replace_counter = 0
        for sent in paragraph.sents:
            sent = str(sent)
            # Reinput bracket text
            while bracket_replace_counter < len(bracket_text_paragraph):
                if bracket_placeholder + str(bracket_replace_counter) in sent:
                    sent = sent.replace(
                        bracket_placeholder + str(bracket_replace_counter),
                        bracket_text_paragraph[bracket_replace_counter])
                    bracket_replace_counter += 1
                else:
                    break
            sent = sent.replace(
                comp_placeholder,
                document_dict_new["comp_name"]
                )
            sentences_paragraph.append(sent)
        sentences_document = sentences_document + sentences_paragraph
        contains_verb_document = contains_verb_document + \
            [any([w.pos_ == "AUX" or w.pos_ == "VERB" for w in s])
             for s in paragraph.sents]
    document_dict_new["body_text"] = sentences_document
    document_dict_new["contains_verb"] = contains_verb_document
    return document_dict_new
