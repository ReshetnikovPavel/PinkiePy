from rply import LexerGenerator


def regex_is_keyword():
    return ''.join([rf'({key})|' for key in keywords])[:-1]


def infix(key):
    return rf"(?<=[\s.,!?‽…:]){key}(?=[\s.,!?‽…:])"


def add_not_postfix(key):
    return rf"{key}(?:(?:n't)|(?: not))"


keywords = {
    r"\d+": "NUMBER",
    r'["”“](?:.|\n)*?["”“]': "STRING",
    r"['‘’].?['‘’]": "CHAR",
    r"[.,!?‽…:]": "PUNCTUATION",
    #r"(P.)+S.+\n": "COMMENT_INLINE",
    #r"\(.*\)": "COMMENT_BLOCK",
    r"/": "SOLIDUS",

    r"That's what I would do": "END",
    r"Conditional conclusion": "DEFAULT",
    r"Or else": "ELSE",
    r"Otherwise": "ELSE",
    r"On the": "CASE_PREFIX",
    r"(?:(?:nd)|(?:rd)|(?:st)|(?:th))? hoof": "CASE_POSTFIX",
    r"If": "IF_PREFIX",
    r"When": "IF_PREFIX",
    r"then": "IF_POSTFIX",
    r"In regards to": "SWITCH",
    r"Dear": "REPORT_DECLARATION",
    r"I learned": "PARAGRAPH_DECLARATION",
    r"Today I learned": "MANE_PARAGRAPH_DECLARATION",
    r"Did you know that": "VARIABLE_DEFINITION",
    r"to get": "RETURNED_VARIABLE_TYPE_DEFINITION",
    r"with": "RETURNED_VARIABLE_TYPE_DEFINITION",
    r"Your faithful student": "END_REPORT",
    r"That’s all about": "END_PARAGRAPH",
    r"Remember when I wrote about": "REPORT_IMPORT",
    rf"{infix('has')}": "VARIABLE_INITIALIZATION-EQUAL_INFIX",
    rf"{infix('is')}": "VARIABLE_INITIALIZATION-EQUAL_INFIX",
    r"likes?": "VARIABLE_INITIALIZATION",
    rf"{infix('was')}": "VARIABLE_INITIALIZATION-EQUAL_INFIX",
    r"always": "CONSTANT_INITIALIZATION",
    r"using": "LISTING_PARAGRAPH_PARAMETERS",
    r"I did this while": "END_DO_WHILE",
    r"I did this as long as": "END_DO_WHILE",
    r"That's what I did": "END_WHILE",
    r"Here's what I did": "DO_WHILE",
    r"As long as": "WHILE",
    r"While": "WHILE",
    r"I said": "PRINT",
    r"I sang": "PRINT",
    r"I wrote": "PRINT",
    r"I asked": "PROMPT_USER_FOR_IMPORT",
    r"I heard": "READLINE",
    r"I read": "READLINE",
    r"Then you get": "RETURN",
    r"I remembered": "RUN_PARAGRAPH",
    r"I would": "RUN_PARAGRAPH",
    r"(?:the )?logic": "BOOLEAN_TYPE",
    r"(?:(?:an )|(?:the ))?argument": "BOOLEAN_TYPE",
    r"(?:the )?logics": "BOOLEAN_ARRAY_TYPE",
    r"(?:(?:a )|(?:the ))?number": "NUMBER_64_TYPE",
    r"(?:(?:a )|(?:the ))?character": "CHAR_TYPE",
    r"(?:(?:a )|(?:the ))?letter": "CHAR_TYPE",
    r"(?:(?:many )|(?:the ))?numbers": "NUMBER_64_ARRAY_TYPE",
    r"(?:(?:many )|(?:the ))?phrases": "CHAR_ARRAY_OF_ARRAYS_TYPE",
    r"(?:(?:many )|(?:the ))?quotes": "CHAR_ARRAY_OF_ARRAYS_TYPE",
    r"(?:(?:many )|(?:the ))?sentences": "CHAR_ARRAY_OF_ARRAYS_TYPE",
    r"(?:(?:many )|(?:the ))?words": "CHAR_ARRAY_OF_ARRAYS_TYPE",
    r"(?:(?:a )|(?:the ))?phrase": "CHAR_ARRAY_TYPE",
    r"(?:(?:a )|(?:the ))?quote": "CHAR_ARRAY_TYPE",
    r"(?:(?:a )|(?:the ))?sentence": "CHAR_ARRAY_TYPE",
    r"(?:(?:a )|(?:the ))?word": "CHAR_ARRAY_TYPE",
    r"(?:the )?characters": "CHAR_ARRAY_TYPE",
    r"(?:the )?letters": "CHAR_ARRAY_TYPE",
    r"are now": "VARIABLE_VALUE_ASSIGNMENT",
    r"becomes?": "VARIABLE_VALUE_ASSIGNMENT",
    r"is now": "VARIABLE_VALUE_ASSIGNMENT",
    r"now likes?": "VARIABLE_VALUE_ASSIGNMENT",
    #   Operators
    rf"{infix('added to')}": "ADDITION_INFIX",
    rf"{infix('plus')}": "ADDITION_INFIX",
    rf"{infix('divided by')}": "DIVISION_INFIX",
    rf"{infix('multiplied with')}": "MULTIPLICATION_INFIX",
    rf"{infix('times')}": "MULTIPLICATION_INFIX",
    rf"{infix('minus')}": "SUBTRACTION_INFIX",
    rf"{infix('without')}": "SUBTRACTION_INFIX",
    r"got one less": "DECREMENT_POSTFIX",
    r"got one more": "INCREMENT_POSTFIX",
    r"add": "ADDITION_PREFIX",
    r"divide": "DIVISION_PREFIX",
    r"by": "BY",
    r"multiply": "MULTIPLICATION_PREFIX",
    r"the product of": "MULTIPLICATION_PREFIX",
    r"subtract": "SUBTRACTION_PREFIX",
    r"the difference between": "SUBTRACTION_PREFIX",
    r"from": "FROM",
    r"There was one less": "DECREMENT_PREFIX",
    r"There was one more": "INCREMENT_PREFIX",
    rf"{infix('and')}": "AND_INFIX",
    rf"{infix('or')}": "OR_INFIX",
    r"either": "EXCLUSIVE_OR_PREFIX",
    r"not": "NOT_PREFIX",
    r"it's not the case that": "NOT_PREFIX",
    rf"{infix('(?:(?:had)|(?:has)) more than')}": "GREATER_THAN_INFIX",
    rf"{infix('(?:(?:is)|(?:was)|(?:were)) greater than')}":
        "GREATER_THAN_INFIX",
    rf"{infix('(?:(?:is)|(?:was)|(?:were)) more than')}":
        "GREATER_THAN_INFIX",
    #   TODO
    r"(((is)|(was)|(were)(n't)|( not)|( no))|((had)|(has) no)) less than":
        "GREATER_THAN_OR_EQUAL_INFIX",
    rf"{infix('(?:(?:had)|(?:has)) less than')}": "LESS_THAN_INFIX",
    rf"{infix('(?:(?:is)|(?:was)|(?:were)) less than')}":
        "LESS_THAN_INFIX",
    #   TODO
    r"(?<=[\s.,!?‽…:])((is)|(was)|(were)(n't)|( not)|( no) (greater)|(more))"
    r"|((had)|(has) no more) than(?=[\s.,!?‽…:])":
        "GREATER_THAN_OR_EQUAL_INFIX",
    rf"{infix('had')}": "EQUAL_INFIX",
    rf"{infix('were')}": "EQUAL_INFIX",
    rf"{infix(add_not_postfix('had'))}": "NOT_EQUAL_INFIX",
    rf"{infix(add_not_postfix('has'))}": "NOT_EQUAL_INFIX",
    rf"{infix(add_not_postfix('is'))}": "NOT_EQUAL_INFIX",
    rf"{infix(add_not_postfix('was'))}": "NOT_EQUAL_INFIX",
    rf"{infix(add_not_postfix('were'))}": "NOT_EQUAL_INFIX",

    r"correct": "TRUE",
    r"right": "TRUE",
    r"true": "TRUE",
    r"yes": "TRUE",
    r"false": "FALSE",
    r"incorrect": "FALSE",
    r"no": "FALSE",
    r"wrong": "FALSE",
    r"nothing": "NULL",
}

lg = LexerGenerator()
lg.ignore(r"\s")
lg.ignore(r"(P.)+S.+\n")
lg.ignore(r"\(.*\)")
for keyword in keywords.items():
    lg.add(keyword[1], keyword[0])
lg.add("NAME", rf'(?:(?!{regex_is_keyword()}).)*')
lg.add("NONSENSE", r".+?")
lexer = lg.build()

program = """Dear Princess Celestia: Hello World!

Today I learned how to say Hello World!
I said “Hello World”!
That’s all about how to say Hello World!

Your faithful student, Kyli Rouge.
"""

program2 = """Dear Princess Celestia: Numbers are fun! (Start the class, naming it and its superclass)

Today I learned some math. (Start the mane method. This is the first part that runs)
I wrote the sum of everything from 1 to 100. (Run the “the sum of all the numbers from 1 to 100” method and print the return value)
That’s all about some math. (and now the program has finished running)

I learned the sum of everything from 1 to 100 to get a number. (start of a new method)
Did you know that the sum was the number 0? (Declare a new variable named “the sum” to be a number, and initialize it to 0)
Did you know that the current count was the number 0? (Declare a new variable named “the current count” to be a number, and initialize it to 0)

As long as the current count was no more than 100: (Start a conditional statement that loops while “the current count” is less than or equal to 100)
I would add the current count to the sum. (Increment “the sum” by the value held in “the current count”)
the current count got one more. (Increment “the current count” by 1)
That’s what I did. (End of the loop)

Then you get the sum! (Return the value held in “the sum”)
That’s all about the sum of everything from 1 to 100. (End of the method)

Your faithful student, Kyli Rouge. (End the class and sign your name)
"""

program3 = """Dear Princess Celestia: Letter One.

Today I learned how to sing Applejack's Drinking Song.

Did you know that Applejack likes the number 99?

As long as Applejack had more than 1…
I sang Applejack" jugs of cider on the wall, "Applejack" jugs of cider,".
Applejack got one less. (Jug of cider)

When Applejack had more than 1… (Jugs of cider)
I sang "Take one down and pass it around, "Applejack" jugs of cider on the wall.".

Otherwise: If Applejack had 1… (Jug of cider)
I sang "Take one down and pass it around, 1 jug of cider on the wall.
1 jug of cider on the wall, 1 jug of cider.
Take one down and pass it around, no more jugs of cider on the wall.".

Otherwise…
I sang "No more jugs of cider on the wall, no more jugs of cider.
Go to the store and buy some more, 99 jugs of cider on the wall.".
That's what I would do, That’s what I did.

That's all about how to sing Applejack's Drinking Song!

Your faithful student, Twilight Sparkle.

P.S. Twilight's drunken state truly frightened me, so I couldn't disregard her order to send you this letter. Who would have thought her first reaction to hard cider would be this... explosive? I need your advice, your help, everything, on how to deal with her drunk... self. -Spike
"""

stream = lexer.lex(program3)
for i in stream:
    print(i)
