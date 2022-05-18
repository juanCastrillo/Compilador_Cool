from sly import Lexer, Parser
from math import factorial

class CalcLexer(Lexer):
    tokens = { NAME, NUMBER }
    ignore = ' \t'
    literals = { '=', '+', '-', '*', '/', '(', ')' }

    # Tokens
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class CalcParser(Parser):
    tokens = CalcLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
        )

    def __init__(self):
        self.names = { }

    @_('NAME "=" expr')
    def statement(self, p):
        self.names[p.NAME] = p.expr

    @_("NAME NAME '(' NAME ')' ':' expr")
    def expr(self, p):
        h = p.expr
        def temp(arg):
            return h()
        self.names[p.NAME1] =temp 


    @_("NAME '(' expr ')'")
    def expr(self, p):
        j = p.expr()
        if p.NAME == 'factorial':
            def temp():
                
                return factorial(j)
        else:
            def temp():
                return 0
        return temp


    @_('expr')
    def statement(self, p):
        print(p.expr())

    @_('expr "+" expr')
    def expr(self, p):
        temp1 =p.expr0
        temp2 =p.expr1
        def temp():
            return temp1() + temp2()
        return temp

    @_('expr "-" expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr "*" expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr "/" expr')
    def expr(self, p):

        return p.expr0 / p.expr1

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        def temp():
            return - p.expr()
        return temp

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        i = int(p.NUMBER)
        def temp():
            return i
        return temp

    @_('NAME')
    def expr(self, p):
        try:
            return self.names[p.NAME]
        except LookupError:
            print("Undefined name '%s'" % p.NAME)
            return 0

if __name__ == '__main__':
    lexer = CalcLexer()
    parser = CalcParser()
    while True:
        try:
            text = input('calc > ')
        except EOFError:
            break
        if text:
            parser.parse(lexer.tokenize(text))