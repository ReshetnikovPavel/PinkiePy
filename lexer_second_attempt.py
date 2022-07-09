import re
from enum import Enum
from io import StringIO


class Token:
    def __init__(self, pattern, name, state, suffix, line, position):
        self.pattern = pattern
        self.name = name
        self.state = state
        self.suffix = suffix
        self.line = line
        self.position = position

    def __str__(self):
        return f'{self.pattern} {self.name} {self.line} {self.position}'


class ReservedWord:
    def __init__(self, regex, name, state, suffix):
        self.regex = regex
        self.name = name
        self.state = state
        self.suffix = suffix


class RegexInfo:
    def __init__(self, pattern, name, state, suffix, start, end):
        self.pattern = pattern
        self.name = name
        self.state = state
        self.suffix = suffix
        self.start = start
        self.end = end

    def __str__(self):
        return f'{self.pattern} {self.name} {self.start} {self.end}'


class Block(Enum):
    NONE = 0
    BEGIN = 1
    END = 2
    BEGIN_PARTNER = 3
    END_PARTNER = 4
    INFO_INSIDE = 5


class Suffix(Enum):
    NONE = 0
    PREFIX = 1
    INFIX = 2
    POSTFIX = 3


def is_in_regex_match(position, regex_info):
    return regex_info.start <= position <= regex_info.end


class Lexer:
    def __init__(self, source):
        self.source = source
        self.current_line = 0
        self.current_position = 0
        self.global_position = 0
        self.compile_reserved_words()

    punctuation = ('.', ',', '!', '?', '‽', '…', ':')
    string_notation = ('"', '”', '“')
    literals = [
        ReservedWord(r'["”“](?:.|\n)*?["”“]', "STRING", Block.NONE,
                     Suffix.NONE),
        ReservedWord(r'\((?:.|\n)*?\)', "COMMENT", Block.NONE, Suffix.NONE),
        ReservedWord(r"(P\.)+S\..*\n?", "COMMENT", Block.NONE, Suffix.NONE),
        ReservedWord(r'(?:\.\.\.)|[.!?‽…:]', "PUNCTUATION", Block.NONE, Suffix.NONE),
        ReservedWord(r"['‘’].?['‘’]", "CHAR", Block.NONE, Suffix.NONE),
        ReservedWord(r"[+-]?([0-9]*[.])?[0-9]+", "NUMBER", Block.NONE,
                     Suffix.NONE),
        # ReservedWord(r"(P.)+S.+\n?", "COMMENT_INLINE", Block.NONE, Suffix.NONE),
        # ReservedWord(r"\(.*\)", "COMMENT_BLOCK", Block.NONE, Suffix.NONE),
        ReservedWord(r'\bcorrect\b', 'TRUE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\bright\b', 'TRUE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\btrue\b', 'TRUE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\byes\b', 'TRUE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\bincorrect\b', 'FALSE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\bfalse', 'FALSE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\bwrong\b', 'FALSE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\bno\b', 'FALSE', Block.NONE, Suffix.NONE),
        ReservedWord(r'\bnothing\b', 'NULL', Block.NONE, Suffix.NONE),
    ]
    keywords = [
        ReservedWord(r'\bI did this as long as\b', 'DO_WHILE', Block.END,
                     Suffix.PREFIX),
        ReservedWord(r"\bit's not the case that\b", 'NOT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(
            r'\b(?:(?:is)|(?:was)|(?:were)|(?:had)|(?:has)) no more than',
            'LESS_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:had)|(?:has)) no less than\b',
                     'GREATER_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bRemember when I wrote about\b', 'IMPORT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r"\bThat's what I would do\b", 'IF', Block.END,
                     Suffix.NONE),
        ReservedWord(r"\bThat's what I would do\b", 'ELSE', Block.END,
                     Suffix.NONE),
        ReservedWord(r'\bDid you know that\b', 'VAR', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bI did this while\b', 'DO_WHILE', Block.END,
                     Suffix.PREFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n't)|(?: not)) greater than",
            'LESS_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n't)|(?: not)) less than",
            'GREATER_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:is)|(?:was)|(?:were)) greater than\b',
                     'GREATER_THAN', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:is)|(?:was)|(?:were)) more than\b',
                     'GREATER_THAN', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:is)|(?:was)|(?:were)) less than\b', 'LESS_THAN',
                     Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:had)|(?:has)) more than\b', 'GREATER_THAN',
                     Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:had)|(?:has)) less than\b', 'LESS_THAN',
                     Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bthe difference between(?=.+?)(?![.,!?‽…:])(?=.+?(?:(?:and)|(?:from)))\b',
            'SUBTRACTION', Block.NONE,
            Suffix.PREFIX),
        ReservedWord(r'\bYour faithful student,', 'REPORT', Block.END,
                     Suffix.PREFIX),
        ReservedWord(r'\bThere was one less\b', 'DECREMENT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bThere was one more\b', 'INCREMENT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r"\bThat's what I did\b", 'WHILE', Block.END, Suffix.NONE),
        ReservedWord(r"\bHere's what I did\b", 'DO_WHILE', Block.BEGIN,
                     Suffix.NONE),
        ReservedWord(r'\bThat’s all about\b', 'PARAGRAPH', Block.END,
                     Suffix.PREFIX),
        ReservedWord(r'\bIn regards to\b', 'SWITCH', Block.BEGIN,
                     Suffix.PREFIX),
        ReservedWord(r'\bgot one less\b', 'DECREMENT', Block.NONE,
                     Suffix.POSTFIX),
        ReservedWord(r'\bgot one more\b', 'INCREMENT', Block.NONE,
                     Suffix.POSTFIX),
        ReservedWord(r'\bThen you get\b', 'RETURN', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bAs long as\b', 'WHILE', Block.BEGIN, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:nd)|(?:rd)|(?:st)|(?:th))? hoof\b', 'CASE',
                     Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bConditional conclusion\b', 'DEFAULT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bToday I learned\b', 'MANE_PARAGRAPH', Block.BEGIN,
                     Suffix.PREFIX),
        ReservedWord(r'\bmultiplied with\b', 'MULTIPLICATION', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(
            r'\bthe product of(?=.+?)(?![.,!?‽…:])(?=.+?)(?:(?:and)|(?:by))\b',
            'MULTIPLICATION',
            Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bI remembered\b', 'RUN', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bdivided by\b', 'DIVISION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bnow likes?\b', 'VARIABLE_VALUE_ASSIGNMENT', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\bI learned\b', 'PARAGRAPH', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\badded to\b', 'ADDITION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bOr else\b', 'ELSE', Block.BEGIN, Suffix.NONE),
        ReservedWord(r'\bI wrote\b', 'PRINT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bI asked\b', 'PROMPT_USER_FOR_IMPORT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bI heard\b', 'READLINE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bI would\b', 'RUN', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bare now\b', 'VARIABLE_VALUE_ASSIGNMENT', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\bOn the\b', 'CASE', Block.BEGIN_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bto get\b', 'RETURNED_VARIABLE_TYPE_DEFINITION',
                     Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bI said\b', 'PRINT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bI sang\b', 'PRINT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bI read\b', 'READLINE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bis now\b', 'VARIABLE_VALUE_ASSIGNMENT', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?sentences\b',
                     'STRING_ARRAY_TYPE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?numbers\b', 'NUMBER_ARRAY_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?phrases\b',
                     'STRING_ARRAY_TYPE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?phrases\b',
                     'STRING_ARRAY_TYPE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:an )|(?:the ))?argument\b', 'BOOLEAN_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?character\b', 'CHAR_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?quotes\b',
                     'STRING_ARRAY_TYPE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?words\b',
                     'STRING_ARRAY_TYPE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:many )|(?:the ))?names\b',
                     'STRING_ARRAY_TYPE', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?sentence\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?number\b', 'NUMBER_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?letter\b', 'CHAR_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?phrase\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?quote\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?word\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?name\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r"\bwere(?:(?:n't)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bhad(?:(?:n't)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bhas(?:(?:n't)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bwas(?:(?:n't)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bis(?:(?:n't)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\b(?:the )?characters\b', 'STRING_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:the )?letters\b', 'STRING_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:the )?logics\b', 'BOOLEAN_ARRAY_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:the )?logic\b', 'BOOLEAN_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bOtherwise\b', 'ELSE', Block.END, Suffix.NONE),
        ReservedWord(r'\bFor every\b', 'FOR', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bbecomes?\b', 'VARIABLE_VALUE_ASSIGNMENT', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\bsubtract(?=.+?)(?![.,!?‽…:])(?=.+?from)\b',
                     'SUBTRACTION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\bmultiply\b', 'MULTIPLICATION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\bwithout\b', 'SUBTRACTION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\balways\b', 'CONSTANT_INITIALIZATION', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bdivide(?=.+?)(?![.,!?‽…:])(?=.+?)(?:(?:and)|(?:by))\b',
                     'DIVISION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\beither(?=.+?)(?![.,!?‽…:])(?=.+?or)\b', 'EXCLUSIVE_OR',
                     Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\blikes?\b', 'VARIABLE_VALUE_ASSIGNMENT', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\bfrom\b', 'ITER', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\busing\b', 'LISTING_PARAGRAPH_PARAMETERS', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\btimes\b', 'MULTIPLICATION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bWhile\b', 'WHILE', Block.BEGIN, Suffix.PREFIX),
        ReservedWord(r'\bminus\b', 'SUBTRACTION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bplus\b', 'ADDITION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bWhen\b', 'IF', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bthen\b', 'IF_POSTFIX', Block.END_PARTNER,
                     Suffix.POSTFIX),
        ReservedWord(r'\bDear\b', 'REPORT', Block.BEGIN, Suffix.PREFIX),
        ReservedWord(r'\bwith\b', 'RETURNED_VARIABLE_TYPE_DEFINITION',
                     Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bwere\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\badd(?=.+?)(?![.,!?‽…:])(?=.+?and)\b', 'ADDITION',
                     Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\badd(?=.+?)(?![.,!?‽…:])(?=.+?to)\b', 'INCREMENT',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\band\b', 'AND', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\band\b', 'ADDITION', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\band\b', 'SUBTRACTION', Block.END_PARTNER,
                     Suffix.INFIX),
        ReservedWord(r'\band\b', 'MULTIPLICATION', Block.END_PARTNER,
                     Suffix.INFIX),
        ReservedWord(r'\band\b', 'AND', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bnot\b', 'NOT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bhad\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bhas\b', 'VAR', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bhas\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bwas\b', 'VAR', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bwas\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bIf\b', 'IF', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bto\b', 'ITER', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bor\b', 'OR', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bis\b', 'VAR', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bis\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bThat’s what I did\b', 'FOR', Block.END, Suffix.NONE),
        ReservedWord(r'\bin\b', 'IN', Block.END, Suffix.NONE),
    ]

    def compile_reserved_words(self):
        for word in self.literals + self.keywords:
            word.regex = re.compile(word.regex)

    def lex(self):
        tokens = self.match_keywords()
        for t in tokens:
            print(t)
        return tokens

    def match_keywords(self):
        words = []
        for word in self.keywords + self.literals:
            for m in word.regex.finditer(self.source):
                ri = RegexInfo(m.group(), word.name, word.state, word.suffix,
                               m.start(), m.end())
                words.append(ri)
        words = sorted(words, key=lambda x: (x.start, -x.end, -len(x.pattern)))
        stack = []

        partner_flag = False
        if len(words) == 0:
            stack.append(
                RegexInfo(
                    self.source,
                    'NAME',
                    Block.NONE,
                    Suffix.NONE,
                    0,
                    len(self.source)-1))
        elif words[0].start != 0:
            pattern = self.source[0:words[0].start].strip()
            if pattern != '':
                stack.append(
                    RegexInfo(
                        pattern,
                        'NAME',
                        Block.NONE,
                        Suffix.NONE,
                        0,
                        words[0].start - 1))
        for word in words:
            if len(stack) == 0:
                if word.state == Block.BEGIN_PARTNER:
                    partner_flag = True
                    stack.append(word)
                    continue
                stack.append(word)
                continue
            if word.start < stack[-1].end:
                continue
            if word.start-1 > stack[-1].end:
                pattern = self.source[stack[-1].end+1:word.start].strip()
                if stack[-1].name == 'NAME' and pattern != '':
                    stack[-1].pattern += ' ' + pattern
                    stack[-1].end = word.start - 1
                elif pattern != '':
                    stack.append(
                        RegexInfo(
                            pattern,
                            'NAME',
                            Block.NONE,
                            Suffix.NONE,
                            stack[-1].end+1,
                            word.start-1))
            if word.state == Block.BEGIN_PARTNER:
                partner_flag = True
                stack.append(word)
                continue
            elif word.state == Block.END_PARTNER:
                if partner_flag:
                    partner_flag = False
                    stack.append(word)
                    continue
                else:
                    if stack[-1].name == 'NAME':
                        stack[-1].pattern += ' ' + word.pattern
                        stack[-1].end = word.end
                    else:
                        stack.append(
                            RegexInfo(
                                word.pattern,
                                'NAME',
                                Block.NONE,
                                Suffix.NONE,
                                word.start,
                                word.end))

            if word.start >= stack[-1].end:
                stack.append(word)
                continue
        return stack


program_text = """Dear Princess Celestia: Hello World!

Today I learned how to say Hello World!
I said “Hello World”!
That’s all about how to say Hello World!

Your faithful student, Kyli Rouge.
"""
#l = Lexer(program_text)
#l.lex()
# for token in l.lex():
#    print(token)
