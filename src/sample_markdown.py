# -*- coding:utf-8 -*-
from parser_combinator.load_module import *
import os

# 文字列の長さをstringで取得(lenをそのまま使うとintになるため)
slen = lambda s : str(len(s))
# タグ文字列生成
tag = lambda tagname , element : "<" + tagname + ">" + element + "</" + tagname + ">"
tagnl = lambda tagname , element : "<" + tagname + ">" + os.linesep + element + os.linesep + "</" + tagname + ">"

# 汎用パーサ
## 改行コード
newline = ( Str("\r\n") | Str("\r") | Str("\n") ) * Ignore()
## 改行コード(オプション)
optnewline = newline * Option()
## 行の文字(改行ではない文字を)
lineChar = Any("\r\n","\r","\n")
## 行の文字列
lineContent = lineChar * Greedy()

# hタグの定義
h_def = Str("#") * Greedy() + Str(" ") * Greedy() + lineContent
h_conv = lambda sharp ,blank ,element : tag( "h"+ slen(sharp) ,element )
h_parser = h_def @ h_conv
h_line = (h_parser + optnewline) * Join()

# ulタグの定義
# ulの中のliの定義
ul_def = Str("*") + Str(" ") * Greedy() + lineContent
ul_conv = lambda asta , blank ,element : tag("li",element)
ul_parser = ul_def @ ul_conv
ul_line = (ul_parser + optnewline) * Join()
# liの集合をグループ化
ul_group_def = ul_line * Greedy(join=False) * Join(os.linesep)
ul_group_conv = lambda li : tagnl("ul",li)
ul_group = ul_group_def @ ul_group_conv

# 行だったらなんでもよい
anyline = (lineChar * Greedy(0) + optnewline) * Join()


# 上で作成した定義に合わせてMarkDown用パーサの生成
markdown_def = ( h_line | ul_group | newline | anyline  ) * Greedy(join=False)
markdown_conv = lambda *args : os.linesep.join(args)
markdown_parser = markdown_def @ markdown_conv 


target = """
# これが表題です
表題の説明
## 章1
章の中身
### あああ
色々
## 章2
* あいうえお
* かきくけこ
* さしすせそ
"""

result = markdown_parser.parse(target)

print(result)