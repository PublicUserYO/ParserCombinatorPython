# -*- coding:utf-8 -*-
from parser_combinator.load_module import *

target = "I am Taro."

# parser
blank = Str(" ") * Greedy()
iam = (Str("I") + blank + Str("am")) * Join()
name = Any() * Greedy()

parser = (iam + blank + name ) * Join()

def english_deutch(word):
    if word == "I am" :
        return "Ich bin"
    elif word == "apple":
        return "Apfel"
    else:
        return word

parser_e2d = (iam @ english_deutch + blank + name ) * Join()

print(parser.parse(target))
print(parser_e2d.parse(target))


