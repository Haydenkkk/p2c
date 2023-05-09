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
                    p[0]["SymbolTable"] += [
                        {
                            "id": self.id,
                            "token": i,
                            "type": p[5]["SymbolTable"]["type"],
                            "isArray": p[5]["SymbolTable"]["isArray"],
                            "dimension": p[5]["SymbolTable"]["dimension"],
                            "size": p[5]["SymbolTable"]["size"],
                            "start": p[5]["SymbolTable"]["start"],
                        }
                    ]
                    # 加入 symbolmap
                    self.symbolMap[self.id] = {
                        "id": self.id,
                        "token": i,
                        "type": p[5]["SymbolTable"]["type"],
                        "isArray": p[5]["SymbolTable"]["isArray"],
                        "dimension": p[5]["SymbolTable"]["dimension"],
                        "size": p[5]["SymbolTable"]["size"],
                        "start": p[5]["SymbolTable"]["start"],
                    }
                    self.id += 1
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
                    p[0]["SymbolTable"] += [
                        {
                            "id": self.id,
                            "token": i,
                            "type": p[3]["SymbolTable"]["type"],
                            "isArray": p[3]["SymbolTable"]["isArray"],
                            "dimension": p[3]["SymbolTable"]["dimension"],
                            "size": p[3]["SymbolTable"]["size"],
                            "start": p[3]["SymbolTable"]["start"],
                        }
                    ]
                    self.symbolMap[self.id] = {
                        "id": self.id,
                        "token": i,
                        "type": p[3]["SymbolTable"]["type"],
                        "isArray": p[3]["SymbolTable"]["isArray"],
                        "dimension": p[3]["SymbolTable"]["dimension"],
                        "size": p[3]["SymbolTable"]["size"],
                        "start": p[3]["SymbolTable"]["start"],
                    }
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
                    # 初始化错误信息
                    report_error("The upper bound is bigger than the lower bounds of the array",p.slice[3].lineno,[p[3], p[5]],p.slice[3].lineno + p.slice[3].lexpos - 1,p.slice[5].lineno
                                + p.slice[5].lexpos
                                + len(str(p[5])))
                p[0] = {
                    "length": len(p),
                    "type": "period",
                    "values": p[1]["values"] + [{"start": p[3], "end": p[5]}],
                }
                # 更新符号表
                p[0]["SymbolTable"] = {
                    "dimension": p[1]["SymbolTable"]["dimension"] + 1,  # 数组维度
                    "size": p[1]["SymbolTable"]["size"] + [p[5] - p[3] + 1],
                    "start": p[1]["SymbolTable"]["start"] + [p[3]],
                }
            # 产生式2 period -> digits .. digits
            else:

                if p[1] > p[3]:
                    report_error("The upper bound is bigger than the lower bounds of the array",p.slice[1].lineno,[p[1], p[3]],p.slice[1].lineno + p.slice[1].lexpos - 1,p.slice[3].lineno
                                + p.slice[3].lexpos
                                + len(str(p[3])))
                p[0] = {
                    "length": len(p),
                    "type": "period",
                    "values": [{"start": p[1], "end": p[3]}],
                }
                p[0]["SymbolTable"] = {
                    "dimension": 1,
                    "size": [p[3] - p[1] + 1],
                    "start": [p[1]],
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
                if p[3] in self.subFuncMap:
                    if not self.warning:
                        self.warning = []
                        self.warning += [{
                            "code": "函数重载",
                            "info": {
                                "line": p.lexer.lineno,
                                "value": [p[3]],
                                "lexpos": p.lexer.lexpos
                            }
                        }]#函数名称重定义

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
                if p[3] in self.subFuncMap:
                    if not self.warning:
                        self.warning = []
                        self.warning += [{
                            "code": "函数重载",
                            "info": {
                                "line": p.lexer.lineno,
                                "value": [p[3]],
                                "lexpos": p.lexer.lexpos
                            }
                        }]#函数名称重定义
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
