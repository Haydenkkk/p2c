import ply.lex as lex


class Scanner(object):
    def find_tok_column(self, token):
        last_cr = self.lexer.lexdata.rfind("\n", 0, token.lexpos)
        if last_cr < 0:
            last_cr = 0
        return token.lexpos - last_cr

    def build(self):
        self.lexer = lex.lex(object=self, debug=False)
        self.error = []
        self.comment = []

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        return self.lexer.token()

    # 定义token
    tokens = (
        "REAL",
        "COLON",
        "LBRACKET",
        "LPAREN",
        "DIGITS",
        "ASSIGNOP",
        "FOR",
        "DO",
        "UMINUS",
        "OF",
        "NUM",
        "EQUAL",
        "ELSE",
        "CONST",
        "COM",
        "RPAREN",
        "ARRAY",
        "INTEGER",
        "THEN",
        "POINTTO",
        "CHAR",
        "NOT",
        "POINT",
        "TO",
        "PROCEDURE",
        "WHILE",
        "LETTER",
        "RELOP",
        "VAR",
        "BOOLEAN",
        "IF",
        "FUNCTION",
        "END",
        "RBRACKET",
        "PROGRAM",
        "READ",
        "WRITE",
        "BEGIN",
        "SEMICOLON",
        "ID",
        "MULOP",
        "ADDOP",
    )
    # 定义保留字
    reserved = [
        "PROGRAM",
        "VAR",
        "BEGIN",
        "END",
        "IF",
        "THEN",
        "ELSE",
        "WHILE",
        "DO",
        "INTEGER",
        "REAL",
        "PROCEDURE",
        "FOR",
        "OF",
        "CONST",
        "TO",
        "ARRAY",
        "CHAR",
        "BOOLEAN",
        "FUNCTION",
        "READ",
        "WRITE",
        "NOT",
    ]
    # PASCAL是大小写不敏感语言(?i)
    # 变量类型
    t_REAL = r"(?i)REAL"
    t_VAR = r"(?i)VAR"
    t_BOOLEAN = r"(?i)BOOLEAN"
    t_CONST = r"(?i)CONST"
    t_INTEGER = r"(?i)INTEGER"
    t_CHAR = r"(?i)CHAR"
    t_ARRAY = r"(?i)ARRAY"
    # 赋值
    t_ASSIGNOP = r":="
    t_EQUAL = r"="
    # 不将“ = ”列为关系运算符是考虑到语法分析中的应用
    # 标点符
    t_COLON = r":"
    t_COM = r","
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_POINTTO = "\.\."
    t_POINT = r"\."
    t_SEMICOLON = r";"
    
    t_PROGRAM = r"(?i)PROGRAM"
    t_PROCEDURE = r"(?i)PROCEDURE"
    t_FUNCTION = r"(?i)FUNCTION"
    t_BEGIN = r"(?i)BEGIN"
    t_END = r"(?i)END"
    # 程序控制
    t_IF = r"(?i)IF"
    t_ELSE = r"(?i)ELSE"
    t_THEN = r"(?i)THEN"
    t_FOR = r"(?i)FOR"
    t_DO = r"(?i)DO"
    t_OF = r"(?i)OF"
    t_TO = r"(?i)TO"
    t_WHILE = r"(?i)WHILE"
    t_READ = r"(?i)READ"
    t_WRITE = r"(?i)WRITE"
    t_NOT = r"(?i)NOT"
    # 字符
    t_LETTER = r"\'[a-zA-Z]\'"
    # 忽略\t
    t_ignore = " \t"
    # 关系运算符，乘法运算符，加法运算符
    t_RELOP = r"<=|>=|<>|<|>"

    def t_MULOP(self, t):
        r"(?i)\*|\/|DIV|MOD|AND"
        return t

    def t_ADDOP(self, t):
        r"(?i)\+|-|OR"
        return t

    # 则式匹配COMMENT，更新行号，保存COMMENT内容
    def t_COMMENT(self, t):
        # r"{(?:.|\n)*?}"
        # 匹配左边的 {。
        # 接着匹配零个或多个匹配项，每个匹配项可以是以下两种之一：
        # [^{}]：表示匹配除了 { 和 } 之外的任意字符。也就是匹配单个非括号字符。
        # \{[^{}]*\}：表示匹配以 { 开头、以 } 结尾的一段字符串，中间不能包含 { 和 }。这是一个递归的过程，可以匹配多层的嵌套注释。
        # 最后匹配右边的 }。
        r"\{([^{}]|\{[^{}]*\})*\}"
        self.comment.append({"comment_value": t.value, "lineno": t.lexer.lineno})
        t.lexer.lineno += t.value.count("\n")
        pass

    def t_COMMENT2(self,t):
        r'\(\*(.|\n)*?\*\)'
        self.comment.append({"comment_value": t.value, "lineno": t.lexer.lineno})
        t.lexer.lineno += t.value.count("\n")
        pass

    # 正则式匹配NUM，value值保存为float类型
    def t_NUM(self, t):
        r"\d+\.\d+"
        t.value = float(t.value)
        return t

    # 正则式匹配DIGITS，value值保存为int类型
    def t_DIGITS(self, t):
        r"\d+"
        if int(t.value) > 65535:
            self.error.append(
                {
                    "TYPE": "Lexical Analysis Integer Out of Bounds Error",
                    "info": {
                        "line": t.lineno,
                        "value": [t.value.split("\n")[0]],
                        "lexpos": t.lexpos,
                    },
                }
            )
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r"[0-9a-zA-Z_][a-zA-Z_0-9]*(\.[0-9a-zA-Z_][a-zA-Z_0-9]*)*"
        if t.value.upper() in self.reserved:
            t.type = t.value.upper()
        return t

    # 遇到换行符则行数计数增加
    def t_ignore_newline(self, t):
        r"\n+"
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        self.error.append(
            {
                "code": "Lexical Analysis Illegal Character Error",
                "info": {
                    "line": t.lineno,
                    "value": [t.value.split("\n")[0]],
                    "lexpos": t.lexpos,
                },
            }
        )
        # 错误处理：跳过该错误
        t.lexer.skip(1)


# scanner = Scanner()
# scanner.build()
# fin = "testcodes/1.pas"
# f = open(fin, 'r', encoding='utf-8')
# data = f.read()
# scanner.input(data)
# while True:
#     tok = scanner.token()
#     if not tok:
#         break
#     print(tok)
# print(scanner.comment)
