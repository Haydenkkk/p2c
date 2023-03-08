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

    def input(self, text):
        self.lexer.input(text)

    def token(self):
        return self.lexer.token()

    # literals = "{}()<>=;:,+-*/%&|^"

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
        "RECORD",
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
        "MULOP",
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
        "NOT",
        "BEGIN",
        "SEMICOLON",
        "ADDOP",
        "ID",
    )
    # 定义保留字
    reserved = [
        "REAL",
        "FOR",
        "DO",
        "RECORD",
        "OF",
        "ELSE",
        "CONST",
        "TO",
        "ARRAY",
        "INTEGER",
        "THEN",
        "CHAR",
        "PROCEDURE",
        "WHILE",
        "VAR",
        "BOOLEAN",
        "IF",
        "FUNCTION",
        "END",
        "PROGRAM",
        "READ",
        "WRITE",
        "NOT",
        "BEGIN",
    ]

    # 定义运算符
    reserved_2 = ["DIV", "MOD", "AND", "OR"]

    # 运算符对应的记号属性
    reserved_2_map = {
        "DIV": "MULOP",
        "MOD": "MULOP",
        "AND": "MULOP",
        "OR": "ADDOP",
    }

    # 定义safe的赋值情况，如 INTEGER数据类型的值可以安全地赋值给INTEGER和REAL变量
    safe_assign = {
        "INTEGER": ["INTEGER", "REAL"],
        "REAL": ["REAL"],
        "CHAR": ["CHAR", "INTEGER", "REAL"],
        "BOOLEAN": ["BOOLEAN", "INTEGER", "REAL", "CHAR"],
        "RECORD": ["RECORD"],
    }

    # 定义产生Warning的赋值情况，如 CHAR数据类型的值赋值给BOOLEAN变量时会产生warning
    warn_assign = {
        "INTEGER": ["CHAR", "BOOLEAN"],
        "REAL": ["CHAR", "BOOLEAN", "INTEGER"],
        "CHAR": ["BOOLEAN"],
        "BOOLEAN": [],
        "RECORD": [],
    }
    # 忽略\t
    t_ignore = " \t"
    # 简单token的正则匹配规则
    t_REAL = r"(?i)REAL"  # (?i)大小写不敏感
    t_COLON = r":"
    t_LBRACKET = r"\["
    t_LPAREN = r"\("
    t_ASSIGNOP = r":="
    t_FOR = r"(?i)FOR"
    t_DO = r"(?i)DO"
    t_RECORD = r"(?i)RECORD"
    t_OF = r"(?i)OF"
    t_EQUAL = r"="
    t_ELSE = r"(?i)ELSE"
    t_CONST = r"(?i)CONST"
    t_COM = r","
    t_RPAREN = r"\)"
    t_ARRAY = r"(?i)ARRAY"
    t_INTEGER = r"(?i)INTEGER"
    t_THEN = r"(?i)THEN"
    t_POINTTO = "\.\."
    t_CHAR = r"(?i)CHAR"
    t_MULOP = r"(?i)\*|\/|DIV|MOD|AND"
    t_POINT = r"\."
    t_TO = r"(?i)TO"
    t_PROCEDURE = r"(?i)PROCEDURE"
    t_WHILE = r"(?i)WHILE"
    t_LETTER = r"\'[a-zA-Z]\'"
    t_RELOP = r"<=|>=|<>|<|>"
    t_VAR = r"(?i)VAR"
    t_BOOLEAN = r"(?i)BOOLEAN"
    t_IF = r"(?i)IF"
    t_FUNCTION = r"(?i)FUNCTION"
    t_END = r"(?i)END"
    t_RBRACKET = r"\]"
    t_READ = r"(?i)READ"
    t_WRITE = r"(?i)WRITE"
    t_NOT = r"(?i)NOT"
    t_BEGIN = r"(?i)BEGIN"
    t_SEMICOLON = r";"
    t_ADDOP = r"(?i)\+|-|OR"
    t_PROGRAM = r"(?i)PROGRAM"

    # 则式匹配COMMENT，更新行号，忽略COMMENT内容
    def t_ignore_COMMENT(self, t):
        r"\{.*\}|//.*|\(\*(.|\n)*\*\)"
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
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r"[0-9a-zA-Z_][a-zA-Z_0-9]*(\.[0-9a-zA-Z_][a-zA-Z_0-9]*)*"
        if t.value.upper() in self.reserved:
            t.type = t.value.upper()  # 更改对应保留字的类型
        elif t.value.upper() in self.reserved_2:  # 属于运算符保留字（但不规范）
            t.type = self.reserved_2_map[t.value.upper()]  # 对应规范运算符的类型
        elif "." in t.value:
            # 将ID以.为分界切割，如Book.title切割为Book和title
            t.value = t.value.split(".")
            for i in t.value:
                if t.value[0].isdigit():  # 出现ID以数字开头的错误
                    if not self.error:
                        self.error = []
                    self.error.append(
                        {
                            "code": "A-01",
                            "info": {
                                "line": t.lineno,
                                "value": [t.value.split("\n")[0]],
                                "lexpos": t.lexpos,
                            },
                        }
                    )
                while i[0].isdigit():
                    i = i[1:]  # 错误恢复：如果ID首元素是数字，则去掉该数字
        else:
            if t.value[0].isdigit():  # 出现ID以数字开头的错误
                if not self.error:
                    self.error = []
                self.error.append(
                    {
                        "code": "A-01",
                        "info": {
                            "line": t.lineno,
                            "value": [t.value.split("\n")[0]],
                            "lexpos": t.lexpos,
                        },
                    }
                )
            while t.value[0].isdigit():
                t.value = t.value[1:]  # 错误恢复：如果ID首元素是数字，则去掉该数字
        return t

    def t_ignore_newline(self, t):
        r"\n+"
        t.lexer.lineno += t.value.count("\n")  # 遇到换行符则行数计数增加

    def t_error(self, t):
        if not self.error:
            self.error = []
        self.error.append(
            {  # 不在已有错误中，则为词法分析中的非法字符错误
                "code": "A-02",
                "info": {
                    "line": t.lineno,
                    "value": [t.value.split("\n")[0]],
                    "lexpos": t.lexpos,
                },
            }
        )
        t.lexer.skip(1)  # 错误处理：跳过该错误


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
