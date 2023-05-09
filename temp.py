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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "给未定义的变量赋值",
                        "info": {
                            "line": p.lexer.lineno,
                            "value": [p[2]],
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：给未定义的变量赋值
                id = self.search_symbol(p[2])
                if id:
                    if p[4]["__type"] == "UNDEFINED":  # expression未定义
                        if not self.error:
                            self.error = []
                        self.error += [{
                            "code": "使用未定义的变量进行赋值",
                            "info": {
                                "line": p.lexer.lineno,
                                "value": [p[2]],
                                "lexpos": p.lexer.lexpos
                            }
                        }]  # 错误类型：使用未定义的变量进行赋值
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
                            if not self.error:
                                self.error = []
                            self.error += [{
                                "code": "变量赋值类型不匹配",
                                "info": {
                                    "line": p.slice[3].lineno,
                                    "value": [p[2], id["type"] if id["type"] else "VOID", p[4]["__type"] if p[4]["__type"] else "VOID"],
                                    "lexpos": p.slice[3].lexpos + p.slice[3].lineno - 1
                                }
                            }]  # 错误类型：变量赋值类型不匹配，且不能转换
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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "给未定义的变量赋值",
                        "info": {
                            "line": p.lexer.lineno,
                            "value": [p[1]["ID"]],
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：给未定义的变量赋值
                id = self.search_symbol(p[1]["ID"])  # 获取变量id
                if p[3]["__type"] == "UNDEFINED":  # expression未定义
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "使用未定义的变量进行赋值",
                        "info": {
                            "line": p.lexer.lineno,
                            "value": [p[1]["ID"]],
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：使用未定义的变量进行赋值
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
                            if not self.error:
                                self.error = []
                            self.error += [{
                                "code": "变量赋值类型不匹配",
                                "info": {
                                    "line": p.slice[2].lineno,
                                    "value": [p[1]["ID"], id["type"] if id["type"] else "VOID", p[3]["__type"] if p[3]["__type"] else "VOID"],
                                    "lexpos": p.slice[2].lexpos + p.slice[2].lineno - 1
                                }
                            }]  # 错误类型：变量赋值类型不匹配，且不能转换
                else:
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "给未定义的变量赋值",
                        "info": {
                            "line": p.lexer.lineno,
                            "value": [p[1]["ID"]],
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：给未定义的变量赋值
            #  statement : procedure_call
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
                if not self.error:
                    self.error = []
                self.error += [{
                    "code": "使用的变量未定义",
                    "info": {
                        "line": p.slice[1].lineno,
                        "value": [p[1]],
                        "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                        "end_lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1])
                    }
                }]  # 错误类型：使用的变量未定义（变量标识符）
            elif type(p[1]) == list:  # 如果ID是list，则为record
                possiable_token = list(self.curSymbol.keys(
                )) + (list(self.subSymbol.keys()) if self.inSubFun else [])  # 整合参数表
                i = p[1][0]  # record名称
                if i not in possiable_token:
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "使用的变量未定义",
                        "info": {
                            "line": p.slice[1].lineno,
                            "value": [i],
                            "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                            "end_lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1])
                        }
                    }]  # 错误类型：使用的变量未定义
                elif self.search_symbol(i)["recordTable"]:  # 如果该变量已定义，且它的record存在
                    possiable_token = [j["token"] for j in self.search_symbol(
                        i)["recordTable"]["variables"]]  # possiable_token符号表成为该record的变量表
                    record_table = self.search_symbol(i)["recordTable"]
                for j in p[1][1:]:  # record内部项
                    new_possiable_token = []
                    for record_item in possiable_token:
                        new_possiable_token += record_item['ids']
                    possiable_token = new_possiable_token  # 更新possiable_token
                    if j not in possiable_token:
                        if not self.error:
                            self.error = []
                        self.error += [{
                            "code": "使用的变量未定义",
                            "info": {
                                "line": p.slice[1].lineno,
                                "value": [j],
                                "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                "end_lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1])
                            }
                        }]  # 错误类型：使用的变量未定义
                    # 该项已定义，在recordTable内部查，逐层循环
                    elif self.search_symbol(j, record_table)["recordTable"]:
                        possiable_token = [k["token"] for k in self.search_symbol(
                            j, record_table)["recordTable"]["variables"]]
                        record_table = self.search_symbol(
                            j, record_table)["recordTable"]
                    else:  # 最终层，确定最终该变量类型
                        p[0]["__type"] = self.search_symbol(
                            j, record_table)["type"]

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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "函数调用时变量个数不匹配",
                        "info": {
                            "line": p.slice[1].lineno,
                            "value": ["0", len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else [])],
                            "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                            "end_lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1 + len(p[1])
                        }
                    }]
            else:  # procedure_call : ID LPAREN expression_list RPAREN
                p[0] = {
                    "length": len(p),
                    "type": "procedure_call",
                    "ID": p[1],
                    "expression_list": p[3]
                }
                if len(p[3]["__type"]) != len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else []):  # 变量数量不一致
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "函数调用时变量个数不匹配",
                        "info": {
                            "line": p.slice[1].lineno,
                            "value": [len(p[3]["__type"]), len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else [])],
                            "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                            "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                        }
                    }]  # 错误类型：函数调用时变量个数不匹配
                else:  # 函数调用时变量数量一致
                    for i in range(len(p[3]["__type"])):  # 遍历expression_list
                        from_type = p[3]["__type"][i]
                        to_type = self.subFuncMap[p[1]]["variables"][i]["type"]
                        if from_type == "UNDEFINED":
                            if not self.error:
                                self.error = []
                            self.error += [{
                                "code": "函数调用时参数未定义",
                                "info": {
                                    "line": p.slice[1].lineno,
                                    "value": [from_type, to_type],
                                    "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                    "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                                }
                            }]  # 错误类型：函数调用时参数未定义
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
                                if not self.error:
                                    self.error = []
                                self.error += [{
                                    "code": "函数调用时参数类型不匹配",
                                    "info": {
                                        "line": p.slice[1].lineno,
                                        "value": [self.subFuncMap[p[1]]["variables"][i]['token'], from_type, to_type],
                                        "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                        "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                                    }
                                }]  # 错误类型：函数调用时参数类型不匹配，且不能转换
                        if self.subFuncMap[p[1]]["references"][i] and not (p[3]["expressions"] and p[3]["expressions"][i] and p[3]["expressions"][i]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["_type"] == "variable"):
                            # 判断函数的传参是否正确（expression/variable）
                            if not self.error:
                                self.error = []
                            self.error += [{
                                "code": "引用调用时使用了无法引用的表达式",
                                "info": {
                                    "line": p.slice[1].lineno,
                                    "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                    "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                                }
                            }]  # 无法翻译错误：引用调用时使用了无法引用的表达式

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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "对未定义的变量进行比较",
                        "info": {
                            "line": p.lexer.lineno,
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：对未定义的变量进行比较
                # simple_expression中的标识符类型为RECODRD
                elif p[1]["__type"] == "RECORD" or p[3]["__type"] == "RECORD":
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "对RECORD类型进行比较",
                        "info": {
                            "line": p.lexer.lineno,
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：对RECORD类型进行比较
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
            if p[1]["__type"] == "RECORD" or p[3]["__type"] == "RECORD":
                if not self.error:
                    self.error = []
                self.error += [{
                    "code": "对RECORD类型进行比较",
                    "info": {
                        "line": p.lexer.lineno,
                        "lexpos": p.lexer.lexpos
                    }
                }]  # 错误类型：对RECORD类型进行比较

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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "对未定义的变量进行运算",
                        "info": {
                            "line": p.lexer.lineno,
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：对未定义的变量进行运算
                    p[0]["__type"] = "UNDEFINED"
                # simple_expression或term中标识符类型为RECORD
                elif p[1]["__type"] == "RECORD" or p[3]["__type"] == "RECORD":
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "对RECORD类型进行运算",
                        "info": {
                            "line": p.lexer.lineno,
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：对RECORD类型进行运算
                    p[0]["__type"] = "RECORD"
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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "未知类型的运算",
                        "info": {
                            "line": p.lexer.lineno,
                            "value": [p[1]["__type"], p[3]["__type"]],
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：未知类型的运算
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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "对未定义的变量进行运算",
                        "info": {
                            "line": p.lexer.lineno,
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：对未定义的变量进行运算
                    p[0]["__type"] = "UNDEFINED"
                elif p[1]["__type"] == "RECORD" or p[3]["__type"] == "RECORD":  # term或factor中标识符为RECORD
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "对RECORD类型进行运算",
                        "info": {
                            "line": p.lexer.lineno,
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：对RECORD类型进行运算
                    p[0]["__type"] = "RECORD"
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
                    if not self.error:
                        self.error = []
                    self.error += [{
                        "code": "未知类型的运算",
                        "info": {
                            "line": p.lexer.lineno,
                            "value": [p[1]["__type"], p[3]["__type"]],
                            "lexpos": p.lexer.lexpos
                        }
                    }]  # 错误类型：未知类型的运算
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
                if not self.error:
                    self.error = []
                self.error += [{
                    "code": "函数调用时变量个数不匹配",
                    "info": {
                        "line": p.slice[1].lineno,
                        "value": [len(p[3]["__type"]), len(self.subFuncMap[p[1]]["variables"] if self.subFuncMap[p[1]]["variables"] else [])],
                        "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                        "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                    }
                }]  # 错误类型：函数调用时变量个数不匹配
            else:  # 函数调用时变量数量一致
                for i in range(len(p[3]["__type"])):  # 遍历expression_list
                    from_type = p[3]["__type"][i]
                    to_type = self.subFuncMap[p[1]]["variables"][i]["type"]
                    if from_type == "UNDEFINED":
                        if not self.error:
                            self.error = []
                        self.error += [{
                            "code": "函数调用时参数未定义",
                            "info": {
                                "line": p.slice[1].lineno,
                                "value": [from_type, to_type],
                                "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                            }
                        }]  # 错误类型：函数调用时参数未定义
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
                            if not self.error:
                                self.error = []
                            self.error += [{
                                "code": "函数调用时参数类型不匹配",
                                "info": {
                                    "line": p.slice[1].lineno,
                                    "value": [self.subFuncMap[p[1]]["variables"][i]['token'], from_type, to_type],
                                    "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                    "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                                }
                            }]  # 错误类型：函数调用时参数类型不匹配，且不能转换
                    if self.subFuncMap[p[1]]["references"][i] and not (p[3]["expressions"] and p[3]["expressions"][i] and p[3]["expressions"][i]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["length"] == 2 and p[3]["expressions"][i]["simple_expression"]["term"]["factor"]["_type"] == "variable"):
                        # 判断函数的传参是否正确（expression/variable）
                        if not self.error:
                            self.error = []
                        self.error += [{
                            "code": "引用调用时使用了无法引用的表达式",
                            "info": {
                                "line": p.slice[1].lineno,
                                "lexpos": p.slice[1].lexpos + p.slice[1].lineno - 1,
                                "end_lexpos": p.slice[4].lexpos + p.slice[4].lineno + len(p[4])
                            }
                        }]  # 无法翻译错误：引用调用时使用了无法引用的表达式

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

        def p_multype(p):
            '''
            multype : multype idlist COLON type SEMICOLON
                    | idlist COLON type SEMICOLON
            '''
            if len(p) == 6:  # multype : multype idlist COLON type SEMICOLON
                p[0] = {
                    "length": len(p),
                    "id": self.id,
                    "type": "multype",
                    "values": p[1]["values"]+[{
                        "idlist": p[2],
                        "type":p[4]
                    }]
                }
                p[0]["SymbolTable"] = {
                    "variables": p[1]["SymbolTable"]["variables"] + [{
                        "id": self.id,
                        "token": p[2],
                        "type": p[4]["SymbolTable"]["type"],
                        "isArray": p[4]["SymbolTable"]["isArray"],
                        "dimension": p[4]["SymbolTable"]["dimension"],
                        "size": p[4]["SymbolTable"]["size"],
                        "start": p[4]["SymbolTable"]["start"],
                        "recordTable": p[4]["SymbolTable"]["recordTable"]
                    }]  # 符号表，规约前一个multype符号表的变量、idlist符号表和type符号表
                }
                self.symbolMap[self.id] = {
                    "id": self.id,
                    "token": p[2],
                    "type": p[4]["SymbolTable"]["type"],
                    "isArray": p[4]["SymbolTable"]["isArray"],
                    "dimension": p[4]["SymbolTable"]["dimension"],
                    "size": p[4]["SymbolTable"]["size"],
                    "start": p[4]["SymbolTable"]["start"],
                    "recordTable": p[4]["SymbolTable"]["recordTable"]
                }
                self.id += 1  # 标识符数量+1
            else:  # multype : idlist COLON type SEMICOLON
                p[0] = {
                    "length": len(p),
                    "id": self.id,
                    "type": "multype",
                    "values": [{
                        "idlist": p[1],
                        "type":p[3]
                    }]
                }
                p[0]["SymbolTable"] = {
                    "variables": [{
                        "id": self.id,
                        "token": p[1],
                        "type": p[3]["SymbolTable"]["type"],
                        "isArray": p[3]["SymbolTable"]["isArray"],
                        "dimension": p[3]["SymbolTable"]["dimension"],
                        "size": p[3]["SymbolTable"]["size"],
                        "start": p[3]["SymbolTable"]["start"],
                        "recordTable": p[3]["SymbolTable"]["recordTable"]
                    }]  # 符号表，规约idlist符号表和type符号表
                }
                self.symbolMap[self.id] = {
                    "id": self.id,
                    "token": p[1],
                    "type": p[3]["SymbolTable"]["type"],
                    "isArray": p[3]["SymbolTable"]["isArray"],
                    "dimension": p[3]["SymbolTable"]["dimension"],
                    "size": p[3]["SymbolTable"]["size"],
                    "start": p[3]["SymbolTable"]["start"],
                    "recordTable": p[3]["SymbolTable"]["recordTable"]
                }
                self.id += 1

        def p_error(p):
            if not self.error:
                self.error = []
            self.error.append({
                "code": "不符合语法",
                "info": {
                    "line": p.lineno if p else 0,
                    "value": [p.value if p else ""],
                    "lexpos": p.lexpos if p else 0
                }
            })  # 错误类型：不符合语法

        self.parser = yacc(debug=debug, write_tables=write_tables)

    def search_symbol(self, token):
        if type(token) == str:
            token = [token]
        # 在子函数中
        if self.inSubFun and token[0] in list(self.subSymbol.keys()):
            return self.symbolMap[self.subSymbol[token[0]]]
        elif token[0] in list(self.curSymbol.keys()):  # 在当前符号表中
            return self.symbolMap[self.curSymbol[token[0]]]