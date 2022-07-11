import rply
from rply import LexerGenerator
import re


def regex_is_in(iterator):
    return ''.join([rf'({key[0]})|' for key in iterator])[:-1]


def infix(key):
    return rf"(?<=\s){key}(?=\s)"


def add_not_postfix(key):
    return rf"{key}(?:(?:n't)|(?: not))"


def add_boundary(regex_expr):
    return rf"\b{regex_expr}\b"


def _sort():
    return sorted(
        keywords,
        reverse=True,
        key=lambda x: (len(re.findall(r"[A-Za-z)?]\s[A-Za-z(]", x[0])),
                       len(x[0])))


literals = [(r'["”“](?:.|\n)*?["”“]', "STRING"),
            (r"['‘’].?['‘’]", "CHAR"),
            (r"\d+", "NUMBER"),
            (r"[.,!?‽…:]", "PUNCTUATION"),
            # r"(P.)+S.+\n": "COMMENT_INLINE",
            # r"\(.*\)": "COMMENT_BLOCK",
            # (r"/", "SOLIDUS"),
            (r'\b(?:(?:(?:(?:an )|(?:the ))argument|(?:the )?logic)?)?'
                r'(?:(?:correct)|(?:true)|(?:yes))\b', 'TRUE'),
            (r'\b(?:(?:(?:(?:an )|(?:the ))argument|(?:the )?logic)?)?'
             r'(?:(?:incorrect)|(?:false)|(?:wrong)|(?:no))\b', 'FALSE'),
            (r'\bnothing\b', 'NULL'),
            ]

keywords = [
            (r"[.,!?‽…:]", "PUNCTUATION"),
            (r'\bI did this as long as\b', 'END_DO_WHILE'),
            (r"\bit's not the case that\b", 'NOT_PREFIX'),
            (r'\b(?:(?:is)|(?:was)|(?:were)|(?:had)|(?:has)) no more than',
             'LESS_THAN_OR_EQUAL_INFIX'),
            (r'\b(?:(?:had)|(?:has)) no less than\b', 'GREATER_THAN_OR_EQUAL_INFIX'),
            (r'\bRemember when I wrote about\b', 'REPORT_IMPORT'),
            (r"\bThat's what I would do\b", 'END'),
            (r'\bDid you know that\b', 'VARIABLE_DEFINITION'),
            (r'\bI did this while\b', 'END_DO_WHILE'),
            (r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n't)|(?: not)) greater than",
             'LESS_THAN_OR_EQUAL_INFIX'),
            (r"\b(?:(?:is)|(?:was)|(?:were))(?:(?:n't)|(?: not)) less than",
             'GREATER_THAN_OR_EQUAL_INFIX'),
            (r'\b(?:(?:is)|(?:was)|(?:were)) greater than\b', 'GREATER_THAN_INFIX'),
            (r'\b(?:(?:is)|(?:was)|(?:were)) more than\b', 'GREATER_THAN_INFIX'),
            (r'\b(?:(?:is)|(?:was)|(?:were)) less than\b', 'LESS_THAN_INFIX'),
            (r'\b(?:(?:had)|(?:has)) more than\b', 'GREATER_THAN_INFIX'),
            (r'\b(?:(?:had)|(?:has)) less than\b', 'LESS_THAN_INFIX'),
            (r'\bthe difference between(?=.+?)(?![.,!?‽…:])(?=.+?(?:(?:and)|(?:from)))\b', 'SUBTRACTION_PREFIX'),
            (r'\bYour faithful student\b', 'END_REPORT'),
            (r'\bThere was one less\b', 'DECREMENT_PREFIX'),
            (r'\bThere was one more\b', 'INCREMENT_PREFIX'),
            (r"\bThat's what I did\b", 'END_WHILE'),
            (r"\bHere's what I did\b", 'DO_WHILE'),
            (r'\bThat’s all about\b', 'END_PARAGRAPH'),
            (r'\bIn regards to\b', 'SWITCH'),
            (r'\bgot one less\b', 'DECREMENT_POSTFIX'),
            (r'\bgot one more\b', 'INCREMENT_POSTFIX'),
            (r'\bThen you get\b', 'RETURN'),
            (r'\bAs long as\b', 'WHILE'),
            (r'\b(?:(?:nd)|(?:rd)|(?:st)|(?:th))? hoof\b', 'CASE_POSTFIX'),
            (r'\bConditional conclusion\b', 'DEFAULT'),
            (r'\bToday I learned\b', 'MANE_PARAGRAPH_DECLARATION'),
            (r'\bmultiplied with\b', 'MULTIPLICATION_INFIX'),
            (r'\bthe product of(?=.+?)(?![.,!?‽…:])(?=.+?)(?:(?:and)|(?:by))\b', 'MULTIPLICATION_PREFIX'),
            (r'\bI remembered\b', 'RUN_PARAGRAPH'),
            (r'\bdivided by\b', 'DIVISION_INFIX'),
            (r'\bnow likes?\b', 'VARIABLE_VALUE_ASSIGNMENT'),
            (r'\bI learned\b', 'PARAGRAPH_DECLARATION'),
            (r'\badded to\b', 'ADDITION_INFIX'),
            (r'\bOr else\b', 'ELSE'),
            (r'\bI wrote\b', 'PRINT'),
            (r'\bI asked\b', 'PROMPT_USER_FOR_IMPORT'),
            (r'\bI heard\b', 'READLINE'),
            (r'\bI would\b', 'RUN_PARAGRAPH'),
            (r'\bare now\b', 'VARIABLE_VALUE_ASSIGNMENT'),
            (r'\bOn the\b', 'CASE_PREFIX'),
            (r'\bto get\b', 'RETURNED_VARIABLE_TYPE_DEFINITION'),
            (r'\bI said\b', 'PRINT'),
            (r'\bI sang\b', 'PRINT'),
            (r'\bI read\b', 'READLINE'),
            (r'\bis now\b', 'VARIABLE_VALUE_ASSIGNMENT'),
            #(r'\b(?:(?:many )|(?:the ))?sentences\b', 'CHAR_ARRAY_OF_ARRAYS_TYPE'),
            #(r'\b(?:(?:many )|(?:the ))?numbers\b', 'NUMBER_ARRAY_TYPE'),
            #(r'\b(?:(?:many )|(?:the ))?phrases\b', 'CHAR_ARRAY_OF_ARRAYS_TYPE'),
            #(r'\b(?:(?:an )|(?:the ))?argument\b', 'BOOLEAN_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?character\b', 'CHAR_TYPE'),
            #(r'\b(?:(?:many )|(?:the ))?quotes\b', 'CHAR_ARRAY_OF_ARRAYS_TYPE'),
            #(r'\b(?:(?:many )|(?:the ))?words\b', 'CHAR_ARRAY_OF_ARRAYS_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?sentence\b', 'CHAR_ARRAY_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?number\b', 'NUMBER_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?letter\b', 'CHAR_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?phrase\b', 'CHAR_ARRAY_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?quote\b', 'CHAR_ARRAY_TYPE'),
            #(r'\b(?:(?:a )|(?:the ))?word\b', 'CHAR_ARRAY_TYPE'),
            (r"\bwere(?:(?:n't)|(?: not))\b", 'NOT_EQUAL_INFIX'),
            (r"\bhad(?:(?:n't)|(?: not))\b", 'NOT_EQUAL_INFIX'),
            (r"\bhas(?:(?:n't)|(?: not))\b", 'NOT_EQUAL_INFIX'),
            (r"\bwas(?:(?:n't)|(?: not))\b", 'NOT_EQUAL_INFIX'),
            (r"\bis(?:(?:n't)|(?: not))\b", 'NOT_EQUAL_INFIX'),
            #(r'\b(?:the )?characters\b', 'CHAR_ARRAY_TYPE'),
            #(r'\b(?:the )?letters\b', 'CHAR_ARRAY_TYPE'),
            #(r'\b(?:the )?logics\b', 'BOOLEAN_ARRAY_TYPE'),
            #(r'\b(?:the )?logic\b', 'BOOLEAN_TYPE'),
            (r'\bOtherwise\b', 'ELSE'),
            (r'\bbecomes?\b', 'VARIABLE_VALUE_ASSIGNMENT'),
            (r'\bsubtract(?=.+?)(?![.,!?‽…:])(?=.+?from)\b', 'SUBTRACTION_PREFIX'),
            (r'\bmultiply\b', 'MULTIPLICATION_PREFIX'),
            (r'\bwithout\b', 'SUBTRACTION_INFIX'),
            (r'\balways\b', 'CONSTANT_INITIALIZATION'),
            (r'\bdivide(?=.+?)(?![.,!?‽…:])(?=.+?)(?:(?:and)|(?:by))\b', 'DIVISION_PREFIX'),
            (r'\beither(?=.+?)(?![.,!?‽…:])(?=.+?or)\b', 'EXCLUSIVE_OR_PREFIX'),
            (r'\blikes?\b', 'VARIABLE_INITIALIZATION'),
            (r'\busing\b', 'LISTING_PARAGRAPH_PARAMETERS'),
            (r'\btimes\b', 'MULTIPLICATION_INFIX'),
            (r'\bWhile\b', 'WHILE'),
            (r'\bminus\b', 'SUBTRACTION_INFIX'),
            (r'\bplus\b', 'ADDITION_INFIX'),
            (r'\bWhen\b', 'IF_PREFIX'),
            (r'\bthen\b', 'IF_POSTFIX'),
            (r'\bDear\b', 'REPORT_DECLARATION'),
            (r'\bwith\b', 'RETURNED_VARIABLE_TYPE_DEFINITION'),
            (r'\bwere\b', 'EQUAL_INFIX'),
            (r'\badd(?=.+?)(?![.,!?‽…:])(?=.+?and)\b', 'ADDITION_PREFIX'),
            (r'\badd(?=.+?)(?![.,!?‽…:])(?=.+?to)\b', 'INCREMENT_PREFIX'),
            (r'\band\b', 'AND_INFIX'),
            (r'\bnot\b', 'NOT_PREFIX'),
            (r'\bhad\b', 'EQUAL_INFIX'),
            (r'\bhas\b', 'VARIABLE_INITIALIZATION-EQUAL_INFIX'),
            (r'\bwas\b', 'VARIABLE_INITIALIZATION-EQUAL_INFIX'),
            (r'\bIf\b', 'IF_PREFIX'),
            (r'\bor\b', 'OR_INFIX'),
            (r'\bis\b', 'VARIABLE_INITIALIZATION-EQUAL_INFIX'),
            ]


lg = LexerGenerator()
lg.ignore(r"\s")
lg.ignore(r"(P\.)+S\..*\n")
lg.ignore(r"\(.*\)")
for keyword in literals:
    lg.add(keyword[1], keyword[0])
for keyword in keywords:
    print(keyword)
    lg.add(keyword[1], keyword[0])
#   TODO support 'to', 'from' and others in names (except 'add ... to' etc.)
lg.add("NAME", rf'(?:(?!"|(?:{regex_is_in(literals)})))\s*(?:(?!"|(?:{regex_is_in(keywords)})).)+')
lg.add("NONSENSE", r".+?")
lexer = lg.build()


def lex(program):
    stream = lexer.lex(program)
    for i in stream:
        yield i