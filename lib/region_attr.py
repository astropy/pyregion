
from pyparsing import Literal, CaselessKeyword, CaselessLiteral, \
     Word, Optional, OneOrMore, Group, Combine, ZeroOrMore, nums, \
     Forward, StringEnd, restOfLine, alphas, alphanums, CharsNotIn, \
     MatchFirst, And, Or, quotedString, QuotedString


def attr_parser():
    lhs = Word(alphas)
    paren = QuotedString("(",endQuoteChar=")")
    rhs = Or([Word(alphas+nums),
              quotedString,
              QuotedString("{",endQuoteChar="}"),
              paren + ZeroOrMore(paren),
              Word(nums+" "),
              Word(nums+".")
              ])
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

if __name__ == "__main__":
    p = attr_parser("color font tag select source dashlist panda".split())
    s = 'color=green dashlist= 8 4 font="helvetica 10 normal" tag={group 1} select=1 source panda=(1 3 2)(2 3 4)'
    #s = 'dashlist= 8 4 font=1'
    ss = p.parseString(s)
    print ss
