# -*- coding:utf-8 -*-
import parser_combinator.parser_combinator as pc

# 以下のimport文でまとめて読み込む用モジュール
# from parser_combinator.load_module import *
# * でインポートするとモジュール名無しでクラスが呼び出せるが
# 読み込みたくないものまでインポートしてしまうのでここでコントロールする
Str = pc.Str
Any = pc.Any
Greedy = pc.Greedy
Repeat = pc.Repeat
Option = pc.Option
Or = pc.Repeat
And = pc.And
Join = pc.Join
Converter = pc.Converter
Ignore = pc.Ignore
