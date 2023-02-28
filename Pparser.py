from scanner import Scanner


class pParser(object):
    def __init__(self) -> None:
        self.scanner = Scanner()
        self.scanner.build()
        self.tokens = Scanner.tokens

    precedence = ()

    def p_programstruct(self, p):
        """programstruct : program_head SEMICOLON program_body ENDPOINT"""
        pass

    def p_program_head(self, p):
        """
        program_head : PROGRAM ID LPAREN idlist RPAREN
                     | PROGRAM ID
        """
        pass

    def p_program_body(self, p):
        """
        program_body : const_declarations var_declarations subprogram_declarations compound_statement
        """
        pass

    def p_idlist(self, p):
        """idlist : ID
        | idlist COMMA ID
        """
        pass

    def p_const_declarations(self, p):
        """
        const_declarations : CONST const_declaration SEMICOLON
                        |
        """
        pass

    def p_const_declaration(self, p):
        """
        const_declaration : const_declaration SEMICOLON ID EQUAL const_value
                        | ID EQUAL const_value
        """
        pass

    def p_const_value(self, p):
        """const_value : LETTER
        | PLUS INT_NUMBER
        | PLUS REAL_NUMBER
        """
        pass

    def p_const_value_num(self, p):
        """
        const_value : INT_NUMBER
        | REAL_NUMBER
        """
        pass

    def p_var_declarations(self, p):
        """
        var_declarations : VAR var_declaration SEMICOLON
                        |
        """
        pass

    def p_var_declaration(self, p):
        """
        var_declaration : var_declaration SEMICOLON idlist COLON type
                        | idlist COLON type
        """
        pass

    def p_type(self, p):
        """
        type : basic_type
            | ARRAY LBRAC period RBRAC OF basic_type
        """
        pass

    def p_basic_type(self, p):
        """
        basic_type : INTEGER
                    | REAL
                    | BOOLEAN
                    | CHAR
        """
        pass

    def p_period(self, p):
        """
        period : period COM DIGITS DOTDOT DIGITS
            | DIGITS DOTDOT DIGITS
        """
        pass

    def p_subprogram_declarations(self, p):
        """
        subprogram_declarations : subprogram_declarations subprogram SEMICOLON
                                |
        """
        pass

    def p_subprogram(self, p):
        """
        subprogram : subprogram_head SEMICOLON subprogram_body
        """
        pass

    def p_subprogram_head(self, p):
        """
        subprogram_head : seen_PROCEDURE PROCEDURE ID formal_parameter
                        | seen_FUNCTION FUNCTION ID formal_parameter COLON basic_type
        """
        pass

    def p_PROCEDURE(self, p):
        """
        seen_PROCEDURE :
        """
        pass

    def p_FUNCTION(self, p):
        """
        seen_FUNCTION :
        """
        pass

    def p_formal_parameter(self, p):
        """
        formal_parameter : LPAREN parameter_list RPAREN
                        |
        """
        pass

    def p_parameter_list(self, p):
        """
        parameter_list : parameter_list SEMICOLON parameter
                    | parameter
        """
        pass

    def p_parameter(self, p):
        """
        parameter : var_parameter
                | value_parameter
        """
        pass

    def p_var_parameter(self, p):
        """
        var_parameter : VAR value_parameter
        """
        pass

    def p_value_parameter(self, p):
        """
        value_parameter : idlist COLON basic_type
        """
        pass

    def p_subprogram_body(self, p):
        """
        subprogram_body : const_declarations var_declarations compound_statement
        """
        pass

    def p_compound_statement(self, p):
        """
        compound_statement : BEGIN statement_list END
        """
        pass

    def p_statement_list(self, p):
        """
        statement_list : statement_list SEMICOLON statement
                    | statement
        """
        pass

    def p_statement(self, p):
        """
        statement : variable ASSIGNOP expression
                | procedure_call
                | compound_statement
                | IF expression THEN statement else_part
                | FOR ID ASSIGNOP expression TO expression DO statement
                | READ LPAREN variable_list  RPAREN
                | WRITE LPAREN expression_list RPAREN
                |
        """
        pass

    def p_variable_list(self, p):
        """
        variable_list : variable_list COM variable
                    | variable
        """
        pass

    def p_variable(self, p):
        """
        variable : ID id_varpart
        """
        pass

    def p_id_varpart(self, p):
        """
        id_varpart : LBRAC expression_list RBRAC
                    |
        """
        pass

    def p_procedure_call(self, p):
        """
        procedure_call : ID
                        | ID LPAREN expression_list RPAREN
        """
        pass

    def p_else_part(self, p):
        """
        else_part : ELSE statement
                    |
        """
        pass

    def p_expression_list(self, p):
        """
        expression_list : expression_list COM expression
                        | expression
        """
        pass

    def p_expression(self, p):
        """
        expression : simple_expression RELOP simple_expression
                    | simple_expression
        """
        pass

    def p_expression_equal(self, p):
        """
        expression : simple_expression EQUAL simple_expression
        """
        pass

    def p_simple_expression(self, p):
        """
        simple_expression : simple_expression ADDOP term
                            | term
        """
        pass

    def p_term(self, p):
        """
        term : term MULOP factor
                | factor
        """
        pass

    def p_factor_num(self, p):
        """
        factor : NUM
                | DIGITS
        """
        pass

    def p_factor_variable(self, p):
        """
        factor : variable
        """
        pass

    def p_factor_procedure_id(self, p):
        """
        factor : ID LPAREN expression_list RPAREN
        """
        pass

    def p_factor_expression(self, p):
        """
        factor : LPAREN expression RPAREN
        """
        pass

    def p_factor_not(self, p):
        """
        factor : NOT factor
        """
        pass

    def p_factor_uminus(self, p):
        """
        factor : UMINUS factor
                | ADDOP factor
        """
        pass

    def p_multype(self, p):
        """
        multype : multype idlist COLON type SEMICOLON
                | idlist COLON type SEMICOLON
        """
        pass
