import re
from enum import Enum

# TODO: refactor this to be more readable


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


class Literals(Enum):
    CHAR = 0
    STRING = 1
    NUMBER = 2
    TRUE = 3
    FALSE = 4
    NULL = 5

    def __str__(self):
        return self.name


def is_in_regex_match(position, regex_info):
    return regex_info.start <= position <= regex_info.end


def match_reserved_words(words, source):
    res = []
    for word in words:
        for m in word.regex.finditer(source):
            ri = RegexInfo(m.group(), word.name, word.state, word.suffix,
                           m.start(), m.end())
            res.append(ri)
    return sorted(res, key=lambda x: (x.start, -x.end, -len(x.pattern)))


class Lexer:
    def __init__(self, source):
        self.source = source
        self.current_line = 0
        self.current_position = 0
        self.global_position = 0
        self.compile_reserved_words()

    punctuation_pattern = r'(?:(?:\.\.\.)|[!?‽…:]|(?:(?!\d)\.(?!\d)))'
    any_allowed_char_pattern = r'(?:.|[,\s])'
    string_notation = ('"', '”', '“')
    types = [
        ReservedWord(r'\b(?:(?:a )|(?:the ))?character\b', 'CHAR_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?number\b', 'NUMBER_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?letter\b', 'CHAR_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:(?:a )|(?:the ))?'
                     r'(?:(?:(?:sentence)|(?:phrase)|(?:quote)|(?:word)|(?:name)))'
                     r'|(?:(?:the )?(?:(?:characters)|(?:letters))) )?\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?phrase\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?quote\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?word\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:a )|(?:the ))?name\b', 'STRING_TYPE',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\b(?:the )?characters\b', 'STRING_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:the )?letters\b', 'STRING_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:the )?logic\b', 'BOOLEAN_TYPE', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\b(?:(?:an )|(?:the ))?argument\b', 'BOOLEAN_TYPE',
                     Block.NONE, Suffix.PREFIX)
    ]
    literals = [
        ReservedWord(r"(?:(?:(?:a )|(?:the ))?(?:(?:letter)|(?:character)) )?"
                     r"['‘’].?['‘’]", Literals.CHAR, Block.NONE, Suffix.NONE),
        ReservedWord(r'(?:(?:(?:a )|(?:the ))?'
                     r'(?:'
                     r'(?:sentence)|(?:phrase)|(?:quote)|(?:word)|(?:name)) )?'
                     r'["”“](?:.|\n)*?["”“]', Literals.STRING, Block.NONE,
                     Suffix.NONE),
        ReservedWord(r'(?:(?:the )?(?:(?:characters)|(?:letters)) )?'
                     r'["”“](?:.|\n)*?["”“]', Literals.STRING, Block.NONE,
                     Suffix.NONE),
        ReservedWord(r"(?:\b(?:(?:a )|(?:the ))?number )?"
                     r"[+-]?([0-9]*[.])?[0-9]+", Literals.NUMBER, Block.NONE,
                     Suffix.NONE),
        ReservedWord(r'\b(?:(?:(?:(?:the )?logic)'
                     r'|(?:(?:an )|(?:the ))?argument) )?'
                     r'(?:(?:correct)|(?:right)|(?:true)|(?:yes))\b',
                     Literals.TRUE, Block.NONE, Suffix.NONE),
        ReservedWord(r'\b(?:(?:(?:(?:the )?logic)'
                     r'|(?:(?:an )|(?:the ))?argument) )?'
                     r'(?:(?:incorrect)|(?:false)|(?:wrong)|(?:no))\b',
                     Literals.FALSE, Block.NONE, Suffix.NONE),
        ReservedWord(r'\bnothing\b', Literals.NULL, Block.NONE, Suffix.NONE),

    ]
    keywords = [
        ReservedWord(r'(?:(?:(?:a )|(?:the ))?'
                     r'(?:'
                     r'(?:sentence)|(?:phrase)|(?:quote)|(?:word)|(?:name)) )?'
                     r'["”“](?:.|\n)*?["”“]', Literals.STRING, Block.NONE,
                     Suffix.NONE),
        ReservedWord(r'(?:(?:the )?(?:(?:characters)|(?:letters)) )?'
                     r'["”“](?:.|\n)*?["”“]', Literals.STRING, Block.NONE,
                     Suffix.NONE),

        ReservedWord(r'\((?:.|\n)*?\)', "COMMENT", Block.NONE, Suffix.NONE),
        ReservedWord(r"(P\.)+S\..*\n?", "COMMENT", Block.NONE, Suffix.NONE),
        ReservedWord(punctuation_pattern, "PUNCTUATION", Block.NONE,
                     Suffix.NONE),
        ReservedWord(r'\bI did this as long as\b', 'DO_WHILE', Block.END,
                     Suffix.PREFIX),
        ReservedWord(r"\bit['‘’]s not the case that\b", 'NOT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were)|(?:had)|(?:has))(?:(?:n['‘’]t)|(?: not)|(?: no)) more than",
            'LESS_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\b(?:(?:had)|(?:has)) no less than\b',
                     'GREATER_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bRemember when I wrote about\b', 'IMPORT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r"\bThat['‘’]s what I would do\b", 'IF', Block.END,
                     Suffix.NONE),
        ReservedWord(r"\bThat['‘’]s what I would do\b", 'ELSE', Block.END,
                     Suffix.NONE),
        ReservedWord(r'\bDid you know that\b', 'VAR', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\bI did this while\b', 'DO_WHILE', Block.END,
                     Suffix.PREFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n['‘’]t)|(?: not)) greater than",
            'LESS_THAN_OR_EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(
            r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n['‘’]t)|(?: not)|(?: no)) less than",
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
            rf'\bthe difference between(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?(?:(?:and)|(?:from)))\b',
            'SUBTRACTION', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bYour faithful student,', 'REPORT', Block.END,
                     Suffix.PREFIX),
        ReservedWord(r'\bThere was one less\b', 'DECREMENT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\bThere was one more\b', 'INCREMENT', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r"\bThat['‘’]s what I did\b", 'END_LOOP', Block.END, Suffix.NONE),
        ReservedWord(r"\bHere['‘’]s what I did\b", 'DO_WHILE', Block.BEGIN,
                     Suffix.NONE),
        ReservedWord(r"\bThat['‘’]s all about\b", 'PARAGRAPH', Block.END,
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
        ReservedWord(r'\bConditional conclusion\b',
                     'DEFAULT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'If all else fails',
                     'DEFAULT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bToday I learned\b', 'MANE_PARAGRAPH', Block.BEGIN,
                     Suffix.PREFIX),
        ReservedWord(r'\bmultiplied with\b', 'MULTIPLICATION', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(
            rf'\bthe product of(?={any_allowed_char_pattern}+?)'
            rf'(?!{punctuation_pattern})'
            rf'(?={any_allowed_char_pattern}+?)(?:(?:and)|(?:by))\b',
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
        ReservedWord(r'\bI asked\b', 'READ', Block.NONE,
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
        ReservedWord(r"\bwere(?:(?:n['‘’]t)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bhad(?:(?:n['‘’]t)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bhas(?:(?:n['‘’]t)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bwas(?:(?:n['‘’]t)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r"\bis(?:(?:n['‘’]t)|(?: not))\b", 'NOT_EQUAL', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(r'\bOtherwise\b', 'ELSE', Block.END, Suffix.NONE),
        ReservedWord(r'\bFor every\b', 'FOR', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\bbecomes?\b', 'VARIABLE_VALUE_ASSIGNMENT', Block.NONE,
                     Suffix.INFIX),
        ReservedWord(rf'\bsubtract(?={any_allowed_char_pattern}+?)'
                     rf'(?!{punctuation_pattern})'
                     rf'(?={any_allowed_char_pattern}+?(?:(?:from)|(?:and)))\b',
                     'SUBTRACTION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\bmultiply\b', 'MULTIPLICATION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\bwithout\b', 'SUBTRACTION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\balways\b', 'CONSTANT_INITIALIZATION', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(rf'\bdivide(?={any_allowed_char_pattern}+?)'
                     rf'(?!{punctuation_pattern})'
                     rf'(?={any_allowed_char_pattern}+?(?:(?:and)|(?:by)))\b',
                     'DIVISION', Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(rf'\beither(?={any_allowed_char_pattern}+?)'
                     rf'(?!{punctuation_pattern})'
                     rf'(?={any_allowed_char_pattern}+?or)\b', 'EXCLUSIVE_OR',
                     Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(r'\blikes?\b', 'VAR', Block.END_PARTNER,
                     Suffix.INFIX),
        ReservedWord(r'\bfrom\b', 'ITER', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\busing\b', 'LISTING_PARAGRAPH_PARAMETERS', Block.NONE,
                     Suffix.PREFIX),
        ReservedWord(r'\btimes\b', 'MULTIPLICATION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bWhile\b', 'WHILE', Block.BEGIN, Suffix.PREFIX),
        ReservedWord(r'\bminus\b', 'SUBTRACTION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bplus\b', 'ADDITION', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bWhen\b', 'IF', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bthen\b', 'IF', Block.END_PARTNER,
                     Suffix.POSTFIX),
        ReservedWord(r'\bDear\b', 'REPORT', Block.BEGIN, Suffix.PREFIX),
        ReservedWord(r'\bwith\b', 'RETURNED_VARIABLE_TYPE_DEFINITION',
                     Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bwere\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\badd(?=.+?)(?![.,!?‽…:])(?=.+?and)\b', 'ADDITION',
                     Block.BEGIN_PARTNER,
                     Suffix.PREFIX),
        ReservedWord(rf'\badd(?={any_allowed_char_pattern}+?)'
                     rf'(?!{punctuation_pattern})'
                     rf'(?={any_allowed_char_pattern}+?to)\b',
                     'INCREMENT',
                     Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\band\b', 'ADDITION', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\band\b', 'DIVISION', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\band\b', 'SUBTRACTION', Block.END_PARTNER,
                     Suffix.INFIX),
        ReservedWord(r'\band\b', 'MULTIPLICATION', Block.END_PARTNER,
                     Suffix.INFIX),
        ReservedWord(r'\band\b', 'AND', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bnot\b', 'NOT', Block.NONE, Suffix.PREFIX),
        ReservedWord(r'\bhad\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bhas\b', 'VAR', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bhas\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bwas\b', 'VAR', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bwas\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bIf\b', 'IF', Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(r'\bto\b', 'ITER', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bor\b', 'OR', Block.NONE, Suffix.INFIX),
        ReservedWord(r'\bis\b', 'VAR', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bis\b', 'EQUAL', Block.NONE, Suffix.INFIX),
        ReservedWord(r"\bThat['‘’]s what I did\b", 'END_LOOP', Block.END, Suffix.NONE),
        ReservedWord(r'\bin\b', 'FOR', Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(r'\bby\b', 'DIVISION', Block.END_PARTNER, Suffix.NONE),
    ]

    def compile_reserved_words(self):
        for word in self.literals + self.keywords:
            word.regex = re.compile(word.regex)

    def add_keyword_to_stack(self, stack, keyword):
        if len(stack) != 0 and stack[-1].name == 'NAME':
            self.add_literals_to_stack(stack, stack.pop())
        stack.append(keyword)

    def add_literals_to_stack(self, stack, regex_info):
        if regex_info.pattern != '':
            tokens = self.handle_literals(regex_info)
            for token in tokens:
                stack.append(token)

    def lex(self):
        keywords = match_reserved_words(self.keywords, self.source)
        stack = []

        partner_name_stack = []

        # no keywords found
        if len(keywords) == 0:
            self.add_literals_to_stack(
                stack,
                RegexInfo(
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
                    RegexInfo(
                        pattern,
                        'NAME',
                        Block.NONE,
                        Suffix.NONE,
                        0,
                        keywords[0].start - 1))

        for index, keyword in enumerate(keywords):
            # if stack is empty
            if len(stack) == 0:
                if keyword.state == Block.BEGIN_PARTNER:
                    partner_name_stack.append(keyword.name)
                    self.add_keyword_to_stack(stack, keyword)
                    continue
                self.add_keyword_to_stack(stack, keyword)
                continue


            # if keyword is end_partner with no begin_partner with the same name
            # then it is probably a name
            if keyword.state == Block.END_PARTNER and partner_name_stack \
                    and partner_name_stack[-1] != keyword.name:
                continue

            # if keyword is end_partner with begin_partner with the same name
            if keyword.state == Block.END_PARTNER and partner_name_stack \
                    and partner_name_stack[-1] == keyword.name \
                    and stack[-1].pattern == keyword.pattern:
                stack.pop()
                partner_name_stack.pop()
                self.add_keyword_to_stack(stack, keyword)
                continue

            # if it crosses a previous one
            if keyword.start < stack[-1].end:
                continue

            # if it doesn't cross a previous one,
            # so there is probably a name between them
            if keyword.start - 1 > stack[-1].end:
                pattern = self.source[stack[-1].end + 1:keyword.start].strip()
                # if previous was a name, merge
                if stack[-1].name == 'NAME' and pattern != '':
                    stack[-1].pattern += ' ' + pattern
                    stack[-1].end = keyword.start - 1
                # else add a new one
                elif pattern != '':
                    self.add_literals_to_stack(
                        stack,
                        RegexInfo(
                            pattern,
                            'NAME',
                            Block.NONE,
                            Suffix.NONE,
                            stack[-1].end + 1,
                            keyword.start - 1))
            # if begin partner
            if keyword.state == Block.BEGIN_PARTNER:
                partner_name_stack.append(keyword.name)
                self.add_keyword_to_stack(stack, keyword)
                continue
            # if end partner
            elif keyword.state == Block.END_PARTNER:
                # if it is the right partner
                if partner_name_stack and partner_name_stack[-1] == keyword.name:
                    partner_name_stack.pop()
                    self.add_keyword_to_stack(stack, keyword)
                    continue
                # if it is the wrong partner,
                # we merge it with the previous name,
                # or it is a standalone name
                else:
                    if keywords[index + 1].pattern == keyword.pattern:
                        continue
                    if stack[-1].name == 'NAME':
                        stack[-1].pattern += ' ' + keyword.pattern
                        stack[-1].end = keyword.end
                    else:
                        self.add_literals_to_stack(
                            stack,
                            RegexInfo(
                                keyword.pattern,
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
                RegexInfo(
                    self.source[stack[-1].end + 1:],
                    'NAME',
                    Block.NONE,
                    Suffix.NONE,
                    stack[-1].end + 1,
                    len(self.source) - 1))
        return stack

    def handle_literals(self, name_regex_info):
        literals = match_reserved_words(self.literals, name_regex_info.pattern)
        if len(literals) == 0:
            yield name_regex_info
            return
        start_index = 0
        previous = None
        for literal in literals:
            if previous is not None and literal.start < previous.end:
                continue
            name_pattern = name_regex_info.pattern[start_index:literal.start]\
                .strip()
            if name_pattern != '':
                name_pattern = name_regex_info.pattern[start_index:]
                previous = RegexInfo(
                    name_pattern,
                    'NAME',
                    Block.NONE,
                    Suffix.NONE,
                    start_index + name_regex_info.start,
                    name_regex_info.end)
                yield previous
                break
            else:
                previous = RegexInfo(
                    literal.pattern,
                    literal.name,
                    literal.state,
                    literal.suffix,
                    literal.start + name_regex_info.start,
                    literal.end + name_regex_info.start)
                start_index = literal.end + 1
                yield previous






program_text = """Dear Princess Celestia: Hello World!

Today I learned how to say Hello World!
I said “Hello World”!
That’s all about how to say Hello World!

Your faithful student, Kyli Rouge.
"""
# l = Lexer(program_text)
# l.lex()
# for token in l.lex():
#    print(token)
