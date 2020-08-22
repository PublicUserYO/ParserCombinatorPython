# Python での パーサコンビネータのサンプル

## 動作環境

Python 3.8.5  
Windows 10

## 説明

定義されたクラスを使ってパーサを組み立てることができます。


## 部品説明
| #   | クラス名  | 説明                                                     | 演算子|
| --- | --------- | -------------------------------------------------------- | --|
| 1   | Str       | 引数の文字列を抽出する                                   |
| 2   | Any       | 引数に指定した文字列以外を抽出する                       |
| 3   | Greedy    | パーサを可能な限り繰り返し実行する                       | * で左辺に適用|
| 4   | Repeat    | パーサを指定の回数実行する                               |* で左辺に適用|
| 5   | Option    | パーサを任意項目にする                                   |* で左辺に適用|
| 6   | Or        | 複数のパーサを実行し最初に解析に成功したものを結果とする |　\| 演算子で同等の結果 |
| 7   | And       | 複数のパーサを順に実行する                               |　+  演算子で同等の結果 
| 8   | Join      | And,Repeatなどは結果が配列で戻るのでそれを結合する       | * で左辺に適用
| 9   | Converter | パーサの解析結果に対して関数を適用する                   |　@演算子の左辺に関数を置くことで同等の結果
| 10  | Ignore    | 解析結果を出力しない(Join等で無視する)                   | * で左辺に適用

## 使用例
例1
```
parser = Str("abc")


test1 = "abcdef"
test2 = "defabc"
test3 = "abcabc"

result1 = parser.parse(target1)
result2 = parser.parse(target2)
result3 = parser.parse(target3)

# "abc"が抽出される
print(result1)

# 失敗する
print(result2)

# "abc"が抽出される
print(result3)
```
例2
```
parser = Str("abc") * Greedy()


test1 = "abcdef"
test2 = "defabc"
test3 = "abcabc"

result1 = parser.parse(target1)
result2 = parser.parse(target2)
result3 = parser.parse(target3)

# "abc"が抽出される
print(result1)

# 失敗する
print(result2)

# "abcabc"が抽出される
print(result3)
```
## サンプルプログラム
チェックアウトして以下のコマンドで動かせる。  
`python src\sample_markdown.py`  
`python src\sample_converter.py`  

サンプルとは関係ないがgit bash for windowsでpythonを実行すると設定次第でエラーが出る時もあるので注意
