class KeywordMaker:
    def __init__(self, token_name, words):
        self.token_name = token_name
        self.words = words

    def __str__(self):
        return f'{self.token_name} {self.words}'

    def make_tuples(self):
        print(str.split('words', ' '))

    def make_regex(self):
        res = r''
        for word_pos in self.words:
            curr_res = r''
            if type(word_pos) == tuple:
                for word in word_pos:
                    curr_res += rf'(?:{word})|'
            else:
                curr_res += rf'(?:{word_pos})|'
            if len(curr_res) != 0:
                curr_res = curr_res[:-1]
            res += rf'(?:{curr_res})\s+'
        if len(res) != 0:
            res = res[:-3]
        return res

    def words_used(self):
        for word_pos in self.words:
            if type(word_pos) == tuple:
                for word in word_pos:
                    yield word
            else:
                yield word_pos


if __name__ == '__main__':
    keywords_set = set()
    keywords = {
        r'["”“](?:.|\n)*?["”“]': "STRING",
        r"['‘’].?['‘’]": "CHAR",
        r"[.,!?‽…:]": "PUNCTUATION",
        r"\d+": "NUMBER"
    }
    keyword_makers = [
        KeywordMaker('REPORT_DECLARATION',
                     ("Dear",)),
        KeywordMaker(("END_IF", "END_ELSE", 'END_SWITCH'),
                     ("That's", "what", "I", "would", "do")),
        KeywordMaker('DEFAULT',
                     ("If", "all", "else", "fails")),
        KeywordMaker('ELSE',
                     ("Or", "else")),
        KeywordMaker('ELSE',
                     ("Otherwise",)),
        KeywordMaker('CASE_PREFIX',
                     ("On", "the")),
        KeywordMaker('CASE_POSTFIX',
                     ("hoof",)),
        KeywordMaker('CASE_POSTFIX',
                     (("nd", "rd", "st", "th"), "hoof")),
        KeywordMaker('IF_PREFIX',
                     (("If", "When"),)),
        KeywordMaker('IF_POSTFIX',
                     ("then",)),
        KeywordMaker('SWITCH_PREFIX',
                     ("In", "regards", "to")),
        KeywordMaker('MANE_PARAGRAPH_DECLARATION',
                     ("Today", "I", "learned")),
        KeywordMaker('PARAGRAPH_DECLARATION',
                     ("I", "learned")),
        KeywordMaker('VARIABLE_DEFINITION',
                     ("Did", "you", "know", "that")),
        KeywordMaker('RETURNED_VARIABLE_TYPE_DEFINITION',
                     ("to", "get")),
        KeywordMaker('RETURNED_VARIABLE_TYPE_DEFINIeTION',
                     ("with",)),
    ]

    keyword_makers = sorted(
        keyword_makers,
        key=lambda x: len(x.words),
        reverse=True)

    for keyword_maker in keyword_makers:
        print(keyword_maker.make_regex())
        for word in keyword_maker.words_used():
            keywords_set.add(word)

    print(repr(keywords_set))
