![PinkiePy](https://user-images.githubusercontent.com/92433826/187067728-fe30eea0-b4e9-4f48-8c8a-3e94be6b4303.png)

**PinkiePy** is a [FiM++](https://esolangs.org/wiki/FiM%2B%2B) interpreter written in Python. **PinkiePy** follows [FiM++ 1.0 (Sparkle) language specification](https://docs.google.com/document/d/1gU-ZROmZu0Xitw_pfC1ktCDvJH5rM85TxxQf5pg_xmg/edit#) and also adds some OOP features it lacks.

# Installation

```
# clone the repo
$ git clone https://github.com/ReshetnikovPavel/PinkiePy

# change the working directory to PinkiePy
$ cd PinkiePy

# install the requirements
$ python3 -m pip install -r requirements.txt
```


# Usage

## Interpreter
```
python pinkiepy.py 'full or relative path to file/File Name.fim'
```

## Debugger

```
python pinkiepy.py -d 'full or relative path to file/File Name.fim'
```

# Language documentation
For main features read [FiM++ 1.0 (Sparkle) language specification](https://docs.google.com/document/d/1gU-ZROmZu0Xitw_pfC1ktCDvJH5rM85TxxQf5pg_xmg/edit#), but keep in mind that it has some inconsistencies in examples.

## Code outside classes

Unlike specification it is also allowed to write code outside of classes, so you can write Hello World program like this:

```
I said "Hello World"!
```

Or like this as it was suggested in the specification:

```
Dear Princess Celestia: Hello World!

Today I learned how to say Hello World!
I said “Hello World”!
That’s all about how to say Hello World!

Your faithful student, Pinkie Pie.
```


## Object-Orientation
### Class declaration

In addition to what's written in the specification, you can declare fields using the same syntax as variable declaration.

```
Dear Princess Celestia: Class Name!

    Did you know that field is correct?
    
    Today I learned main method name.
        I remembered method name!
    That's all about main method name.
    
    I learned method name.
        I sang field!
    That's all about method name.    
    
Your faithful student, Pinkie Pie.
```

### Class instance creation

You can create a new instance of a class like this:

```
Did you know that instance name is Class Name?
```

So, if you write a class name in an expression, you create a new instance of it.
Also you can use ``` this report ``` inside a class to get an instance of this class.

*Note: constructors are not implemented, but you can declare a method called, for example, creation and call it on a new instance like so:*

```
Dear Princess Celestia: Class Name!
    
    I learned creation.
        I said "New class instance".
    That's all about creation.    
    
Your faithful student, Pinkie Pie. 

I remembered Class Name`s creation.
```

### Accessing class contents

Use ``` `s ``` or ``` ` ``` after class instance to access it's contents.
```
I said instance`s field!
I remembered instance`s method name!
instance`s field is now 2!
```

*Note: this syntax was inspired by [this proposal on language wiki](https://fimpp.fandom.com/wiki/FiM%2B%2B_Wiki:Proposals/Object-Orientation), but I decided to use ``` ` ``` instead of ``` ' ``` to avoid collision with [Applejack's hat](https://fimpp.fandom.com/wiki/Applejack%27s_Hat).*

### Arrays
The same ``` `s ```, ``` ` ``` syntax is used to access an element of an array with a named variable:

```
Did you know that cake has many names?
cake 1 is “chocolate”.
cake 2 is “apple cinnamon”.
cake 3 is “fruit”.
I said cake 2.

Did you know that apple is number 2?
I said cake`s apple.
```

*Note: ``` `s ``` can be used as ``` of ``` in [FiMSharp](https://github.com/Jaezmien/FiMSharp) if you swap variable names. (``` of ``` is not supported in **PinkiePy**)*
*Note: arrays start at 0*


## Import
You can import a class from another file with the same name. So if you have a file called *Class Name.fim* somewhere in the opened directory and it has a class named *Class Name* you can import this class like so:

```
Remember when I wrote about Class Name?
```

## Typechecking
*Warning! Custom classes are not supported in typechecking due to ambiguity in syntax.*


# Links
- [FiM++ 1.0 (Sparkle) language specification](https://docs.google.com/document/d/1gU-ZROmZu0Xitw_pfC1ktCDvJH5rM85TxxQf5pg_xmg/edit#)
- [FiM++ Community Wiki](https://fimpp.fandom.com/wiki/FiM%2B%2B_Wiki)
- [FiM++ on esolangs](https://esolangs.org/wiki/FiM%2B%2B)

Resources about making interpreters:
- [Crafting Interpreters by Robert Nystrom](https://craftinginterpreters.com/)
- [Let’s Build A Simple Interpreter by Ruslan Spivak](https://ruslanspivak.com/lsbasi-part1/)
