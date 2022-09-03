import re
from enum import Enum


class ReservedWord:
    def __init__(self, regex, type, block, suffix):
        self.regex = regex
        self.type = type
        self.block = block
        self.suffix = suffix


class Token:
    def __init__(self, value, type, block, suffix, start, end):
        self.value = value
        self.type = type
        self.block = block
        self.suffix = suffix
        self.start = start
        self.end = end

    def __str__(self):
        return f'{self.value} {self.type} {self.start} {self.end}'

    def __repr__(self):
        return f"Token({self.value}, {self.type}, {self.block}," \
               f" {self.suffix}, {self.start}, {self.end}) "

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
    BOOL = 7
    CHAR = 0
    STRING = 1
    NUMBER = 2
    TRUE = 3
    FALSE = 4
    NULL = 5
    ID = 6
    ARRAY = 8

    def __str__(self):
        return self.name


class Keywords(Enum):
    MODULO = 47
    FROM = 46
    ARRAY = 45
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
    LISTING_PARAGRAPH_PARAMETERS = 38
    EQUAL = 39
    AND = 40
    OR = 41
    THEN = 42
    ACCESS_FROM_OBJECT = 43
    CONCAT = 44

    def __str__(self):
        return self.name


def match_reserved_words(words, source):
    res = []
    for word in words:
        for m in word.regex.finditer(source):
            ri = Token(m.group(), word.type, word.block, word.suffix,
                       m.start(), m.end())
            res.append(ri)
    return sorted(res, key=lambda x: (x.start, -x.end, -len(x.value)))


class Lexer:
    def __init__(self, source=None):
        if source is None:
            source = ''
        self.source = source
        self.tokens = []
        self._compile_reserved_words()
        self.stack = []
        self.partner_name_stack = []

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
        # STRING is considered literal,
        # but for simplicity we treat it as keyword
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
            # works the same as . in Java or C#, for instance
            r'`s|`',
            Keywords.ACCESS_FROM_OBJECT, Block.NONE, Suffix.NONE),
        ReservedWord(r"\b\bis(?:(?:n['‘’]t)|(?: not)) equal to",
                     Keywords.NOT_EQUAL, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bis equal to\b',
            Keywords.EQUAL, Block.NONE, Suffix.INFIX),
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
            r'(?:(?:nd)|(?:rd)|(?:st)|(?:th))? hoof\b',
            Keywords.CASE, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bConditional conclusion\b',
            Keywords.DEFAULT, Block.END, Suffix.PREFIX),
        ReservedWord(
            r'\bIf all else fails\b',
            Keywords.DEFAULT, Block.END, Suffix.PREFIX),
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
            Keywords.PARAGRAPH, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\badded to\b',
            Keywords.ADDITION, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bOr else\b',
            Keywords.ELSE, Block.END, Suffix.NONE),
        ReservedWord(
            r'\bI wrote\b',
            Keywords.PRINT, Block.NONE, Suffix.PREFIX),
        ReservedWord(
            r'\bI asked\b',
            Keywords.READLINE, Block.NONE, Suffix.PREFIX),
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
            r'\bmodulo\b',
            Keywords.MODULO, Block.NONE, Suffix.INFIX),
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
            r'\bI thought\b',
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
            r'(?<=\bFor every\b\s(?=(?:.*?\bfrom\b)))',
            Keywords.FROM, Block.BEGIN_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bbecomes?\b',
            Keywords.ASSIGN, Block.NONE, Suffix.INFIX),
        ReservedWord(
            r'\bbecame\b',
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
            r'\bmany\b',
            Keywords.ARRAY, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\bfrom\b',
            Keywords.FROM, Block.END_PARTNER, Suffix.PREFIX),
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
            Keywords.IF, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\bthen\b',
            Keywords.THEN, Block.NONE, Suffix.NONE),
        ReservedWord(
            r'\bDear\b',
            Keywords.REPORT, Block.BEGIN, Suffix.PREFIX),
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
            Keywords.INCREMENT, Block.BEGIN_PARTNER, Suffix.PREFIX),
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
            Keywords.IF, Block.BEGIN, Suffix.PREFIX),
        ReservedWord(
            r'\bor\b',
            Keywords.XOR, Block.END_PARTNER, Suffix.INFIX),
        ReservedWord(
            r'\bor\b',
            Keywords.OR, Block.NONE, Suffix.INFIX),
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
        ReservedWord(
            r'\bto\b',
            Keywords.FOR, Block.END_PARTNER, Suffix.PREFIX),
        ReservedWord(
            r'\bto\b',
            Keywords.INCREMENT, Block.END_PARTNER, Suffix.PREFIX),
    ]

    def set_source(self, source):
        self.source = source

    def _compile_reserved_words(self):
        for word in self.literals + self.keywords:
            word.regex = re.compile(word.regex)

    def lex(self):
        keywords = match_reserved_words(self.keywords, self.source)
        for keyword_index, keyword in enumerate(keywords):
            if self._collides_with_previous(keyword):
                continue
            if keyword.start != 0:
                self._add_literals_before(keyword)
            if self._is_wrong_end_partner(keyword):
                if keywords[keyword_index + 1].value == keyword.value:
                    continue
                elif self.stack[-1].type == Literals.ID:
                    self._merge(self.stack[-1], keyword)
                    continue
                else:
                    keyword.type = Literals.ID
            self._add_to_stack(keyword)
        self._finish_lex()
        return self.tokens

    def _collides_with_previous(self, token):
        if token.start == 0 and len(self.stack) == 0:
            return False
        return self._get_latest_token_end() > token.start

    def _add_literals_before(self, token):
        start_offset = self._get_latest_token_end()
        between_tokens = self.source[start_offset:token.start]
        literals = match_reserved_words(self.literals, between_tokens)
        if len(literals) == 0:
            self._add_id_before(token, include_token=False)
        for literal in literals:
            literal.start += start_offset
            literal.end += start_offset
            if self._collides_with_previous(literal):
                continue
            if self._add_id_before(literal):
                break
            self._add_to_stack(literal)
        self._add_id_before(token)

    def _get_latest_token_end(self):
        if len(self.stack) == 0:
            return 0
        return self.stack[-1].end

    def _add_id_before(self, token, include_token=True):
        end = token.end if include_token else token.start
        id = self.source[self._get_latest_token_end():token.start].strip()
        if id != '' or self._can_be_merged(token):
            id = self._create_id_from_to(self._get_latest_token_end(), end)
            id.value = id.value.strip()
            self._merge_with_previous_id_or_add_to_stack(id)
            return True
        return False

    def _can_be_merged(self, token):
        return len(self.stack) != 0 \
               and self.stack[-1].type == Literals.ID \
               and isinstance(token.type, Literals) \
               and token.type != Literals.STRING

    def _create_id_from_to(self, start_pos, end_pos):
        value = self.source[start_pos:end_pos].strip()
        return self._create_id_token(value, start_pos, end_pos)

    def _merge_with_previous_id_or_add_to_stack(self, id_token):
        if len(self.stack) != 0 and self.stack[-1].type == Literals.ID:
            self._merge(self.stack[-1], id_token)
        else:
            self._add_to_stack(id_token)

    def _get_between_tokens(self, token1, token2):
        return self.source[token1.end:token2.start]

    def _is_wrong_end_partner(self, token):
        if token.block != Block.END_PARTNER:
            return False
        if len(self.partner_name_stack) == 0:
            return True
        if self.partner_name_stack[-1].type == token.type:
            self.partner_name_stack.pop()
            return False
        return True

    def _merge(self, token_to_change, token_to_add):
        token_to_change.value += ' ' + token_to_add.value
        token_to_change.end = token_to_add.end

    def _add_to_stack(self, token):
        if token.block == Block.BEGIN_PARTNER:
            self.partner_name_stack.append(token)
        self.stack.append(token)

    @staticmethod
    def _create_id_token(value, start, end):
        return Token(value, Literals.ID, Block.NONE, Suffix.NONE, start, end)

    def _finish_lex(self):
        eof = self._create_token_eof()
        self._add_literals_before(eof)
        self._add_to_stack(eof)
        self.tokens = self.stack
        self.stack = []
        self.add_line_count_to_tokens()

    def _create_token_eof(self):
        return Token('EOF', 'EOF', Block.NONE, Suffix.NONE,
                     len(self.source), len(self.source))

    def add_line_count_to_tokens(self):
        new_line_positions = list(self._get_new_line_positions())
        line_count = 0
        latest_new_line_pos = 0
        for index, token in enumerate(self.tokens):
            while len(new_line_positions) > line_count \
                    and token.start > new_line_positions[line_count]:
                latest_new_line_pos = new_line_positions[line_count]
                line_count += 1
            token.line = line_count
            offset = 0 if line_count == 0 else 1
            token.column = token.start - latest_new_line_pos - offset

    def _get_new_line_positions(self):
        for index, char in enumerate(self.source):
            if char == '\n':
                yield index

    def get_next_token(self):
        if len(self.tokens) == 0:
            return Token.default_token()
        token = self.tokens.pop(0)
        while len(self.tokens) > 0 and token.type == Keywords.COMMENT:
            token = self.tokens.pop(0)
        return token

    def peek(self):
        if len(self.tokens) == 0:
            return Token.default_token()
        return self.tokens[0]
