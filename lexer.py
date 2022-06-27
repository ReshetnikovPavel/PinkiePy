from rply import LexerGenerator
lg = LexerGenerator()

keywords = {
    #   TODO it uses the same keyword
    #
    r"That's what I would do": ("END_IF", "END_ELSE", "END_SWITCH"),
    r"Conditional conclusion": "DEFAULT",
    r"(Or else)|(Otherwise)": "ELSE",
    r"On the \d+((nd)|(rd)|(st)|(th))? hoof": "CASE",
    r"(If)|(When) .+( then)?": "IF",
    r"In regards to": "SWITCH",
    r"Dear": "REPORT_DECLARATION",
    r"I learned": "PARAGRAPH_DECLARATION",
    r"Today I learned": "MAIN_PARAGRAPH_DECLARATION",
    r"Did you know that": "VARIABLE_DEFINITION",
    r"(to get)|(with)": "RETURNED_VARIABLE_TYPE_DEFINITION",
    r"Your faithful student": "END_REPORT",
    r"That’s all about": "END_PARAGRAPH",
    r"Remember when I wrote about": "REPORT_IMPORT",
    r"(has)|(is)|(like)|(likes)|(was)": "VARIABLE_INITIALIZATION",
    r"always (has)|(is)|(like)|(likes)|(was)": "CONSTANT_INITIALIZATION",
    r"and": "LISTING_IMPORTED_INTERFACES",
    r"using": "LISTING_PARAGRAPH_PARAMETERS",
    r"I did this (while)|(as long as)": "END_DO_WHILE",
    r"That's what I did": "END_WHILE",
    r"Here's what I did": "DO_WHILE",
    r"(As long as)|(while)": "WHILE",
    r"I (said)|(sang)|(wrote)": "PRINT",
    r"I asked": "PROMPT_USER_FOR_IMPORT",
    r"I (heard)|(read)": "READLINE",
    r"Then you get": "RETURN",
    r"I (remembered)|(would)": "RUN_PARAGRAPH",
    r"((an )|(the )?argument)|((the )?logic)": "BOOLEAN",
    r"(the )?(arguments)|(logics)": "BOOLEAN_ARRAY",
    r"(a )|(the )?number": "NUMBER_64",
    r"(a )|(the )?(character)|(letter)": "CHAR",
    r"(many )|(the )?numbers": "NUMBER_64_ARRAY",
    r"(many )|(the )?(phrases)|(quotes)|(sentences)|(words)":
        "CHAR_ARRAY_OF_ARRAYS",
    r"((a )|(the )?(phrase)|(quote)|(sentence)|(word))"
    r"|((the )?(characters)|(letters)": "CHAR_ARRAY",
    r"(are now)|(becomes?)|(is now)|(now likes?)": "VARIABLE_VALUE_ASSIGNMENT",
    #   Operators
    r"(added to)|(and)|(plus)": "ADDITION_",
    r"divided by": "DIVISION",
    r"(multiplied with)|(times)": "MULTIPLICATION",
    r"(minus)|(without)": "SUBTRACTION",
    r"got one less": "DECREMENT",
    r"got one more": "INCREMENT",
    #   TODO
}