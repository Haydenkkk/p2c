import ply.lex as lex


class Scanner(object):
    def find_tok_column(self, token):
        last_cr = self.lexer.lexdata.rfind("\n", 0, token.lexpos)
        if last_cr < 0:
            last_cr = 0
        return token.lexpos - last_cr

    def build(self):
        self.lexer = lex.lex(object=self, debug=False)

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        return self.lexer.token()

    # literals = "{}()<>=;:,+-*/%&|^"

    reserved = {
        "program": "PROGRAM",
        "begin": "BEGIN",
        "end": "END",
        "var": "VAR",
        "if": "IF",
        "then": "THEN",
        "else": "ELSE",
        "case": "CASE",
        "of": "OF",
        "while": "WHILE",
        "do": "DO",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "mod": "MOD",
        "array": "ARRAY",
        "boolean": "BOOLEAN",
        "function": "FUNCTION",
        "return": "RETURN",
        "integer": "INTEGER",
        "real": "REAL",
        "char": "CHAR",
        "string": "STRING",
        "uses": "USES",
        "const": "CONST",
        "type": "TYPE",
        "for": "FOR",
        "to": "TO",
        "downto": "DOWNTO",
        "continue": "CONTINUE",
        "break": "BREAK",
    }

    tokens = [
        "LETTER",  # 字符
        "INT_NUMBER",  # 整数
        "REAL_NUMBER",  # 浮点数
        "ID",  # 标识符 Identifier
        "PLUS",  # +
        "MINUS",  # -
        "TIMES",  # *
        "DIVIDE",  # /
        "ASSIGNOP",  # :=
        "SEMICOLON",  # ;
        "COLON",  # :
        "COMMA",  # ,
        "EQ",  # =
        "LT",  # <
        "LE",  # <=
        "GT",  # >
        "GE",  # >=
        "NE",  # !=
        "LPAREN",  # (
        "RPAREN",  # )
        "LBRAC",  # [
        "RBRAC",  # ]
        "LLAVEI",  # {
        "LLAVED",  # }
        "ENDPOINT",  # .(结束符)
        "GOTO",
        "DOTDOT",  # ..(为了支持数组)
    ] + list(reserved.values())

    t_DOTDOT = "\.\."
    t_LETTER = r"\'[a-zA-Z]\'"
    t_ignore = " \t"
    t_PLUS = r"\+"
    t_MINUS = r"\-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_ASSIGNOP = r":="
    t_SEMICOLON = r"\;"
    t_COLON = r":"
    t_COMMA = r","
    t_EQ = r"\="
    t_LT = r"\<"
    t_LE = r"<="
    t_GT = r"\>"
    t_GE = r">="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRAC = r"\["
    t_RBRAC = r"\]"
    t_LLAVEI = r"{"
    t_LLAVED = r"}"
    t_NE = r"!="
    t_ENDPOINT = r"."
    error = 0

    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        print(
            "Illegal character '{0}' ({1}) in line {2}".format(
                t.value[0], hex(ord(t.value[0])), t.lexer.lineno
            )
        )
        Scanner.error = 1
        t.lexer.skip(1)

    def t_REAL_NUMBER(self, t):
        r"[\+-](\d+\.\d+([eE][\+-]\d+)?)|(\d+[eE][\+-]\d+)"
        t.value = float(t.value)
        t.endlexpos = t.lexpos + len(str(t.value))
        return t

    def t_INT_NUMBER(self, t):
        r"\d+"
        if int(t.value) > 65535:
            print(
                "[lexical] line: {}  Integer out of bounds '{}'".format(
                    t.lexer.lineno, t.value.lower()
                )
            )
        t.value = int(t.value)
        t.endlexpos = t.lexpos + len(str(t.value))
        return t

    def t_ID(self, t):
        r"[a-zA-Z_][a-zA-Z_0-9]*"
        if t.value.upper() in self.reserved:
            t.type = t.value.upper()
        # t.type = Scanner.reserved.get(t.value.lower(), "ID")
        print("{} type: {}".format(t.value, t.type))
        t.endlexpos = t.lexpos + len(t.value)
        return t

    def t_COMMENT(self, t):
        r"(/\*(.|\n)*?\*/)|(//.*\n)"
        # r"(?s)(\(\*.*?\*\))|({[^}]*})"
        t.lexer.lineno += t.value.count("\n")
        t.endlexpos = t.lexpos + len(t.value)
        pass


scanner = Scanner()
scanner.build()
fin = "testcodes/1.pas"
f = open(fin, "r")
data = f.read()
scanner.input(data)
while True:
    tok = scanner.token()
    if not tok:
        break
    print(tok)
