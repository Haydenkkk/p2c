import json
from Scanner import Scanner
from ply.yacc import yacc


class pParser(object):
    id = 0
    # error = []
    warning = []
    subSymbol = {}
    # 用于记录当前程序块的符号表信息
    curSymbol = {}
    # 用于记录各个符号在符号表中的位置信息
    symbolMap = {}
    subFuncMap = {}
    SymbolTable = {"constants": [], "variables": [], "subFunc": []}
    inSubFun = False
    parser = None
    lexer = None
    

    def __init__(self):
        self.scanner = Scanner()
        self.scanner.build()
        self.lexer = self.scanner.lexer
        tokens = self.scanner.tokens
        self.error = self.scanner.error
        safe_assign = {
            'INTEGER': ['INTEGER', 'REAL'],
            'REAL': ['REAL'],
            'CHAR': ['CHAR', 'INTEGER', 'REAL'],
            'BOOLEAN': ['BOOLEAN', 'INTEGER', 'REAL', 'CHAR'],
        }

        # 定义产生Warning的赋值情况，如 CHAR数据类型的值赋值给BOOLEAN变量时会产生warning
        warn_assign = {
            'INTEGER': ['CHAR', 'BOOLEAN'],
            'REAL': ['CHAR', 'BOOLEAN', 'INTEGER'],
            'CHAR': ['BOOLEAN'],
            'BOOLEAN': [],
        }

        def report_error(error_code, lineno, values, lexpos, endLexpos=None):
            # Report an error with the specified code, line number, values, and lexical position
            if not self.error:
                self.error = []
            if endLexpos:
                self.error.append(
                    {
                    "code": error_code,
                    "info": {
                        "line": lineno,
                        "value": values,
                        "lexpos": lexpos,
                        "end_lexpos": endLexpos
                        }
                    }
                )
            else:
                self.error.append(
                    {
                    "code": error_code,
                    "info": {
                        "line": lineno,
                        "value": values,
                        "lexpos": lexpos
                        }
                    }
                )

        def get_type(value):
            # Determine the type of the constant
            if type(value) == int:
                return "INTEGER"
            elif type(value) == float:
                return "REAL"
            else:
                return "CHAR"

        def is_positive(value):
            # Check if the value is a positive integer or float
            return type(value) != str and value > 0

        def p_programstruct(p):
            """
            programstruct : program_head SEMICOLON program_body POINT
            """
            # 语法树节点信息，记录上述产生式下非终结符的节点信息，下同
            p[0] = {
                "length": len(p),
                "type": "programstruct",
                "program_head": p[1],
                "program_body": p[3],
            }
            # 符号表信息由 program_body 获取
            self.SymbolTable = {
                "constants": p[3]["SymbolTable"]["constants"],
                "variables": p[3]["SymbolTable"]["variables"],
                "subFunc": p[3]["SymbolTable"]["subFunc"],
            }

        def p_program_head(p):
            """
            program_head : PROGRAM ID LPAREN idlist RPAREN
            """
            p[0] = {
                "length": len(p),
                "type": "program_head",
                "ID": p[2],
                "idlist": p[4],
            }

        def p_program_head_program_id(p):
            """
            program_head : PROGRAM ID
            """
            p[0] = {
                "length": len(p),
                "type": "program_head",
                "ID": p[2],
                "idlist": [],  # 该产生式不含 idlist
            }

        def p_program_body(p):
            """
            program_body : const_declarations var_declarations subprogram_declarations compound_statement
            """
            p[0] = {
                "length": len(p),
                "type": "program_body",
                "const_declarations": p[1],
                "var_declarations": p[2],
                "subprogram_declarations": p[3],
                "compound_statement": p[4],
                # 符号表信息自底向上生成，考虑 const_declarations var_declarations subprogram_declaration 为 ε 的情况
                "SymbolTable":{
                    "constants": p[1]["SymbolTable"] if p[1] else [],
                    "variables": p[2]["SymbolTable"] if p[2] else [],
                    "subFunc": p[3]["SymbolTable"] if p[3] else [],
                }
            }

        def p_idlist(p):
            """
            idlist : idlist COM ID
                    | ID
            """
            symbol_table = self.subSymbol if self.inSubFun else self.curSymbol
            if len(p)==4:
                p[0] = {"length": len(p), "type": "idlist", "ids": p[1]["ids"] + [p[3]]}
                # 在 subSymbol 中已经存在或存在于 curSymbol 中
                if p[3] in list(symbol_table.keys()):
                    report_error("Duplicate lable or redefininy symbol that cannot be redefined.", p.lexer.lineno, [p[3]], p.lexer.lexpos, p.slice[3].lexpos + p.slice[3].lineno - 1 + len(p[3]))
            else:
                p[0] = {"length": len(p), "type": "idlist", "ids": [p[1]]}
                if p[1] in list(symbol_table.keys()):
                    report_error("Duplicate lable or redefininy symbol that cannot be redefined.", p.lexer.lineno, [p[1]], p.lexer.lexpos, p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1]))


        def p_const_declarations(p):
            """
            const_declarations : CONST const_declaration SEMICOLON
                            |
            """
            if len(p) == 4:
                p[0] = {
                    "length": len(p),
                    "type": "const_declarations",
                    "const_declaration": p[2],
                    # 符号表由 产生式右侧 const_declaration 获取
                    "SymbolTable": p[2]["SymbolTable"]
                }
                # 不在子函数中，在 curSymbol 创建一个 map，把 token 作为 key， id 作为 value
                if not self.inSubFun:
                    self.curSymbol = {i["token"]: i["id"] for i in p[0]["SymbolTable"]}
                # 在子函数内部，在 subSymbol 创建同上 map
                else:
                    self.subSymbol.update({i["token"]: i["id"] for i in p[0]["SymbolTable"]})
            else:
                p[0] = None

        def p_const_declaration(p):
            """
            const_declaration : const_declaration SEMICOLON ID EQUAL const_value
            """
            symbol_entry = {
                "id": self.id,
                "token": p[3],
                "type": get_type(p[5]["value"]),
                "value": p[5],
                "positive": is_positive(p[5]["value"]),
            }
            # 将 ID const_value 加入symbolMap，self.id 为 key，通过 id 直接获取符号表信息
            self.symbolMap[self.id] = symbol_entry
            self.id += 1
            # 判断Duplicate lable or redefininy symbol that cannot be redefined.
            if self.inSubFun and p[3] in list(self.subSymbol.keys()):
                report_error("Duplicate lable or redefininy symbol that cannot be redefined.", p.lexer.lineno, [p[3]], p.lexer.lexpos)
            elif not self.inSubFun and p[3] in list(self.curSymbol.keys()):
                report_error("Duplicate lable or redefininy symbol that cannot be redefined.", p.lexer.lineno, [p[3]], p.lexer.lexpos)
            p[0] = {
                "length": len(p),
                "id": self.id,
                "type": "const_declaration",
                "values": p[1]["values"] + [{"ID": p[3], "const_value": p[5]}],
                 # 符号表由 产生式右侧 const_declaration 、 ID 与 const_value 获取
                "SymbolTable": p[1]["SymbolTable"] + [symbol_entry]
            }

        def p_const_declaration_id(p):
            """
            const_declaration : ID EQUAL const_value
            """
            symbol_entry = {
                "id": self.id,
                "token": p[1],
                "type": get_type(p[3]["value"]),
                "value": p[3],
                "positive": is_positive(p[3]["value"]),
            }
            self.symbolMap[self.id] = symbol_entry
            self.id += 1
            # 判断是否重复定义
            if (self.inSubFun and p[1] in self.subSymbol.keys()) or (not self.inSubFun and p[1] in self.curSymbol.keys()):
                report_error("Duplicate lable or redefininy symbol that cannot be redefined.", p.lexer.lineno, [p[1]], p.lexer.lexpos)
            p[0] = {
                "length": len(p),
                "id": self.id,
                "type": "const_declaration",
                "values": [{"ID": p[1], "const_value": p[3]}],
                "SymbolTable": [symbol_entry]
            }
            
        def p_const_value_addop(p):
            """
            const_value : ADDOP NUM
                        | ADDOP DIGITS
            """
            p[0] = {
                "length": len(p),
                "type": "const_value",
                "_type": "NUM",
                "value": p[2] if p[1] == "+" else -p[2],
            }

        def p_const_value(p):
            """
            const_value : NUM
                        | DIGITS
            """
            p[0] = {
                "length": len(p),
                "type": "const_value",
                "_type": "NUM",
                "value": p[1],
            }

        def p_const_value_letter(p):
            """
            const_value : LETTER
            """
            p[0] = {
                "length": len(p),
                "type": "const_value",
                "_type": "LETTER",
                "value": p[1].replace("'", ""),
            }

        def p_var_declarations(p):
            """
            var_declarations : VAR var_declaration SEMICOLON
                            |
            """
            
            # var_declarations -> ε
            if len(p) != 4:
                p[0] = None
            # var_declarations -> var var_declaration ;
            else:
                p[0] = {
                    "length": len(p),
                    "type": "var_declarations",
                    "var_declaration": p[2]
                }
                # 构建符号表
                p[0]["SymbolTable"] = p[2]["SymbolTable"]
                # 如果不在子函数内，添加到当前符号表内
                if not self.inSubFun:
                    for i in p[0]["SymbolTable"]:
                        self.curSymbol[i["token"]] = i["id"]
                else:
                    for i in p[0]["SymbolTable"]:
                        self.subSymbol[i["token"]] = i["id"]
        
        def p_var_declaration(p):
            """
            var_declaration : var_declaration SEMICOLON idlist COLON type
                            | idlist COLON type
            """
            # 产生式1 var_declaration -> var_declaration ; idlist : type
            if len(p) == 6:
                p[0] = {
                    "length": len(p),
                    "type": "var_declaration",
                    "values": p[1]["values"] + [{"idlist": p[3], "type": p[5]}],
                }
                # 构造符号表
                p[0]["SymbolTable"] = p[1]["SymbolTable"]
                # 遍历 idlist，把每一个标识符加入符号表
                for i in p[3]["ids"]:
                    symbol_entry = { 
                            "id": self.id,
                            "token": i,
                            "type": p[5]["SymbolTable"]["type"],
                            "isArray": p[5]["SymbolTable"]["isArray"],
                            "dimension": p[5]["SymbolTable"]["dimension"],
                            "size": p[5]["SymbolTable"]["size"],
                            "start": p[5]["SymbolTable"]["start"],
                        }
                    p[0]["SymbolTable"] += [symbol_entry]
                    # 加入 symbolmap
                    self.symbolMap[self.id] = symbol_entry
            # 产生式2 var_declaration -> idlist : type
            else:
                p[0] = {
                    "length": len(p),
                    "id": self.id,
                    "type": "var_declaration",
                    "values": [{"idlist": p[1], "type": p[3]}],
                }
                p[0]["SymbolTable"] = []
                for i in p[1]["ids"]:
                    symbol_entry = { 
                            "id": self.id,
                            "token": i,
                            "type": p[3]["SymbolTable"]["type"],
                            "isArray": p[3]["SymbolTable"]["isArray"],
                            "dimension": p[3]["SymbolTable"]["dimension"],
                            "size": p[3]["SymbolTable"]["size"],
                            "start": p[3]["SymbolTable"]["start"],
                        }
                    p[0]["SymbolTable"] += [symbol_entry]
                    self.symbolMap[self.id] = symbol_entry
            self.id += 1

        def p_type(p):
            """
            type : basic_type
                | ARRAY LBRACKET period RBRACKET OF basic_type
            """
            # type->array[period] of basic_type
            if not type(p[1]) == dict and p[1].upper() == "ARRAY":
                p[0] = {
                    "length": len(p),
                    "type": "type",
                    "_type": "ARRAY",
                    "period": p[3],
                    "basic_type": p[6],
                }
                p[0]["SymbolTable"] = {
                    "type": p[6]["SymbolTable"],
                    "isArray": True,
                    "dimension": p[3]["SymbolTable"]["dimension"],
                    "size": p[3]["SymbolTable"]["size"],
                    "start": p[3]["SymbolTable"]["start"],
                }
            # type->basic_type
            else:
                p[0] = {"length": len(p),
                        "type": "type",
                        "_type": p[1]}
                p[0]["SymbolTable"] = {
                    "type": p[1]["SymbolTable"],
                    "isArray": False,
                    "dimension": 0,
                    "size": [],
                    "start": [],
                }

        def p_basic_type(p):
            """
            basic_type : INTEGER
                        | REAL
                        | BOOLEAN
                        | CHAR
            """
            p[0] = {"type": "basic_type",
                    "_type": p[1].upper()}
            p[0]["SymbolTable"] = p[1].upper()

        def p_period(p):  # 数组
            """
            period : period COM DIGITS POINTTO DIGITS
                    | DIGITS POINTTO DIGITS
            """
            # period -> period , digits ..Digits
            if len(p) == 6:
                # 错误判断
                if p[3] > p[5]:
                    report_error("The array subscript lower bound exceeds the upper bound", 
                                 p.slice[3].lineno, [p[3], p[5]], p.slice[3].lineno + p.slice[3].lexpos - 1, p.slice[5].lineno + p.slice[5].lexpos + len(str(p[5])))
                p[0] = {
                    "length": len(p),
                    "type": "period",
                    "values": p[1]["values"] + [{"start": p[3], "end": p[5]}],
                    "SymbolTable":{
                        "dimension": p[1]["SymbolTable"]["dimension"] + 1,  # 数组维度
                        "size": p[1]["SymbolTable"]["size"] + [p[5] - p[3] + 1],
                        "start": p[1]["SymbolTable"]["start"] + [p[3]],
                    }
                }
            # 产生式2 period -> digits .. digits
            else:
                if p[1] > p[3]:
                    report_error("The array subscript lower bound exceeds the upper bound", 
                                 p.slice[1].lineno, [p[1], p[3]], p.slice[1].lineno + p.slice[1].lexpos - 1, p.slice[3].lineno + p.slice[3].lexpos + len(str(p[3])))
                p[0] = {
                    "length": len(p),
                    "type": "period",
                    "values": [{"start": p[1], "end": p[3]}],
                    "SymbolTable":{
                        "dimension": 1,
                        "size": [p[3] - p[1] + 1],
                        "start": [p[1]],
                    }
                }

        def p_subprogram_declarations(p):
            """
            subprogram_declarations : subprogram_declarations subprogram SEMICOLON
                                    |
            """
            self.inSubFun = False
            #  subprogram_declarations -> subprogram_declarations subprogram ;
            if len(p) == 4:
                p[0] = {
                    "length": len(p),
                    "type": "subprogram_declarations",
                    "subprograms": p[1]["subprograms"] + [p[2]],
                }
                # 符号表由产生式右侧生成
                p[0]["SymbolTable"] = p[1]["SymbolTable"] + [p[2]["SymbolTable"]]
            # subprogram_declarations -> ε
            else:
                p[0] = {
                    "length": len(p),
                    "type": "subprogram_declarations",
                    "subprograms": [],
                }
                p[0]["SymbolTable"] = []

        def p_subprogram(p):
            """
            subprogram : subprogram_head SEMICOLON subprogram_body
            """
            p[0] = {
                "length": len(p),
                "id": p[1]["SymbolTable"]["id"],
                "type": "subprogram",
                "subprogram_head": p[1],
                "subprogram_body": p[3],
            }
            # 构造符号表
            p[0]["SymbolTable"] = {
                "id": p[1]["SymbolTable"]["id"],
                "token": p[1]["SymbolTable"]["token"],
                "type": p[1]["SymbolTable"]["type"],
                "table": {
                    "params": p[1]["SymbolTable"]["params"],
                        "references": p[1]["SymbolTable"]["references"],
                        "constants": p[3]["SymbolTable"]["constants"],
                        "variables": p[1]["SymbolTable"]["variables"]
                        + p[3]["SymbolTable"]["variables"]
                        if p[1]["SymbolTable"]["variables"]
                        else p[3]["SymbolTable"]["variables"],
                    }
            }

        def p_into_procedure(p):
            """
            into_procedure :
            """
            self.inSubFun = True
            self.subSymbol = {}

        def p_into_function(p):
            """
            into_function :
            """
            self.inSubFun = True
            self.subSymbol = {}

        def p_subprogram_head(p):
            """
            subprogram_head : into_procedure PROCEDURE ID formal_parameter
                            | into_function FUNCTION ID formal_parameter COLON basic_type
            """
            # subprogram_head -> into_procedure procedure id formal_parameter
            if not type(p[2]) == dict and p[2].upper() == "PROCEDURE":
                p[0] = {
                    "length": len(p),
                    "type": "subprogram_head",
                    "_type": "PROCEDURE",
                    "ID": p[3],
                    "formal_parameter": p[4],
                }
                # 子过程符号表
                p[0]["SymbolTable"] = {
                    "id": self.id,
                    "token": p[3],
                    "type": None,
                    "params": p[4]["SymbolTable"]["params"]
                    if p[4] is not None
                    else None,
                    "references": p[4]["SymbolTable"]["references"]
                    if p[4] is not None
                    else None,
                    "variables": p[4]["SymbolTable"]["variables"]
                    if p[4] is not None
                    else None,
                }
                # 添加到符号表中
                self.symbolMap[self.id] = {
                    "id": self.id,
                    "token": p[3],
                    "type": None,
                    "params": p[4]["SymbolTable"]["params"]
                    if p[4] is not None
                    else None,
                    "references": p[4]["SymbolTable"]["references"]
                    if p[4] is not None
                    else None,
                    "variables": p[4]["SymbolTable"]["variables"]
                    if p[4] is not None
                    else None,
                }
                # 子函数列表
                self.subSymbol = {p[3]: self.id}
                # 更新subFuncMap
                self.subFuncMap[p[3]] = {
                    "type": None,
                    "params": p[4]["SymbolTable"]["params"]
                    if p[4] is not None
                    else None,
                    "variables": p[4]["SymbolTable"]["variables"]
                    if p[4] is not None
                    else None,
                    "references": p[4]["SymbolTable"]["references"]
                    if p[4] is not None
                    else None,
                }
                self.id += 1
            #  subprogram_head -> into_function function id formal_parameter : basic_type
            elif not type(p[2]) == dict and p[2].upper() == "FUNCTION":
                p[0] = {
                    "length": len(p),
                    "type": "subprogram_head",
                    "_type": "FUNCTION",
                    "ID": p[3],
                    "formal_parameter": p[4],
                    "basic_type": p[6],
                }
                #  子函数过程表
                p[0]["SymbolTable"] = {
                    "id": self.id,
                    "token": p[3],
                    "type": p[6]["SymbolTable"],
                    "params": p[4]["SymbolTable"]["params"]
                    if p[4] is not None
                    else None,
                    "references": p[4]["SymbolTable"]["references"]
                    if p[4] is not None
                    else None,
                    "variables": p[4]["SymbolTable"]["variables"]
                    if p[4] is not None
                    else None,
                }
                self.symbolMap[self.id] = {
                    "id": self.id,
                    "token": p[3],
                    "type": p[6]["SymbolTable"],
                    "params": p[4]["SymbolTable"]["params"]
                    if p[4] is not None
                    else None,
                    "references": p[4]["SymbolTable"]["references"]
                    if p[4] is not None
                    else None,
                    "variables": p[4]["SymbolTable"]["variables"]
                    if p[4] is not None
                    else None,
                }
                self.subSymbol = {p[3]: self.id}
                self.subFuncMap[p[3]] = {
                    "type": p[6]["SymbolTable"],
                    "variables": p[4]["SymbolTable"]["variables"]
                    if p[4] is not None
                    else None,
                    "references": p[4]["SymbolTable"]["references"]
                    if p[4] is not None
                    else None,
                }
                self.id += 1

            if p[0]["SymbolTable"]["variables"] is not None:
                for i in p[0]["SymbolTable"]["variables"]:
                    self.subSymbol[i["token"]] = i["id"]

        def p_formal_parameter(p):
            """
            formal_parameter : LPAREN parameter_list RPAREN
                            |
            """
            # 产生式1 formal_parameter -> ( parameter_list )
            if len(p) == 4:
                p[0] = {
                    "length": len(p),
                    "type": "formal_parameter",
                    "parameter_list": p[2],
                }
                p[0]["SymbolTable"] = {
                    "params": p[2]["SymbolTable"]["params"],
                    "references": p[2]["SymbolTable"]["references"],
                    "variables": p[2]["SymbolTable"]["variables"],
                }
            # 产生式2 formal_parameter -> ε
            else:
                p[0] = None

        def p_parameter_list(p):
            """
            parameter_list : parameter_list SEMICOLON parameter
                        | parameter
            """
            # parameter_list -> parameter_list ; parameter
            if len(p) == 4:
                p[0] = {
                    "length": len(p),
                    "type": "parameter_list",
                    "parameters": p[1]["parameters"] + [p[3]],
                }

                p[0]["SymbolTable"] = {
                    "params": p[1]["SymbolTable"]["params"]
                    + p[3]["SymbolTable"]["size"],
                    "references": p[1]["SymbolTable"]["references"]
                    + p[3]["SymbolTable"]["references"],
                    "variables": p[1]["SymbolTable"]["variables"]
                    + p[3]["SymbolTable"]["variables"],
                }
            # parameter_list -> parameter
            else:
                p[0] = {
                    "length": len(p),
                    "type": "parameter_list",
                    "parameters": [p[1]],
                }
                p[0]["SymbolTable"] = {
                    "params": p[1]["SymbolTable"]["size"],
                    "references": p[1]["SymbolTable"]["references"],
                    "variables": p[1]["SymbolTable"]["variables"],
                }

        def p_parameter(p):
            """
            parameter : var_parameter
                    | value_parameter
            """
            p[0] = {"length": len(p),
                    "type": "parameter",
                    "value": p[1]}
            p[0]["SymbolTable"] = p[1]["SymbolTable"]

        def p_var_parameter(p):
            """
            var_parameter : VAR value_parameter
            """
            # 引用调用
            p[0] = {"length": len(p),
                    "type": "var_parameter",
                    "value_parameter": p[2]
                    }
            p[0]["SymbolTable"] = {

                "references": [True for i in range(p[2]["SymbolTable"]["size"])],
                "variables": p[2]["SymbolTable"]["variables"],
                "size": p[2]["SymbolTable"]["size"],
            }

        def p_value_parameter(p):
            """
            value_parameter : idlist COLON basic_type
            """
            p[0] = {
                "length": len(p),
                "type": "value_parameter",
                "idlist": p[1],
                "basic_type": p[3],
            }
            # value_parameter的符号表
            p[0]["SymbolTable"] = {
                # 传值调用
                "references": [False for i in range(len(p[1]["ids"]))],
                "size": len(p[1]["ids"]),  # size为id数量
                "variables": [],
            }
            # 添加新的参数变量
            for i in p[1]["ids"]:  # 遍历idlist中的每个id
                p[0]["SymbolTable"]["variables"] = p[0]["SymbolTable"]["variables"] + [
                    {
                        "id": self.id,
                        "token": i,
                        "type": p[3]["SymbolTable"],
                        "isArray": False,
                        "dimension": 0,
                        "size": [],
                        "start": [],
                    }
                ]
                # 更新符号表
                self.symbolMap[self.id] = {
                    "id": self.id,
                    "token": i,
                    "type": p[3]["SymbolTable"],
                    "isArray": False,
                    "dimension": 0,
                    "size": [],
                    "start": [],
                }
                self.id += 1

        def p_subprogram_body(p):
            """
            subprogram_body : const_declarations var_declarations compound_statement
            """
            p[0] = {
                "length": len(p),
                "type": "subprogram_body",
                "const_declarations": p[1],
                "var_declarations": p[2],
                "compound_statement": p[3],
            }
            p[0]["SymbolTable"] = {
                "constants": p[1]["SymbolTable"] if p[1] else [],
                "variables": p[2]["SymbolTable"] if p[2] else [],
            }

        def p_compound_statement(p):
            """
            compound_statement : BEGIN statement_list END
            """
            p[0] = {
                "length": len(p),
                "type": "compound_statement",
                "statement_list": p[2]
            }

        def p_statement_list(p):
            """
            statement_list : statement_list SEMICOLON statement
                        | statement
            """
            if len(p) == 4:
                # statement_list -> statement_list SEMICOLON statement
                p[0] = {
                    "length": len(p),
                    "type": "statement_list",
                    "statements": p[1]["statements"] + [p[3]]
                }
            else:
            # statement_list -> statement
                p[0] = {
                    "length": len(p),
                    "type": "statement_list",
                    "statements": [p[1]]
                }

        def p_statement(p):
            '''
            statement : variable ASSIGNOP expression
                    | procedure_call
                    | compound_statement
                    | IF expression THEN statement else_part
                    | FOR ID ASSIGNOP expression TO expression DO statement
                    | READ LPAREN variable_list  RPAREN
                    | WRITE LPAREN expression_list RPAREN
                    | WHILE expression DO statement
                    | 
            '''
            if len(p) == 1:  # statement为空
                p[0] = None
            # statement : IF expression THEN statement else_part
            elif not type(p[1]) == dict and p[1].upper() == 'IF':
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "IF",
                    "expression": p[2],
                    "statement": p[4],
                    "else_part": p[5]
                }
            # statement : FOR ID ASSIGNOP expression TO expression DO statement
            elif not type(p[1]) == dict and p[1].upper() == 'FOR':
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "FOR",
                    "ID": p[2],
                    "ASSIGNOP": p[3],
                    "expression": p[4],
                    "to_expression": p[6],
                    "statement": p[8]
                }
                if p[2] not in list(self.curSymbol.keys()) and self.inSubFun and p[2] not in list(self.subSymbol.keys()):
                    # ID既不在当前符号表，也不在子函数符号表，变量未定义
                    report_error("Assigning values to undefined variables",p.lexer.lineno,[p[2]],p.lexer.lexpos) # 错误类型：给未定义的变量赋值
                id = self.search_symbol(p[2])
                if id:
                    if p[4]["__type"] == "UNDEFINED":  # expression未定义
                        report_error("Assigning values using undefined variables",p.lexer.lineno,[p[2]],p.lexer.lexpos) # 错误类型：使用未定义的变量进行赋值
                    elif not p[4]["__type"] or id["type"] not in safe_assign[p[4]["__type"]]:  # 不是安全赋值类型
                        if p[4]["__type"] and id["type"] in warn_assign[p[4]["__type"]]:  # 属于warn复制类型
                            if not self.warning:
                                self.warning = []
                            self.warning += [{
                                "code": "变量赋值类型不匹配",
                                "info": {
                                    "line": p.slice[3].lineno,
                                    "value": [p[2], id["type"], p[4]["__type"]],
                                    "lexpos": p.slice[3].lexpos + p.slice[3].lineno - 1
                                }
                            }]  # 警告类型：变量赋值类型不匹配，转换可能造成数据丢失
                        else:  # 错误赋值
                            report_error("The variable assignment type does not match and cannot be converted",p.slice[3].lineno, [p[2], id["type"] if id["type"] else "VOID", p[4]["__type"] if p[4]["__type"] else "VOID"],p.slice[3].lexpos + p.slice[3].lineno - 1)
                            # 错误类型：变量赋值类型不匹配，且不能转换
            #  statement : READ LPAREN variable_list  RPAREN
            elif not type(p[1]) == dict and p[1].upper() == 'READ':
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "READ",
                    "variable_list": p[3]
                }
            #  statement : WRITE LPAREN expression_list RPAREN
            elif not type(p[1]) == dict and p[1].upper() == 'WRITE':
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "WRITE",
                    "expression_list": p[3]
                }
            #  statement : WHILE expression DO statement
            elif not type(p[1]) == dict and p[1].upper() == 'WHILE':
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "WHILE",
                    "expression": p[2],
                    "statement": p[4]
                }
            #  statement : variable ASSIGNOP expression
            elif p[1]["type"] == "variable":
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "variable",
                    "variable": p[1],
                    "ASSIGNOP": p[2],
                    "expression": p[3]
                }
                if p[1]["__type"] == "UNDEFINED":  # variable未定义
                    report_error("Assigning values to undefined variables",p.lexer.lineno,[p[1]["ID"]],p.lexer.lexpos) # 错误类型：给未定义的变量赋值
                id = self.search_symbol(p[1]["ID"])  # 获取变量id
                if p[3]["__type"] == "UNDEFINED":  # expression未定义
                    report_error("Assigning values using undefined variables",p.lexer.lineno, [p[1]["ID"]],p.lexer.lexpos) # 错误类型：使用未定义的变量进行赋值
                elif id:  # 找到id
                    if not p[3]["__type"] or id["type"] not in safe_assign[p[3]["__type"]]:
                        if p[3]["__type"] and id["type"] in warn_assign[p[3]["__type"]]:
                            if not self.warning:
                                self.warning = []
                            self.warning += [{
                                "code": "变量赋值类型不匹配",
                                "info": {
                                    "line": p.slice[2].lineno,
                                    "value": [p[1]["ID"], id["type"], p[3]["__type"]],
                                    "lexpos": p.slice[2].lexpos + p.slice[2].lineno - 1
                                }
                            }]  # 警告类型：变量赋值类型不匹配，转换可能造成数据丢失
                        else:
                            report_error("The variable assignment type does not match and cannot be converted",p.slice[2].lineno,[p[1]["ID"], id["type"] if id["type"] else "VOID", p[3]["__type"] if p[3]["__type"] else "VOID"], p.slice[2].lexpos + p.slice[2].lineno - 1)
                            # 错误类型：变量赋值类型不匹配，且不能转换
                else:
                    report_error("Assigning values to undefined variables",p.lexer.lineno, [p[1]["ID"]],p.lexer.lexpos) # 错误类型：给未定义的变量赋值
            elif p[1]["type"] == "procedure_call":
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "procedure_call",
                    "procedure_call": p[1]
                }
            #  statement : compound_statement
            elif p[1]["type"] == "compound_statement":
                p[0] = {
                    "length": len(p),
                    "type": "statement",
                    "_type": "compound_statement",
                    "compound_statement": p[1]
                }
            else:
                p[0] = None  # 兼容其他可能出现的错误

        def p_variable_list(p):
            '''
            variable_list : variable_list COM variable
                        | variable
            '''
            if len(p) == 4:  # variable_list : variable_list COM variable
                p[0] = {
                    "length": len(p),
                    "type": "variable_list",
                    # 判断p[3]是否为None
                    "variables": p[1]["variables"] + [p[3]] if p[3] else p[1]["variables"]
                }
            else:  # variable_list : variable
                p[0] = {
                    "length": len(p),
                    "type": "variable_list",
                    "variables": [p[1]]
                }

        def p_variable(p):
            '''
            variable : ID id_varpart
            '''
            p[0] = {
                "length": len(p),
                "type": "variable",
                # ID类型
                "__type": self.search_symbol(p[1])["type"] if self.search_symbol(p[1]) else "UNDEFINED",
                "ID": p[1],
                "id_varpart": p[2]
            }
            if type(p[1]) == str and p[1] not in list(self.curSymbol.keys()) and not (self.inSubFun and p[1] in list(self.subSymbol.keys())):
                # 如果ID是字符串但未定义
                report_error("The variable used is not defined (variable identifier)",p.slice[1].lineno,[p[1]],p.slice[1].lexpos + p.slice[1].lineno - 1, p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1]))
                # 错误类型：使用的变量未定义（变量标识符）

        def p_id_varpart(p):
            '''
            id_varpart : LBRACKET expression_list RBRACKET
                       | 
            '''
            if len(p) == 4:
                p[0] = {
                    "length": len(p),
                    "type": "id_varpart",
                    "expression_list": p[2]  # 规约expression_list
                }
            else:  # id_varpart为空，没有表达式
                p[0] = None

        def p_procedure_call(p):
            '''
            procedure_call : ID
                           | ID LPAREN expression_list RPAREN
            '''
            if len(p) == 2:  # procedure_call : ID
                p[0] = {
                    "length": len(p),
                    "type": "procedure_call",
                    "ID": p[1]
                }
                if self.subFuncMap[p[1]]["type"]:
                    report_error("Mismatched number of variables during function call",p.slice[1].lineno, ["0", len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else [])],p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1]))
                #"函数调用时变量个数不匹配
            else:  # procedure_call : ID LPAREN expression_list RPAREN
                p[0] = {
                    "length": len(p),
                    "type": "procedure_call",
                    "ID": p[1],
                    "expression_list": p[3]
                }
                if len(p[3]["__type"]) != len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else []):  # 变量数量不一致
                    report_error("Mismatched number of variables during function call",p.slice[1].lineno,[len(p[3]["__type"]), len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else [])],p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                 #错误类型：函数调用时变量个数不匹配
                else:  # 函数调用时变量数量一致
                    for i in range(len(p[3]["__type"])):  # 遍历expression_list
                        from_type = p[3]["__type"][i]
                        to_type = self.subFuncMap[p[1]]["variables"][i]["type"]
                        if from_type == "UNDEFINED":
                            report_error("Parameter undefined during function call",p.slice[1].lineno,[from_type, to_type],p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                        # 错误类型：函数调用时参数未定义
                        elif to_type not in safe_assign[from_type]:  # 不属于安全赋值类型
                            if to_type in warn_assign[from_type]:  # 属于warn赋值类型
                                if not self.warning:
                                    self.warning = []
                                self.warning += [{
                                    "code": "函数调用时参数类型不匹配",
                                    "info": {
                                        "line": p.lexer.lineno,
                                        "value": [self.subFuncMap[p[1]]["variables"][i]['token'], from_type, to_type],
                                        "lexpos": p.lexer.lexpos
                                    }
                                }]  # 警告类型：函数调用时参数类型不匹配，转换可能造成数据丢失
                            else:  # 错误复制类型
                                report_error("Parameter type mismatch during function call",p.slice[1].lineno,[self.subFuncMap[p[1]]["variables"][i]['token'], from_type, to_type],p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                        # 错误类型：函数调用时参数类型不匹配，且不能转换
                        if self.subFuncMap[p[1]]["references"][i] and not (p[3]["expressions"] and p[3]["expressions"][i] and p[3]["expressions"][i]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["_type"] == "variable"):
                            # 判断函数的传参是否正确（expression/variable）
                            report_error("An expression that cannot be referenced was used during the reference call",p.slice[1].lineno,"",p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))#无法翻译错误：引用调用时使用了无法引用的表达式

        def p_else_part(p):
            '''
            else_part : ELSE statement
                      | 
            '''
            if len(p) == 3:  # else_part : ELSE statement
                p[0] = {
                    "length": len(p),
                    "type": "else_part",
                    "statement": p[2]
                }
            else:  # else_part为空
                p[0] = {
                    "length": len(p),
                    "type": "else_part",
                    "statement": None
                }

        def p_expression_list(p):
            '''
            expression_list : expression_list COM expression
                            | expression
            '''
            if len(p) == 4:  # expression_list : expression_list COM expression
                p[0] = {
                    "length": len(p),
                    "type": "expression_list",
                    "__type": p[1]["__type"] + [p[3]["__type"] if p[3] else None],
                    "expressions": p[1]["expressions"] + [p[3]] if p[3] else p[1]["expressions"]
                }
            else:  # expression_list : expression
                p[0] = {
                    "length": len(p),
                    "type": "expression_list",
                    "__type": [p[1]["__type"]],
                    "expressions": [p[1]]
                }

        def p_expression(p):
            '''
            expression : simple_expression RELOP simple_expression
                       | simple_expression
            '''
            if len(p) == 4:  # expression : simple_expression RELOP simple_expression
                p[0] = {
                    "length": len(p),
                    "type": "expression",
                    "__type": "BOOLEAN",
                    "simple_expression_1": p[1],
                    "RELOP": p[2],
                    "simple_expression_2": p[3]
                }
                # simple_expression中的标识符未定义
                if p[1]["__type"] == "UNDEFINED" or p[3]["__type"] == "UNDEFINED":
                    report_error("Compare undefined variables",p.lexer.lineno,"",p.lexer.lexpos)
                # simple_expression中的标识符类型为RECODRD
            else:  # expression : simple_expression
                p[0] = {
                    "length": len(p),
                    "type": "expression",
                    "__type": p[1]["__type"],
                    "simple_expression": p[1]
                }

        def p_expression_equal(p):
            '''
            expression : simple_expression EQUAL simple_expression
            '''
            p[0] = {
                "length": len(p),
                "type": "expression",
                "simple_expression_1": p[1],
                "RELOP": p[2],
                "simple_expression_2": p[3]
            }

        def p_simple_expression(p):
            '''
            simple_expression : simple_expression ADDOP term
                              | term
            '''
            if len(p) == 4:  # simple_expression : simple_expression ADDOP term
                p[0] = {
                    "length": len(p),
                    "type": "simple_expression",
                    "simple_expression": p[1],
                    "ADDOP": p[2],
                    "term": p[3]
                }
                # simple_expression或term中标识符未定义
                if p[1]["__type"] == "UNDEFINED" or p[3]["__type"] == "UNDEFINED":
                    report_error("Performing operations on undefined variables",p.lexer.lineno,"",p.lexer.lexpos) # 错误类型：对未定义的变量进行运算
                    p[0]["__type"] = "UNDEFINED"
                # simple_expression或term中标识符为其它类型
                elif p[1]["__type"] == "REAL" or p[3]["__type"] == "REAL":
                    p[0]["__type"] = "REAL"
                elif p[1]["__type"] == "INTEGER" or p[3]["__type"] == "INTEGER":
                    p[0]["__type"] = "INTEGER"
                elif p[1]["__type"] == "CHAR" or p[3]["__type"] == "CHAR":
                    p[0]["__type"] = "CHAR"
                elif p[1]["__type"] == "BOOLEAN" or p[3]["__type"] == "BOOLEAN":
                    p[0]["__type"] = "BOOLEAN"
                else:
                    report_error("Unknown type of operation",p.lexer.lineno,[p[1]["__type"], p[3]["__type"]], p.lexer.lexpos) # 错误类型：未知类型的运算
                    p[0]["__type"] = "UNDEFINED"
            else:  # simple_expression : term
                p[0] = {
                    "length": len(p),
                    "type": "simple_expression",
                    "__type": p[1]["__type"],
                    "term": p[1]
                }

        def p_term(p):
            '''
            term : term MULOP factor
                 | factor
            '''
            if len(p) == 4:  # term : term MULOP factor
                p[0] = {
                    "length": len(p),
                    "type": "term",
                    "term": p[1],
                    "MULOP": p[2],
                    "factor": p[3]
                }
                if p[1]["__type"] == "UNDEFINED" or p[3]["__type"] == "UNDEFINED":  # term或factor中标识符未定义
                    report_error("Performing operations on undefined variables", p.lexer.lineno,"",p.lexer.lexpos) # 错误类型：对未定义的变量进行运算
                    p[0]["__type"] = "UNDEFINED"
                # 标识符为其它类型
                elif p[1]["__type"] == "REAL" or p[3]["__type"] == "REAL":
                    p[0]["__type"] = "REAL"
                elif p[1]["__type"] == "INTEGER" or p[3]["__type"] == "INTEGER":
                    p[0]["__type"] = "INTEGER"
                elif p[1]["__type"] == "CHAR" or p[3]["__type"] == "CHAR":
                    p[0]["__type"] = "CHAR"
                elif p[1]["__type"] == "BOOLEAN" or p[3]["__type"] == "BOOLEAN":
                    p[0]["__type"] = "BOOLEAN"
                else:
                    report_error("Unknown type of operation",p.lexer.lineno,[p[1]["__type"], p[3]["__type"]],p.lexer.lexpos) # 错误类型：未知类型的运算
                    p[0]["__type"] = "UNDEFINED"
            else:  # term : factor
                p[0] = {
                    "length": len(p),
                    "type": "term",
                    "__type": p[1]["__type"],
                    "factor": p[1]
                }

        def p_factor_num(p):
            '''
            factor : NUM
                   | DIGITS
            '''
            p[0] = {
                "length": len(p),
                "type": "factor",
                "_type": "NUM",
                "__type": "INTEGER" if type(p[1]) == int else "REAL",  # 整数/小数
                "NUM": p[1]
            }

        def p_factor_variable(p):
            '''
            factor : variable
            '''
            p[0] = {
                "length": len(p),
                "type": "factor",
                "_type": "variable",
                "__type": p[1]["__type"],  # variable的类型
                "variable": p[1]
            }

        def p_factor_procedure_id(p):
            '''
            factor : ID LPAREN expression_list RPAREN
            '''
            p[0] = {
                "length": len(p),
                "type": "factor",
                "_type": "procedure_id",
                "__type": self.subFuncMap[p[1]]["type"],
                "ID": p[1],
                "expression_list": p[3]
            }
            if len(p[3]["__type"]) != len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else []):  # 变量数量不一致
                report_error("Mismatched number of variables during function call",p.slice[1].lineno, [len(p[3]["__type"]), len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else [])],p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                # 错误类型：函数调用时变量个数不匹配
            else:  # 函数调用时变量数量一致
                for i in range(len(p[3]["__type"])):  # 遍历expression_list
                    from_type = p[3]["__type"][i]
                    to_type = self.subFuncMap[p[1]]["variables"][i]["type"]
                    if from_type == "UNDEFINED":
                        report_error("Parameter undefined during function call",p.slice[1].lineno,[from_type, to_type],p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                        # 错误类型：函数调用时参数未定义
                    elif to_type not in safe_assign[from_type]:  # 不属于安全赋值类型
                        if to_type in warn_assign[from_type]:  # 属于warn赋值类型
                            if not self.warning:
                                self.warning = []
                            self.warning += [{
                                "code": "函数调用时参数类型不匹配",
                                "info": {
                                    "line": p.lexer.lineno,
                                    "value": [self.subFuncMap[p[1]]["variables"][i]['token'], from_type, to_type],
                                    "lexpos": p.lexer.lexpos
                                }
                            }]  # 错误类型：函数调用时参数类型不匹配，转换可能造成数据丢失
                        else:  # 错误复制类型
                            report_error("Parameter type mismatch during function call",p.slice[1].lineno,[self.subFuncMap[p[1]]["variables"][i]['token'], from_type, to_type],p.slice[1].lexpos + p.slice[1].lineno - 1, p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                            # 错误类型：函数调用时参数类型不匹配，且不能转换
                    if self.subFuncMap[p[1]]["references"][i] and not (p[3]["expressions"] and p[3]["expressions"][i] and p[3]["expressions"][i]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["_type"] == "variable"):
                        # 判断函数的传参是否正确（expression/variable）
                        report_error("An expression that cannot be referenced was used during the reference call",p.slice[1].lineno,"",p.slice[1].lexpos + p.slice[1].lineno - 1,p.slice[4].lexpos + p.slice[4].lineno + len(p[4]))
                       # 无法翻译错误：引用调用时使用了无法引用的表达式

        def p_factor_expression(p):
            '''
            factor : LPAREN expression RPAREN
            '''
            p[0] = {
                "length": len(p),
                "type": "factor",
                "_type": "expression",
                "__type": p[2]["__type"],
                "expression": p[2]
            }

        def p_factor_not(p):
            '''
            factor : NOT factor
            '''
            p[0] = {
                "length": len(p),
                "type": "factor",
                "_type": "NOT",
                "__type": p[2]["__type"],
                "factor": p[2]
            }

        def p_factor_uminus(p):
            '''
            factor : UMINUS factor
                   | ADDOP factor
            '''
            p[0] = {
                "length": len(p),
                "type": "factor",
                "_type": "UMINUS" if p[1] == "-" else "NORMAL",  # 符号类型：-/+
                "__type": p[2]["__type"],  # factor类型
                "factor": p[2]
            }

        def p_error(p):
            report_error("No relevant syntax definition",p.lineno if p else 0,[p.value if p else ""], p.lexpos if p else 0)
            # 错误类型：不符合语法
             
        self.parser = yacc(debug=False, write_tables=False)


    def search_symbol(self, token):
        if type(token) == str:
            token = [token]
        # 在子函数中
        if self.inSubFun and token[0] in list(self.subSymbol.keys()):
            return self.symbolMap[self.subSymbol[token[0]]]
        elif token[0] in list(self.curSymbol.keys()):  # 在当前符号表中
            return self.symbolMap[self.curSymbol[token[0]]]


    def _removeSymbolTable(self, p):
        if type(p) == dict:
            if "SymbolTable" in p:
                del p["SymbolTable"]
            for key in p:
                if type(p[key]) == list:
                    for item in p[key]:
                        if type(item) == dict:
                            self._removeSymbolTable(item)
                elif type(p[key]) == dict:
                    self._removeSymbolTable(p[key])


    def parse(self, data):
        self.SymbolTable = {"constants": [], "variables": [], "subFunc": []}
        self.error = []
        self.warning = []
        self.curSymbol = {}
        self.subSymbol = {}
        self.inSubFun = False
        self.id = 0
        self.symbolMap = {}
        self.subFuncMap = {}
        ast = None
        ast = self.parser.parse(data)
        # 该程序编译完毕，重置lineno
        self.lexer.lineno = 1
        self._removeSymbolTable(ast)
        return {
            "ast": ast,
            "symbolTable": self.SymbolTable,
            "error": self.error,
            "warning": self.warning,
        }


Parser = pParser()

import os

current_path = os.path.dirname(os.path.abspath(__file__))
# 构造数据文件夹的路径
data_path = os.path.join(current_path, "testcodes")
# 遍历文件夹中的所有文件
for file_name in os.listdir(data_path):
    file_path = os.path.join(data_path, file_name)
    with open(file_path, "r", encoding='utf-8') as f:
        data = f.read()
        f.close()
        res=json.dumps(Parser.parse(data))
        with open(os.path.join('testResults', '{}.json'.format(file_name)), 'w') as fi:
            fi.write(res)
            fi.close()
    

# fin = "testcodes/gcd.pas"
# f = open(fin, "r", encoding='utf-8')
# data = f.read()
# kk = Parser.parse(data)
# temp_data = json.dumps(kk)
# f2 = open("res.json", "w")
# f2.write(temp_data)
# f2.close()
