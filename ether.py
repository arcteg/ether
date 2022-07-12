from sly import Lexer, Parser
from colorama import init, Fore, Style


init()


class ModLexer(Lexer):
    tokens = {NAME, NUMBER, STRING}
    ignore = '\t '
    literals = {'=', '+', '-', '/', '*', '(', ')'}

    NAME = r'[a-zA-Zа-яА-Я_][a-zA-Zа-яА-Я0-9_]*'
    STRING = r'\".*?\"|\'.*?\''

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

    def error(self, t):
        print(Fore.RED, "Error 2: Undefined character found!", Style.RESET_ALL, sep='')
        self.index += 1


class ModParser(Parser):
    tokens = ModLexer.tokens

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


class ModExecute:
    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"' \
                or isinstance(result, str) and result[0] == "'":
            print(result)

    def walkTree(self, node):
        ops = ["help", "credits"]
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
            if self.walkTree([node[1]]) > 0:
                if self.walkTree(node[2]) > 0:
                    return self.walkTree(node[1]) * self.walkTree(node[2])
            elif self.walkTree(node[1]) < 0:
                return - self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            try:
                return self.walkTree(node[1]) / self.walkTree(node[2])
            except ZeroDivisionError:
                print(Fore.RED, 'Error 3: Zero division found!', Style.RESET_ALL, sep='')

        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'var':
            if node[1] not in ops:
                try:
                    return self.env[node[1]]
                except LookupError:
                    print(Fore.RED, "Error 1: Undefined name '" + node[1] + "' found!", Style.RESET_ALL, sep='')
            else:
                if node[1] == 'help':
                    print('Available commands: help, credits, <any basic math operations>')
                elif node[1] == 'credits':
                    print('Code, architecture & tests: N.Trushko, A.Paruhin, A.Ivanov, K.Savin (SPbSUT)')


if __name__ == '__main__':
    lexer = ModLexer()
    parser = ModParser()
    print(Fore.BLUE + """
    ______________  ____________           ____   ___ 
   / ____/_  __/ / / / ____/ __ \   _   __/ __ \ |__ \\
  / __/   / / / /_/ / __/ / /_/ /  | | / / / / / __/ /
 / /___  / / / __  / /___/ _, _/   | |/ / /_/ / / __/ 
/_____/ /_/ /_/ /_/_____/_/ |_|    |___/\____(_)____/ 
-----------------------------------------------------\n""", Style.RESET_ALL,
"""Ether Language v0.2.\nType "help" or "credits" for more information.""", sep='')
    env = {}

    while True:
        try:
            print("Ether>", end='')
            text = input()
        except EOFError:
            break
        if text:
            if text == 'exit()':
                break
            elif text:
                tree = parser.parse(lexer.tokenize(text))
            ModExecute(tree, env)
