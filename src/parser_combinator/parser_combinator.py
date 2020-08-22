# -*- coding:utf-8 -*-
import os
from parser_combinator.err_msg import  *
# エラーメッセージ生成用関数
NL = os.linesep
TAB = "\t"
REQUIRES_TYPE_OF = lambda typ : "require(s) an object type of %s" %(str(typ))
ERROR_OUT_OF_INDEX = lambda idx,tgt : "out of range. index is %s . target length is %s." % (idx,len(tgt))
FAILURE_POINT = lambda idx :"failure point is ""index %s""" % idx
FAILURE_PARSER = lambda psr :"failure parser is " + psr.exp
FAILURE_PATTERN_MATCHES = lambda ptn : "matches %s" % ptn

# エラー発生時表示用
def to_disp_sring(orig):
    def conv(arg):
        if arg == "\n":
            return "\\n"
        if arg == "\r":
            return "\\r"
        if arg == "\r\n":
            return "\\r\\n"
        else: 
            return arg
    if isinstance(orig,list):
        return [ conv(o) for o in orig ]
    else:
        return conv(orig)

# 型チェック関数
def typevalidate(instance,typ):
    if not isinstance(instance,typ):
        raise TypeError(REQUIRES_TYPE_OF(typ))

# 解析失敗時の無視用オブジェクト
class Ignore:
    pass
IGNORE = Ignore

# パース結果オブジェクト
class ParseResult(object):
    def __init__(self 
        ,success : bool
        ,extracted 
        ,index : int
        ,failureMsg : ErrMsg = ErrMsg.Empty() ):

        self.success = success
        self.extracted = extracted
        self.index = index
        self._failureMsg = failureMsg
    
    def ext(self,extracted):
        return ParseResult(self.success,extracted,self.index)

    def suc(self,success):
        return ParseResult(success,self.extracted,self.index)

    @property
    def failureMsg(self) -> ErrMsg :
        return self._failureMsg

    @failureMsg.setter
    def failureMsg(self,msg:ErrMsg):
        self.failureMsg = msg
    
    
    def __str__(self):
        s = "result : " + ("success" if self.success else "Failure")
        i = "index : " + str(self.index)
        e = "extracted : " + NL +  ( str(self.extracted) if self.success else "")
        fm = "message : " + str(self.failureMsg) if not self.success else ""
        nl = os.linesep
        return nl.join([s,i,e,fm])

    @staticmethod
    def success(extracted,index:int):
        return ParseResult(True,extracted,index)
    
    @staticmethod
    def failure(index,failureMsg:ErrMsg = ErrMsg.Empty()):
        typevalidate(failureMsg,ErrMsg)
        msg = failureMsg if not ErrMsg.isEmptyMsg(failureMsg) else  ErrMsg() + FAILURE_POINT(index) 
        return ParseResult(False,IGNORE,index,msg)


# パーサー基底クラス
class Parser(object):
    
    def __init__(self,exp=""):
        # ログ出力用関数説明
        self.exp = exp

    def parse(self,target,index = 0):
        return self.parse_internal(target,index)

    def parse_internal(self,target,index):
        raise NotImplementedError("function parse_internal must be implemented!")

    # パーサ同士を + 演算子でつないだ場合はAndオブジェクトを生成
    def __add__(self,other):
        typevalidate(other,Parser)
        
        if isinstance(other,And):
            # otherがAndオブジェクト場合はparsersの先頭に自身を追加する
            temp = [self]
            temp[1:1] = other.parsers 
            return And(*temp)
        else:
            return And(self,other)
    
    # パーサ同士を | 演算子でつないだ場合はOrオブジェクトを生成    
    def __or__(self,other):
        typevalidate(other,Parser)
        return Or(self,other)

    # パーサに対してのMetaParserの適用を * 演算子で行う
    def __mul__(self,other):
        typevalidate(other,MetaParser)
        return other.create_new_parser(self)

    # Parser @ 関数オブジェクト を　Converter呼び出しに変える
    def __matmul__(self, other):
        if callable(other):
            return self * Converter(other)
        else:
            raise TypeError("other requires an object callable")


# パーサを引数に新たなパーサを生成するパーサ
class MetaParser(object):
    
    def create_new_parser(self,parser):
        raise NotImplementedError("function create_new_parser must be implemented!")

# コンストラクタで指定した文字以外なら真、何も指定しないと任意の文字列
class Any(Parser):
    def __init__(self,*patterns):
        self.patterns = [*patterns]

        self.exp = "Any( %s ) " % str( to_disp_sring(self.patterns))

    def parse_internal(self,target,index):
        # indexの範囲チェック
        if index >= len(target):
            msg = ErrMsg() + FAILURE_PARSER(self) + ERROR_OUT_OF_INDEX(index ,target)
            return ParseResult.failure(index,msg)

        for p in self.patterns:
            # マッチしたらNG
            end = index+len(p)
            # パターン文字列の長さがパース対象の未解析文字数を超過していたら無視
            if end < len(target):
                match = target[index:end] == p
                if match:
                    msg = ErrMsg() \
                    + FAILURE_POINT(index) \
                    + FAILURE_PARSER(self) \
                    + FAILURE_PATTERN_MATCHES(p)

                    return ParseResult.failure(index,msg)
        return ParseResult.success(target[index],index+1)


# コンストラクタで指定した文字列にマッチするか判定するパーサ
class Str(Parser):
    def __init__(self,pattern):
        self.pattern = pattern
        self.exp = "%s " % to_disp_sring(pattern)  

    def parse_internal(self,target,index):
        
        plen = len(self.pattern)
        
        if index >= len(target):
            msg = ErrMsg() + ERROR_OUT_OF_INDEX(index ,target)
            return ParseResult.failure(index,msg)
        
        # 未解析の文字列が指定パターンより短ければ強制的にFalse
        suc = target[index:index+plen] == self.pattern if index + plen <= len(target) else False
        
        if suc:
            return ParseResult.success(self.pattern,index + plen)
        else:
            msg = ErrMsg()\
                + FAILURE_POINT(index) \
                + FAILURE_PARSER(self)
            
            return ParseResult.failure(index,msg)

# 判定結果が失敗でもTrueを返すパーサに変換する(indexは進めない)
# alternativeに文字列を指定すると、失敗時にその文字に置き換えられる
# 指定しない場合はIGNOREオブジェクトを入れて、一括処理する側で弾く(Joinとか)
class Option(MetaParser):
    def __init__(self,alternative=IGNORE):
        self.alternative = alternative

    def create_new_parser(self,parser):
        return OptionParser(self.alternative, parser)

# Optionで作るパーサ
class OptionParser(Parser):
    def __init__(self, alternative, parser):
        self.alternative = alternative
        self.parser = parser
        self.exp = "Option( %s )" % parser.exp

    def parse_internal(self,target,index):
        result = self.parser.parse(target,index)
        
        if result.success:
            return result
        # 失敗しても強制的にTrue
        return result.suc(True).ext(self.alternative)

# パーサを指定回数繰り返すパーサを作成する
class Repeat(MetaParser):
    def __init__(self, countmin , countmax = None,join=False):
        self.countmin = countmin
        # max指定がなければminと同じ
        self.countmax =  countmax if countmax is not None else countmin
        self.join = join

    def create_new_parser(self,parser):
        return RepeatParser(self.countmin,self.countmax,False,parser,self.join)

# パーサを指定回数以上繰り返すパーサを作成する
class Greedy(MetaParser):
    def __init__(self, countmin = 1,join = True):
        self.countmin = countmin
        self.join = join
    
    def create_new_parser(self,parser):
        return RepeatParser(self.countmin,None,True,parser,self.join)

# Repeat,Greedyで作られるパーサ
class RepeatParser(Parser):
    def __init__(self,min,max,infinity,psr,join):
        self.min = min
        self.max = max
        self.infinity = infinity
        self.psr = psr
        # 抽出結果を配列ではなく結合した文字列で出力するフラグ
        self.join = join
        
        name = "Greedy" if infinity else "Repeat"
        self.exp = "%s:min=%s max=%s ( %s )" % (name ,str(min) ,str(max),psr.exp)

    def parse_internal(self,target,index):

        def t_parse(i):
            if i >= len(target):
                msg = ErrMsg() + ERROR_OUT_OF_INDEX(i ,target)
                return ParseResult.failure(i,msg)
            return self.psr.parse(target,i)
        
        result = ParseResult(True,IGNORE,index)
        count = 0
        extracted = []
        # 成功している間繰り返す
        while result.success and ( self.infinity or count < self.max ):
            result = t_parse(result.index)
            if result.success:
                count += 1
                extracted.append(result.extracted)
        
        success = count >= self.min 

        if success:

            if self.join:
                extracted = "".join([e for e in extracted if e is not IGNORE])

            return ParseResult.success(extracted,result.index)
        else:
            msg = result.failureMsg.caused_by_me() \
                + FAILURE_POINT(result.index) \
                + FAILURE_PARSER(self) \
                + "success count is %s " % count \
                + "success count of this parser requires is more than or equal to %s " % self.min

            return ParseResult.failure(index,msg)

# コンストラクタで渡したParserを順に評価し、どれかが真となれば真となるパーサ
class Or(Parser):
    def __init__(self,*parsers):
        for p in parsers:
            typevalidate(p,Parser)
        
        self.parsers =[*parsers]
        self.exp = "Or(%s)" % ",".join(to_disp_sring([p.exp for p in parsers]))

    def parse_internal(self,target,index):
        
        for p in self.parsers:
            result = p.parse(target,index)        
            if result.success:
                return result

        msg = ErrMsg() + FAILURE_POINT(index) + FAILURE_PARSER(self)
        return ParseResult.failure(index,msg)

# コンストラクタで渡したParserを順に評価し、すべてが真となった場合のみ真となるパーサー
class And(Parser):
    def __init__(self,*parsers):
        for p in parsers:
            typevalidate(p,Parser)
        
        self.parsers =[*parsers]
        self.exp = "And( %s )" % ", ".join([p.exp for p in self.parsers])

    # Parserの実装のみだと A + B + C = [ [A , B ] , C ]になるので
    # Andオブジェクトの場合は + 演算子の挙動を変える    
    def __add__(self,other):
        typevalidate(other,Parser)
        self.parsers.append(other)
        self.exp = "And( %s )" % ", ".join([p.exp for p in self.parsers])
        return self

    def parse_internal(self,target,index):
        
        index_sum = index
        extracted_sum = []
        for p in self.parsers:
            result = p.parse(target,index_sum)        
            if result.success:
                extracted_sum.append(result.extracted)
                index_sum = result.index
            else:
                msg = result.failureMsg.caused_by_me() \
                + FAILURE_POINT(index_sum)\
                + FAILURE_PARSER(p)

                return ParseResult.failure(index,msg)
                
        return ParseResult.success(extracted_sum, index_sum)
    
# パース結果が文字列の一次元配列になるパーサを文字列に変換するパーサ
# RepeatとかGreedyとかをくっつけるイメージ
class Join(MetaParser):
    def __init__(self,joinstr=""):
        self.joinstr = joinstr

    def create_new_parser(self,parser):
        return JoinParser(self.joinstr,parser)

# Joinで作られるパーサ
class JoinParser(Parser):
    def __init__(self,joinstr,parser):
        self.joinstr = joinstr
        self.parser = parser
        self.exp = parser.exp
    def parse_internal(self,target,index):
        result = self.parser.parse(target,index)
        
        if not result.success:
            return result
        
        # IGNORE (パース失敗したけどOptionでOKしたやつ)とかは除外
        # [["aa","bb"],"c","d"] みたいなのには対応していない
        ext = result.extracted       
        temp_list = ext if isinstance(ext,list) else [ext] 
        validlist = [ e for e in temp_list if e is not IGNORE ]

        extracted = self.joinstr.join(validlist)
        
        return result.ext(extracted)

# パース結果に対して関数を適用する
class Converter(MetaParser):
    def __init__(self,func):
        self.func = func

    def create_new_parser(self,parser):
        return ConverterParser(self.func,parser)

# Converterで作られる関数
class ConverterParser(Parser):
    def __init__(self,func,parser):
        self.func = func
        self.parser = parser
        self.exp = parser.exp

    def parse_internal(self,target,index):
        result = self.parser.parse(target,index)
        if not result.success:
            return result
        e = result.extracted
        arg = e if isinstance(e,list) else [e]
        arg = [ a for a in arg if isinstance(a,str)]
        extracted = self.func(*arg)

        return result.ext(extracted)

# 解析に成功した場合でも出力対象にしないオブジェクトに付与する
class Ignore(MetaParser):
    def create_new_parser(self,parser):
        return IgnoreParser(parser)

class IgnoreParser(Parser):
    def __init__(self,parser):
        self.parser = parser
        self.exp = parser.exp

    def parse_internal(self, target, index):
        return self.parser.parse(target,index).ext(IGNORE)