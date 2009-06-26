
from pyparsing import Literal, CaselessKeyword, CaselessLiteral, \
     Word, Optional, OneOrMore, Group, Combine, ZeroOrMore, nums, \
     Forward, StringEnd, restOfLine, alphas, alphanums, CharsNotIn, \
     MatchFirst, And, Or, quotedString, QuotedString


def attr_parser(keylist):
    lhs = Or([Literal(k) for k in keylist])
    #lhs = Word(alphas, alphas+nums)
    rhs = Or([Word(alphas+nums), quotedString, QuotedString("{",endQuoteChar="}")])
    expr = lhs + Optional(Literal("=").suppress() + rhs)
    expr.setParseAction(lambda s, l, tok: tuple(tok))
    
    return ZeroOrMore(expr)

#parse_attr = attr_parser().parseString

def test_attr():

    p = attr_parser("color font tag select source".split())
    assert  p.parseString("color = green")[0] == ("color", "green")
    assert  p.parseString("font=\"123 123\"")[0] == ("font", '"123 123"')
    assert  p.parseString("color")[0] == ("color",)
    assert  p.parseString("tag={group 1}")[0] == ("tag","group 1")


    s = 'color=green font="helvetica 10 normal" tag={group 1} select=1 source'
    ss = p.parseString(s)
    print ss
