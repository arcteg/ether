from sly import Lexer, Parser


class BasicLexer(Lexer):
    tokens = {NAME, NUMBER, STRING}
    ignore = '\t '
    literals = {'=', '+', '-', '/',
                '*', '(', ')', ',', ';'}
                
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'//.*')
    def COMMENT(self, t):
        pass

    @_(r'\n+')
    def newline(self, t):
        self.lineno = t.value.count('\n')


class BasicParser(Parser):
    tokens = BasicLexer.tokens
    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.env = {}

    @_('')
    def statement(self, p):
        pass

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('NAME "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)

    @_('expr')
    def statement(self, p):
        return (p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)


class BasicExecute:

    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)

    def walkTree(self, node):
        if isinstance(node, int) or isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])


        if node[0] == 'str':
            return node[1]

        if node[0] == 'num':
            return node[1]

        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[1] == 'help':
            print('Available commands: print(), input(), help, credits')

        if node[1] == 'credits':
            print('Code & architecture: <names>')

        if node[0] == 'var':
            if node[1] != 'help' and node[1] != 'credits':
                try:
                    return self.env[node[1]]
                except LookupError:
                    print("Error 1: Undefined symbol '" + node[1] + "' found.")


if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    print('Ether Language v0.1.\nType "help" or "credits" for more information.')
    env = {}

    while True:
        try:
            text = input('Ether> ')
        except EOFError:
            break
        if text:
            if text == 'exit()':
                break
            elif text:
                tree = parser.parse(lexer.tokenize(text))
            BasicExecute(tree, env)