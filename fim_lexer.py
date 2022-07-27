import re
from enum import Enum


# TODO: refactor this to be more readable


class ReservedWord:
    def __init__(self, regex, name, block, suffix):
        self.regex = regex
        self.name = name
        self.block = block
        self.suffix = suffix


class Token:
    def __init__(self, value, name, state, suffix, start, end):
        self.value = value
        self.name = name
        self.block = state
        self.suffix = suffix
        self.start = start
        self.end = end

    def __str__(self):
        return f'{self.value} {self.name} {self.start} {self.end}'

    @staticmethod
    def default_token():
        return Token(None, None, None, None, None, None)


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


class Literals(Enum):
    CHAR = 0
    STRING = 1
    NUMBER = 2
    TRUE = 3
    FALSE = 4
    NULL = 5

    def __str__(self):
        return self.name


class Keywords(Enum):
    COMMENT = 0
    PUNCTUATION = 1
    DO_WHILE = 2
    NOT = 3
    LESS_THAN_OR_EQUAL = 4
    GREATER_THAN_OR_EQUAL = 5
    IMPORT = 6
    IF = 7
    VAR = 8
    GREATER_THAN = 9
    LESS_THAN = 10
    SUBTRACTION = 11
    REPORT = 12
    DECREMENT = 13
    INCREMENT = 14
    END_LOOP = 15
    PARAGRAPH = 16
    SWITCH = 17
    RETURN = 18
    WHILE = 19
    CASE = 20
    DEFAULT = 21
    MANE_PARAGRAPH = 22
    MULTIPLICATION = 23
    RUN = 24
    DIVISION = 25
    ASSIGN = 26
    ADDITION = 27
    ELSE = 28
    PRINT = 29
    READ = 30
    READLINE = 31
    RETURNED_VARIABLE_TYPE = 32
    NOT_EQUAL = 33
    FOR = 34
    CONST = 35
    XOR = 36
    ITER = 37
    LISTING_PARAGRAPH_PARAMETERS = 38
    EQUAL = 39
    AND = 40
    OR = 41

    def __str__(self):
        return self.name


def match_reserved_words(words, source):
    res = []
    for word in words:
        for m in word.regex.finditer(source):
            ri = Token(m.group(), word.name, word.block, word.suffix,
                       m.start(), m.end())
            res.append(ri)
    return sorted(res, key=lambda x: (x.start, -x.end, -len(x.value)))


class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = None
        self.compile_reserved_words()

    punctuation_pattern = r'(?:(?:\.\.\.)|[!?‽…:,]|(?:(?!\d)\.(?!\d)))'
    any_allowed_char_pattern = r'(?:.|[,\s])'
    literals = [
        ReservedWord(
            r"(?:(?:(?:a )|(?:the ))?(?:(?:letter)|(?:character)) )?"
            r"['‘’].?['‘’]",
            Literals.CHAR, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'(?:(?:(?:a )|(?:the ))?'
            r'(?:(?:sentence)|(?:phrase)|(?:quote)|(?:word)|(?:name)) )?'
            r'["”“](?:.|\n)*?["”“]',
            Literals.STRING, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'(?:(?:the )?(?:(?:characters)|(?:letters)) )?'
            r'["”“](?:.|\n)*?["”“]',
            Literals.STRING, Block.NONE, Suffix.NONE),
        ReservedWord(
            r"(?:\b(?:(?:a )|(?:the ))?number )?"
            r"[+-]?([0-9]*[.])?[0-9]+",
            Literals.NUMBER, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\b(?:(?:(?:(?:the )?logic)|(?:(?:an )|(?:the ))?argument) )?'
            r'(?:(?:correct)|(?:right)|(?:true)|(?:yes))\b',
            Literals.TRUE, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\b(?:(?:(?:(?:the )?logic)|(?:(?:an )|(?:the ))?argument) )?'
            r'(?:(?:incorrect)|(?:false)|(?:wrong)|(?:no))\b',
            Literals.FALSE, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\bnothing\b',
            Literals.NULL, Block.NONE, Suffix.NONE),

    ]
    keywords = [
        ReservedWord(
            r'(?:(?:(?:a )|(?:the ))?'
            r'(?:(?:sentence)|(?:phrase)|(?:quote)|(?:word)|(?:name)) )?'
            r'["”“](?:.|\n)*?["”“]',
            Literals.STRING, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'(?:(?:the )?(?:(?:characters)|(?:letters)) )?'
            r'["”“](?:.|\n)*?["”“]',
            Literals.STRING, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\((?:.|\n)*?\)',
            Keywords.COMMENT, Block.NONE, Suffix.NONE),
        ReservedWord(
            r"(P\.)+S\..*\n?",
            Keywords.COMMENT, Block.NONE, Suffix.NONE),
        ReservedWord(
            punctuation_pattern,
            Keywords.PUNCTUATION, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\bI did this as long as\b',
            Keywords.DO_WHILE, Block.END, Suffix.PREFIX),
        ReservedWord(
            r"\bit['‘’]s not the case that\b",
            Keywords.NOT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were)|(?:had)|(?:has))"
            r"(?:(?:n['‘’]t)|(?: not)|(?: no)) more than",
            Keywords.LESS_THAN_OR_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\b(?:(?:had)|(?:has)) no less than\b',
            Keywords.GREATER_THAN_OR_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bRemember when I wrote about\b',
            Keywords.IMPORT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r"\bThat['‘’]s what I would do\b",
            Keywords.IF, Block.END, Suffix.NONE),
        ReservedWord(
            r'\bDid you know that\b',
            Keywords.VAR, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bI did this while\b',
            Keywords.DO_WHILE, Block.END, Suffix.PREFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n['‘’]t)|(?: not)) "
            r"greater than",
            Keywords.LESS_THAN_OR_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n['‘’]t)|(?: not)|(?: no)) "
            r"less than",
            Keywords.GREATER_THAN_OR_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\b(?:(?:is)|(?:was)|(?:were)) greater than\b',
            Keywords.GREATER_THAN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\b(?:(?:is)|(?:was)|(?:were)) more than\b',
            Keywords.GREATER_THAN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\b(?:(?:is)|(?:was)|(?:were)) less than\b',
            Keywords.LESS_THAN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\b(?:(?:had)|(?:has)) more than\b',
            Keywords.GREATER_THAN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\b(?:(?:had)|(?:has)) less than\b',
            Keywords.LESS_THAN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            rf'\bthe difference between(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?(?:(?:and)|(?:from)))\b',
            Keywords.SUBTRACTION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bYour faithful student,',
            Keywords.REPORT, Block.END, Suffix.PREFIX),
        ReservedWord(
            r'\bThere was one less\b',
            Keywords.DECREMENT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bThere was one more\b',
            Keywords.INCREMENT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r"\bThat['‘’]s what I did\b",
            Keywords.END_LOOP, Block.END, Suffix.NONE),
        ReservedWord(
            r"\bHere['‘’]s what I did\b",
            Keywords.DO_WHILE, Block.BEGIN, Suffix.NONE),
        ReservedWord(
            r"\bThat['‘’]s all about\b",
            Keywords.PARAGRAPH, Block.END, Suffix.PREFIX),
        ReservedWord(
            r'\bIn regards to\b',
            Keywords.SWITCH, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\bgot one less\b',
            Keywords.DECREMENT, Block.NONE, Suffix.POSTFIX),
        ReservedWord(
            r'\bgot one more\b',
            Keywords.INCREMENT, Block.NONE, Suffix.POSTFIX),
        ReservedWord(
            r'\bThen you get\b',
            Keywords.RETURN, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bAs long as\b',
            Keywords.WHILE, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\b(?:(?:nd)|(?:rd)|(?:st)|(?:th))? hoof\b',
            Keywords.CASE, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bConditional conclusion\b',
            Keywords.DEFAULT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bIf all else fails\b',
            Keywords.DEFAULT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bToday I learned\b',
            Keywords.MANE_PARAGRAPH, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\bmultiplied with\b',
            Keywords.MULTIPLICATION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            rf'\bthe product of(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?)(?:(?:and)|(?:by))\b',
            Keywords.MULTIPLICATION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bI remembered\b',
            Keywords.RUN, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bdivided by\b',
            Keywords.DIVISION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bnow likes?\b',
            Keywords.ASSIGN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bI learned\b',
            Keywords.PARAGRAPH, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\badded to\b',
            Keywords.ADDITION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bOr else\b',
            Keywords.ELSE, Block.BEGIN, Suffix.NONE),
        ReservedWord(
            r'\bI wrote\b',
            Keywords.PRINT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bI asked\b',
            Keywords.READ, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bI heard\b',
            Keywords.READLINE, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bI would\b',
            Keywords.RUN, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bare now\b',
            Keywords.ASSIGN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bOn the\b',
            Keywords.CASE, Block.BEGIN_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bto get\b',
            Keywords.RETURNED_VARIABLE_TYPE, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bI said\b',
            Keywords.PRINT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bI sang\b',
            Keywords.PRINT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bI read\b',
            Keywords.READLINE, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bis now\b',
            Keywords.ASSIGN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\bwere(?:(?:n['‘’]t)|(?: not))\b",
            Keywords.NOT_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\bhad(?:(?:n['‘’]t)|(?: not))\b",
            Keywords.NOT_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\bhas(?:(?:n['‘’]t)|(?: not))\b",
            Keywords.NOT_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\bwas(?:(?:n['‘’]t)|(?: not))\b",
            Keywords.NOT_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\bis(?:(?:n['‘’]t)|(?: not))\b",
            Keywords.NOT_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bOtherwise\b',
            Keywords.ELSE, Block.END, Suffix.NONE),
        ReservedWord(
            r'\bFor every\b',
            Keywords.FOR, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bbecomes?\b',
            Keywords.ASSIGN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            rf'\bsubtract(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?(?:(?:from)|(?:and)))\b',
            Keywords.SUBTRACTION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bmultiply\b',
            Keywords.MULTIPLICATION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bwithout\b',
            Keywords.SUBTRACTION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\balways\b',
            Keywords.CONST, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            rf'\bdivide(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?(?:(?:and)|(?:by)))\b',
            Keywords.DIVISION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            rf'\beither(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?or)\b',
            Keywords.XOR, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\blikes?\b',
            Keywords.VAR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bfrom\b',
            Keywords.ITER, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\busing\b',
            Keywords.LISTING_PARAGRAPH_PARAMETERS, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\btimes\b',
            Keywords.MULTIPLICATION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bWhile\b',
            Keywords.WHILE, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\bminus\b',
            Keywords.SUBTRACTION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bplus\b',
            Keywords.ADDITION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bWhen\b',
            Keywords.IF, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bthen\b',
            Keywords.IF, Block.END_PARTNER, Suffix.POSTFIX),
        ReservedWord(
            r'\bDear\b', 'REPORT', Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\bwith\b',
            Keywords.RETURNED_VARIABLE_TYPE, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bwere\b',
            Keywords.EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\badd(?=.+?)(?![.,!?‽…:])(?=.+?and)\b',
            Keywords.ADDITION, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            rf'\badd(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?to)\b',
            Keywords.INCREMENT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\band\b',
            Keywords.ADDITION, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\band\b',
            Keywords.DIVISION, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\band\b',
            Keywords.SUBTRACTION, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\band\b',
            Keywords.MULTIPLICATION, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\band\b',
            Keywords.AND, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bnot\b',
            Keywords.NOT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bhad\b',
            Keywords.EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bhas\b',
            Keywords.VAR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bhas\b',
            Keywords.EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bwas\b',
            Keywords.VAR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bwas\b',
            Keywords.EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bIf\b',
            Keywords.IF, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bto\b',
            Keywords.ITER, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bor\b',
            Keywords.OR, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bor\b',
            Keywords.XOR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bis\b',
            Keywords.VAR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bis\b',
            Keywords.EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\bThat['‘’]s what I did\b",
            Keywords.END_LOOP, Block.END, Suffix.NONE),
        ReservedWord(
            r'\bin\b',
            Keywords.FOR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bby\b',
            Keywords.DIVISION, Block.END_PARTNER, Suffix.INFIX),
    ]

    def compile_reserved_words(self):
        for word in self.literals + self.keywords:
            word.regex = re.compile(word.regex)

    def lex(self):
        keywords = match_reserved_words(self.keywords, self.source)
        stack = []

        partner_name_stack = []

        # no keywords found
        if len(keywords) == 0:
            self.add_literals_to_stack(
                stack,
                Token(
                    self.source,
                    'NAME',
                    Block.NONE,
                    Suffix.NONE,
                    0,
                    len(self.source) - 1))

        # keyword is not at the start of the source
        elif keywords[0].start != 0:
            pattern = self.source[0:keywords[0].start].strip()
            if pattern != '':
                self.add_literals_to_stack(
                    stack,
                    Token(
                        pattern,
                        'NAME',
                        Block.NONE,
                        Suffix.NONE,
                        0,
                        keywords[0].start - 1))

        for index, keyword in enumerate(keywords):
            # if stack is empty
            if len(stack) == 0:
                if keyword.block == Block.BEGIN_PARTNER:
                    partner_name_stack.append(keyword.name)
                    self.add_keyword_to_stack(stack, keyword)
                    continue
                self.add_keyword_to_stack(stack, keyword)
                continue

            # if keyword is end_partner with no begin_partner with the same name
            # then it is probably a name
            if keyword.block == Block.END_PARTNER and partner_name_stack \
                    and partner_name_stack[-1] != keyword.name:
                continue

            # if keyword is end_partner with begin_partner with the same name
            if keyword.block == Block.END_PARTNER and partner_name_stack \
                    and partner_name_stack[-1] == keyword.name \
                    and stack[-1].value == keyword.value:
                stack.pop()
                partner_name_stack.pop()
                self.add_keyword_to_stack(stack, keyword)
                continue

            # if it crosses a previous one
            if keyword.start < stack[-1].end:
                continue

            # if it doesn't cross a previous one,
            # so there is probably a name between them
            if keyword.start >= stack[-1].end:
                pattern = self.source[stack[-1].end:keyword.start].strip()
                # if previous was a name, merge
                if stack[-1].name == 'NAME' and pattern != '':
                    stack[-1].value += ' ' + pattern
                    stack[-1].end = keyword.start - 1
                # else add a new one
                elif pattern != '':
                    self.add_literals_to_stack(
                        stack,
                        Token(
                            pattern,
                            'NAME',
                            Block.NONE,
                            Suffix.NONE,
                            stack[-1].end + 1,
                            keyword.start - 1))
            # if begin partner
            if keyword.block == Block.BEGIN_PARTNER:
                partner_name_stack.append(keyword.name)
                self.add_keyword_to_stack(stack, keyword)
                continue
            # if end partner
            elif keyword.block == Block.END_PARTNER:
                # if it is the right partner
                if partner_name_stack \
                        and partner_name_stack[-1] == keyword.name:
                    partner_name_stack.pop()
                    self.add_keyword_to_stack(stack, keyword)
                    continue
                # if it is the wrong partner,
                # we merge it with the previous name,
                # or it is a standalone name
                else:
                    if keywords[index + 1].value == keyword.value:
                        continue
                    if stack[-1].name == 'NAME':
                        stack[-1].value += ' ' + keyword.value
                        stack[-1].end = keyword.end
                    else:
                        self.add_literals_to_stack(
                            stack,
                            Token(
                                keyword.value,
                                'NAME',
                                Block.NONE,
                                Suffix.NONE,
                                keyword.start,
                                keyword.end))

            # if it is a normal keyword
            if keyword.start >= stack[-1].end:
                self.add_keyword_to_stack(stack, keyword)
                continue

        if stack[-1].end != len(self.source) - 1:
            self.add_literals_to_stack(
                stack,
                Token(
                    self.source[stack[-1].end + 1:],
                    'NAME',
                    Block.NONE,
                    Suffix.NONE,
                    stack[-1].end + 1,
                    len(self.source) - 1))

        self.tokens = stack
        return stack

    def add_keyword_to_stack(self, stack, keyword):
        if len(stack) != 0 and stack[-1].name == 'NAME':
            self.add_literals_to_stack(stack, stack.pop())
        stack.append(keyword)

    def add_literals_to_stack(self, stack, regex_info):
        if regex_info.value != '':
            tokens = self.handle_literals(regex_info)
            for token in tokens:
                stack.append(token)

    def handle_literals(self, name_regex_info):
        literals = match_reserved_words(self.literals, name_regex_info.value)
        if len(literals) == 0:
            yield name_regex_info
            return
        start_index = 0
        previous = None
        for literal in literals:
            if previous is not None and literal.start < previous.end:
                continue
            name_pattern = name_regex_info.value[start_index:literal.start] \
                .strip()
            if name_pattern != '':
                name_pattern = name_regex_info.value[start_index:]
                previous = Token(
                    name_pattern,
                    'NAME',
                    Block.NONE,
                    Suffix.NONE,
                    start_index + name_regex_info.start,
                    name_regex_info.end)
                yield previous
                break
            else:
                previous = Token(
                    literal.value,
                    literal.name,
                    literal.block,
                    literal.suffix,
                    literal.start + name_regex_info.start,
                    literal.end + name_regex_info.start)
                start_index = literal.end + 1
                yield previous

    def get_next_token(self):
        if len(self.tokens) == 0:
            return Token.default_token()
        token = self.tokens.pop(0)
        while token.name == Keywords.COMMENT:
            token = self.tokens.pop(0)
        return token

    def peek(self):
        if len(self.tokens) == 0:
            return Token.default_token()
        return self.tokens[0]
