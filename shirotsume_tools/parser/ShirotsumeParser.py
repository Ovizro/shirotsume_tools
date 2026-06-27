# Generated from ./Shirotsume.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,36,289,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,1,0,5,0,54,
        8,0,10,0,12,0,57,9,0,1,0,4,0,60,8,0,11,0,12,0,61,1,1,1,1,3,1,66,
        8,1,1,2,1,2,1,2,1,3,1,3,1,3,1,3,5,3,75,8,3,10,3,12,3,78,9,3,1,3,
        1,3,1,4,1,4,1,4,1,4,1,4,1,4,1,5,5,5,89,8,5,10,5,12,5,92,9,5,1,6,
        1,6,1,6,1,6,1,6,1,6,1,7,5,7,101,8,7,10,7,12,7,104,9,7,1,8,1,8,1,
        8,1,8,1,8,1,8,1,8,1,8,3,8,114,8,8,1,9,1,9,1,9,1,9,1,9,1,9,1,10,1,
        10,1,10,3,10,125,8,10,1,10,1,10,1,10,1,11,1,11,1,11,5,11,133,8,11,
        10,11,12,11,136,9,11,1,12,1,12,1,12,1,12,1,13,1,13,1,13,1,13,1,14,
        1,14,1,14,1,14,1,14,1,14,1,15,1,15,1,15,1,15,1,16,1,16,1,16,3,16,
        159,8,16,1,17,1,17,1,17,1,17,1,17,1,17,5,17,167,8,17,10,17,12,17,
        170,9,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,1,17,5,17,180,8,17,10,
        17,12,17,183,9,17,1,17,1,17,5,17,187,8,17,10,17,12,17,190,9,17,1,
        17,1,17,1,17,5,17,195,8,17,10,17,12,17,198,9,17,1,17,3,17,201,8,
        17,1,18,1,18,1,18,1,18,1,18,1,18,5,18,209,8,18,10,18,12,18,212,9,
        18,1,18,3,18,215,8,18,1,19,1,19,1,19,5,19,220,8,19,10,19,12,19,223,
        9,19,1,19,1,19,1,20,1,20,1,20,1,20,1,20,5,20,232,8,20,10,20,12,20,
        235,9,20,1,20,3,20,238,8,20,1,21,1,21,1,21,1,22,1,22,1,22,1,22,1,
        22,1,22,1,22,1,22,1,22,1,22,3,22,253,8,22,1,23,4,23,256,8,23,11,
        23,12,23,257,1,24,1,24,1,24,1,24,1,24,1,24,1,24,1,24,1,24,1,24,1,
        24,1,24,3,24,272,8,24,1,24,1,24,1,24,5,24,277,8,24,10,24,12,24,280,
        9,24,1,25,1,25,1,25,1,25,1,25,3,25,287,8,25,1,25,0,1,48,26,0,2,4,
        6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,
        50,0,3,2,0,27,27,29,29,1,0,27,29,1,0,22,23,300,0,55,1,0,0,0,2,65,
        1,0,0,0,4,67,1,0,0,0,6,70,1,0,0,0,8,81,1,0,0,0,10,90,1,0,0,0,12,
        93,1,0,0,0,14,102,1,0,0,0,16,113,1,0,0,0,18,115,1,0,0,0,20,121,1,
        0,0,0,22,129,1,0,0,0,24,137,1,0,0,0,26,141,1,0,0,0,28,145,1,0,0,
        0,30,151,1,0,0,0,32,158,1,0,0,0,34,160,1,0,0,0,36,202,1,0,0,0,38,
        216,1,0,0,0,40,226,1,0,0,0,42,239,1,0,0,0,44,252,1,0,0,0,46,255,
        1,0,0,0,48,271,1,0,0,0,50,286,1,0,0,0,52,54,3,4,2,0,53,52,1,0,0,
        0,54,57,1,0,0,0,55,53,1,0,0,0,55,56,1,0,0,0,56,59,1,0,0,0,57,55,
        1,0,0,0,58,60,3,2,1,0,59,58,1,0,0,0,60,61,1,0,0,0,61,59,1,0,0,0,
        61,62,1,0,0,0,62,1,1,0,0,0,63,66,3,6,3,0,64,66,3,12,6,0,65,63,1,
        0,0,0,65,64,1,0,0,0,66,3,1,0,0,0,67,68,5,1,0,0,68,69,5,28,0,0,69,
        5,1,0,0,0,70,71,5,2,0,0,71,72,7,0,0,0,72,76,5,3,0,0,73,75,3,8,4,
        0,74,73,1,0,0,0,75,78,1,0,0,0,76,74,1,0,0,0,76,77,1,0,0,0,77,79,
        1,0,0,0,78,76,1,0,0,0,79,80,5,4,0,0,80,7,1,0,0,0,81,82,5,5,0,0,82,
        83,7,0,0,0,83,84,5,3,0,0,84,85,3,10,5,0,85,86,5,4,0,0,86,9,1,0,0,
        0,87,89,3,16,8,0,88,87,1,0,0,0,89,92,1,0,0,0,90,88,1,0,0,0,90,91,
        1,0,0,0,91,11,1,0,0,0,92,90,1,0,0,0,93,94,5,6,0,0,94,95,7,0,0,0,
        95,96,5,3,0,0,96,97,3,14,7,0,97,98,5,4,0,0,98,13,1,0,0,0,99,101,
        3,16,8,0,100,99,1,0,0,0,101,104,1,0,0,0,102,100,1,0,0,0,102,103,
        1,0,0,0,103,15,1,0,0,0,104,102,1,0,0,0,105,114,3,18,9,0,106,114,
        3,20,10,0,107,114,3,24,12,0,108,114,3,26,13,0,109,114,3,28,14,0,
        110,114,3,30,15,0,111,114,3,32,16,0,112,114,3,42,21,0,113,105,1,
        0,0,0,113,106,1,0,0,0,113,107,1,0,0,0,113,108,1,0,0,0,113,109,1,
        0,0,0,113,110,1,0,0,0,113,111,1,0,0,0,113,112,1,0,0,0,114,17,1,0,
        0,0,115,116,5,7,0,0,116,117,5,8,0,0,117,118,3,50,25,0,118,119,5,
        9,0,0,119,120,5,10,0,0,120,19,1,0,0,0,121,122,5,27,0,0,122,124,5,
        8,0,0,123,125,3,22,11,0,124,123,1,0,0,0,124,125,1,0,0,0,125,126,
        1,0,0,0,126,127,5,9,0,0,127,128,5,10,0,0,128,21,1,0,0,0,129,134,
        3,48,24,0,130,131,5,11,0,0,131,133,3,48,24,0,132,130,1,0,0,0,133,
        136,1,0,0,0,134,132,1,0,0,0,134,135,1,0,0,0,135,23,1,0,0,0,136,134,
        1,0,0,0,137,138,5,12,0,0,138,139,5,25,0,0,139,140,5,10,0,0,140,25,
        1,0,0,0,141,142,5,13,0,0,142,143,7,1,0,0,143,144,5,10,0,0,144,27,
        1,0,0,0,145,146,5,14,0,0,146,147,7,1,0,0,147,148,5,11,0,0,148,149,
        5,27,0,0,149,150,5,10,0,0,150,29,1,0,0,0,151,152,5,15,0,0,152,153,
        5,29,0,0,153,154,5,10,0,0,154,31,1,0,0,0,155,159,3,34,17,0,156,159,
        3,36,18,0,157,159,3,38,19,0,158,155,1,0,0,0,158,156,1,0,0,0,158,
        157,1,0,0,0,159,33,1,0,0,0,160,161,5,16,0,0,161,162,5,8,0,0,162,
        163,3,48,24,0,163,164,5,9,0,0,164,168,5,3,0,0,165,167,3,16,8,0,166,
        165,1,0,0,0,167,170,1,0,0,0,168,166,1,0,0,0,168,169,1,0,0,0,169,
        171,1,0,0,0,170,168,1,0,0,0,171,188,5,4,0,0,172,173,5,17,0,0,173,
        174,5,16,0,0,174,175,5,8,0,0,175,176,3,48,24,0,176,177,5,9,0,0,177,
        181,5,3,0,0,178,180,3,16,8,0,179,178,1,0,0,0,180,183,1,0,0,0,181,
        179,1,0,0,0,181,182,1,0,0,0,182,184,1,0,0,0,183,181,1,0,0,0,184,
        185,5,4,0,0,185,187,1,0,0,0,186,172,1,0,0,0,187,190,1,0,0,0,188,
        186,1,0,0,0,188,189,1,0,0,0,189,200,1,0,0,0,190,188,1,0,0,0,191,
        192,5,17,0,0,192,196,5,3,0,0,193,195,3,16,8,0,194,193,1,0,0,0,195,
        198,1,0,0,0,196,194,1,0,0,0,196,197,1,0,0,0,197,199,1,0,0,0,198,
        196,1,0,0,0,199,201,5,4,0,0,200,191,1,0,0,0,200,201,1,0,0,0,201,
        35,1,0,0,0,202,203,5,18,0,0,203,204,5,8,0,0,204,205,3,48,24,0,205,
        206,5,9,0,0,206,210,5,3,0,0,207,209,3,16,8,0,208,207,1,0,0,0,209,
        212,1,0,0,0,210,208,1,0,0,0,210,211,1,0,0,0,211,214,1,0,0,0,212,
        210,1,0,0,0,213,215,5,4,0,0,214,213,1,0,0,0,214,215,1,0,0,0,215,
        37,1,0,0,0,216,217,5,19,0,0,217,221,5,3,0,0,218,220,3,40,20,0,219,
        218,1,0,0,0,220,223,1,0,0,0,221,219,1,0,0,0,221,222,1,0,0,0,222,
        224,1,0,0,0,223,221,1,0,0,0,224,225,5,4,0,0,225,39,1,0,0,0,226,227,
        5,20,0,0,227,228,5,28,0,0,228,229,5,21,0,0,229,233,5,3,0,0,230,232,
        3,16,8,0,231,230,1,0,0,0,232,235,1,0,0,0,233,231,1,0,0,0,233,234,
        1,0,0,0,234,237,1,0,0,0,235,233,1,0,0,0,236,238,5,4,0,0,237,236,
        1,0,0,0,237,238,1,0,0,0,238,41,1,0,0,0,239,240,7,2,0,0,240,241,5,
        10,0,0,241,43,1,0,0,0,242,243,5,8,0,0,243,244,5,25,0,0,244,245,5,
        11,0,0,245,246,5,25,0,0,246,253,5,9,0,0,247,248,5,3,0,0,248,249,
        5,25,0,0,249,250,5,11,0,0,250,251,5,25,0,0,251,253,5,4,0,0,252,242,
        1,0,0,0,252,247,1,0,0,0,253,45,1,0,0,0,254,256,3,44,22,0,255,254,
        1,0,0,0,256,257,1,0,0,0,257,255,1,0,0,0,257,258,1,0,0,0,258,47,1,
        0,0,0,259,260,6,24,-1,0,260,272,5,25,0,0,261,272,5,28,0,0,262,272,
        5,26,0,0,263,272,5,27,0,0,264,272,5,30,0,0,265,272,5,24,0,0,266,
        272,3,46,23,0,267,268,5,8,0,0,268,269,3,48,24,0,269,270,5,9,0,0,
        270,272,1,0,0,0,271,259,1,0,0,0,271,261,1,0,0,0,271,262,1,0,0,0,
        271,263,1,0,0,0,271,264,1,0,0,0,271,265,1,0,0,0,271,266,1,0,0,0,
        271,267,1,0,0,0,272,278,1,0,0,0,273,274,10,1,0,0,274,275,5,31,0,
        0,275,277,3,48,24,2,276,273,1,0,0,0,277,280,1,0,0,0,278,276,1,0,
        0,0,278,279,1,0,0,0,279,49,1,0,0,0,280,278,1,0,0,0,281,282,5,24,
        0,0,282,283,5,32,0,0,283,287,3,48,24,0,284,285,5,24,0,0,285,287,
        5,33,0,0,286,281,1,0,0,0,286,284,1,0,0,0,287,51,1,0,0,0,25,55,61,
        65,76,90,102,113,124,134,158,168,181,188,196,200,210,214,221,233,
        237,252,257,271,278,286
    ]

class ShirotsumeParser ( Parser ):

    grammarFileName = "Shirotsume.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'#base_path'", "'class'", "'{'", "'}'", 
                     "'method'", "'page'", "'Operate'", "'('", "')'", "';'", 
                     "','", "'wait'", "'call'", "'far_call'", "'shift'", 
                     "'if'", "'else'", "'while'", "'select'", "'case'", 
                     "':'", "'return'", "'scene_return'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "IDENTIFIER", "NUMBER", "BOOL", "LITERAL", "STRING", 
                      "TEXT", "COLOR", "OPERATOR", "ASSIGNMENT_OPERATOR", 
                      "RIGHT_OPERATOR", "COMMENT", "LINE_COMMENT", "WS" ]

    RULE_program = 0
    RULE_declaration = 1
    RULE_macro_declaration = 2
    RULE_class_declaration = 3
    RULE_method_declaration = 4
    RULE_method_body = 5
    RULE_page_declaration = 6
    RULE_page_body = 7
    RULE_statement = 8
    RULE_operate_statement = 9
    RULE_function_call = 10
    RULE_function_arguments = 11
    RULE_wait_statement = 12
    RULE_call_statement = 13
    RULE_far_call_statement = 14
    RULE_shift_statement = 15
    RULE_control_statement = 16
    RULE_if_statement = 17
    RULE_while_statement = 18
    RULE_select_statement = 19
    RULE_case_statement = 20
    RULE_return_statement = 21
    RULE_move_vector_item = 22
    RULE_move_vector = 23
    RULE_expression = 24
    RULE_operate = 25

    ruleNames =  [ "program", "declaration", "macro_declaration", "class_declaration", 
                   "method_declaration", "method_body", "page_declaration", 
                   "page_body", "statement", "operate_statement", "function_call", 
                   "function_arguments", "wait_statement", "call_statement", 
                   "far_call_statement", "shift_statement", "control_statement", 
                   "if_statement", "while_statement", "select_statement", 
                   "case_statement", "return_statement", "move_vector_item", 
                   "move_vector", "expression", "operate" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    IDENTIFIER=24
    NUMBER=25
    BOOL=26
    LITERAL=27
    STRING=28
    TEXT=29
    COLOR=30
    OPERATOR=31
    ASSIGNMENT_OPERATOR=32
    RIGHT_OPERATOR=33
    COMMENT=34
    LINE_COMMENT=35
    WS=36

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def macro_declaration(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.Macro_declarationContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.Macro_declarationContext,i)


        def declaration(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.DeclarationContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.DeclarationContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = ShirotsumeParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 55
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 52
                self.macro_declaration()
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 59 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 58
                self.declaration()
                self.state = 61 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==2 or _la==6):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeclarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def class_declaration(self):
            return self.getTypedRuleContext(ShirotsumeParser.Class_declarationContext,0)


        def page_declaration(self):
            return self.getTypedRuleContext(ShirotsumeParser.Page_declarationContext,0)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclaration" ):
                listener.enterDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclaration" ):
                listener.exitDeclaration(self)




    def declaration(self):

        localctx = ShirotsumeParser.DeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_declaration)
        try:
            self.state = 65
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [2]:
                self.enterOuterAlt(localctx, 1)
                self.state = 63
                self.class_declaration()
                pass
            elif token in [6]:
                self.enterOuterAlt(localctx, 2)
                self.state = 64
                self.page_declaration()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Macro_declarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(ShirotsumeParser.STRING, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_macro_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMacro_declaration" ):
                listener.enterMacro_declaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMacro_declaration" ):
                listener.exitMacro_declaration(self)




    def macro_declaration(self):

        localctx = ShirotsumeParser.Macro_declarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_macro_declaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(ShirotsumeParser.T__0)
            self.state = 68
            self.match(ShirotsumeParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Class_declarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL(self):
            return self.getToken(ShirotsumeParser.LITERAL, 0)

        def TEXT(self):
            return self.getToken(ShirotsumeParser.TEXT, 0)

        def method_declaration(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.Method_declarationContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.Method_declarationContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_class_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClass_declaration" ):
                listener.enterClass_declaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClass_declaration" ):
                listener.exitClass_declaration(self)




    def class_declaration(self):

        localctx = ShirotsumeParser.Class_declarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_class_declaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            self.match(ShirotsumeParser.T__1)
            self.state = 71
            _la = self._input.LA(1)
            if not(_la==27 or _la==29):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 72
            self.match(ShirotsumeParser.T__2)
            self.state = 76
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==5:
                self.state = 73
                self.method_declaration()
                self.state = 78
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 79
            self.match(ShirotsumeParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Method_declarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def method_body(self):
            return self.getTypedRuleContext(ShirotsumeParser.Method_bodyContext,0)


        def LITERAL(self):
            return self.getToken(ShirotsumeParser.LITERAL, 0)

        def TEXT(self):
            return self.getToken(ShirotsumeParser.TEXT, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_method_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMethod_declaration" ):
                listener.enterMethod_declaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMethod_declaration" ):
                listener.exitMethod_declaration(self)




    def method_declaration(self):

        localctx = ShirotsumeParser.Method_declarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_method_declaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 81
            self.match(ShirotsumeParser.T__4)
            self.state = 82
            _la = self._input.LA(1)
            if not(_la==27 or _la==29):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 83
            self.match(ShirotsumeParser.T__2)
            self.state = 84
            self.method_body()
            self.state = 85
            self.match(ShirotsumeParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Method_bodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.StatementContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.StatementContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_method_body

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMethod_body" ):
                listener.enterMethod_body(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMethod_body" ):
                listener.exitMethod_body(self)




    def method_body(self):

        localctx = ShirotsumeParser.Method_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_method_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 90
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 147714176) != 0):
                self.state = 87
                self.statement()
                self.state = 92
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Page_declarationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def page_body(self):
            return self.getTypedRuleContext(ShirotsumeParser.Page_bodyContext,0)


        def LITERAL(self):
            return self.getToken(ShirotsumeParser.LITERAL, 0)

        def TEXT(self):
            return self.getToken(ShirotsumeParser.TEXT, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_page_declaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPage_declaration" ):
                listener.enterPage_declaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPage_declaration" ):
                listener.exitPage_declaration(self)




    def page_declaration(self):

        localctx = ShirotsumeParser.Page_declarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_page_declaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(ShirotsumeParser.T__5)
            self.state = 94
            _la = self._input.LA(1)
            if not(_la==27 or _la==29):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 95
            self.match(ShirotsumeParser.T__2)
            self.state = 96
            self.page_body()
            self.state = 97
            self.match(ShirotsumeParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Page_bodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.StatementContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.StatementContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_page_body

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPage_body" ):
                listener.enterPage_body(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPage_body" ):
                listener.exitPage_body(self)




    def page_body(self):

        localctx = ShirotsumeParser.Page_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_page_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 102
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 147714176) != 0):
                self.state = 99
                self.statement()
                self.state = 104
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def operate_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Operate_statementContext,0)


        def function_call(self):
            return self.getTypedRuleContext(ShirotsumeParser.Function_callContext,0)


        def wait_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Wait_statementContext,0)


        def call_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Call_statementContext,0)


        def far_call_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Far_call_statementContext,0)


        def shift_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Shift_statementContext,0)


        def control_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Control_statementContext,0)


        def return_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Return_statementContext,0)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)




    def statement(self):

        localctx = ShirotsumeParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_statement)
        try:
            self.state = 113
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [7]:
                self.enterOuterAlt(localctx, 1)
                self.state = 105
                self.operate_statement()
                pass
            elif token in [27]:
                self.enterOuterAlt(localctx, 2)
                self.state = 106
                self.function_call()
                pass
            elif token in [12]:
                self.enterOuterAlt(localctx, 3)
                self.state = 107
                self.wait_statement()
                pass
            elif token in [13]:
                self.enterOuterAlt(localctx, 4)
                self.state = 108
                self.call_statement()
                pass
            elif token in [14]:
                self.enterOuterAlt(localctx, 5)
                self.state = 109
                self.far_call_statement()
                pass
            elif token in [15]:
                self.enterOuterAlt(localctx, 6)
                self.state = 110
                self.shift_statement()
                pass
            elif token in [16, 18, 19]:
                self.enterOuterAlt(localctx, 7)
                self.state = 111
                self.control_statement()
                pass
            elif token in [22, 23]:
                self.enterOuterAlt(localctx, 8)
                self.state = 112
                self.return_statement()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Operate_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def operate(self):
            return self.getTypedRuleContext(ShirotsumeParser.OperateContext,0)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_operate_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperate_statement" ):
                listener.enterOperate_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperate_statement" ):
                listener.exitOperate_statement(self)




    def operate_statement(self):

        localctx = ShirotsumeParser.Operate_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_operate_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 115
            self.match(ShirotsumeParser.T__6)
            self.state = 116
            self.match(ShirotsumeParser.T__7)
            self.state = 117
            self.operate()
            self.state = 118
            self.match(ShirotsumeParser.T__8)
            self.state = 119
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_callContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL(self):
            return self.getToken(ShirotsumeParser.LITERAL, 0)

        def function_arguments(self):
            return self.getTypedRuleContext(ShirotsumeParser.Function_argumentsContext,0)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_function_call

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_call" ):
                listener.enterFunction_call(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_call" ):
                listener.exitFunction_call(self)




    def function_call(self):

        localctx = ShirotsumeParser.Function_callContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_function_call)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 121
            self.match(ShirotsumeParser.LITERAL)
            self.state = 122
            self.match(ShirotsumeParser.T__7)
            self.state = 124
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 1593835784) != 0):
                self.state = 123
                self.function_arguments()


            self.state = 126
            self.match(ShirotsumeParser.T__8)
            self.state = 127
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Function_argumentsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.ExpressionContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_function_arguments

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunction_arguments" ):
                listener.enterFunction_arguments(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunction_arguments" ):
                listener.exitFunction_arguments(self)




    def function_arguments(self):

        localctx = ShirotsumeParser.Function_argumentsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_function_arguments)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 129
            self.expression(0)
            self.state = 134
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==11:
                self.state = 130
                self.match(ShirotsumeParser.T__10)
                self.state = 131
                self.expression(0)
                self.state = 136
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Wait_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ShirotsumeParser.NUMBER, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_wait_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWait_statement" ):
                listener.enterWait_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWait_statement" ):
                listener.exitWait_statement(self)




    def wait_statement(self):

        localctx = ShirotsumeParser.Wait_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_wait_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 137
            self.match(ShirotsumeParser.T__11)
            self.state = 138
            self.match(ShirotsumeParser.NUMBER)
            self.state = 139
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Call_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL(self):
            return self.getToken(ShirotsumeParser.LITERAL, 0)

        def STRING(self):
            return self.getToken(ShirotsumeParser.STRING, 0)

        def TEXT(self):
            return self.getToken(ShirotsumeParser.TEXT, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_call_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCall_statement" ):
                listener.enterCall_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCall_statement" ):
                listener.exitCall_statement(self)




    def call_statement(self):

        localctx = ShirotsumeParser.Call_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_call_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 141
            self.match(ShirotsumeParser.T__12)
            self.state = 142
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 939524096) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 143
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Far_call_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LITERAL(self, i:int=None):
            if i is None:
                return self.getTokens(ShirotsumeParser.LITERAL)
            else:
                return self.getToken(ShirotsumeParser.LITERAL, i)

        def STRING(self):
            return self.getToken(ShirotsumeParser.STRING, 0)

        def TEXT(self):
            return self.getToken(ShirotsumeParser.TEXT, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_far_call_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFar_call_statement" ):
                listener.enterFar_call_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFar_call_statement" ):
                listener.exitFar_call_statement(self)




    def far_call_statement(self):

        localctx = ShirotsumeParser.Far_call_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_far_call_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 145
            self.match(ShirotsumeParser.T__13)
            self.state = 146
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 939524096) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 147
            self.match(ShirotsumeParser.T__10)
            self.state = 148
            self.match(ShirotsumeParser.LITERAL)
            self.state = 149
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Shift_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self):
            return self.getToken(ShirotsumeParser.TEXT, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_shift_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterShift_statement" ):
                listener.enterShift_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitShift_statement" ):
                listener.exitShift_statement(self)




    def shift_statement(self):

        localctx = ShirotsumeParser.Shift_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_shift_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 151
            self.match(ShirotsumeParser.T__14)
            self.state = 152
            self.match(ShirotsumeParser.TEXT)
            self.state = 153
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Control_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def if_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.If_statementContext,0)


        def while_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.While_statementContext,0)


        def select_statement(self):
            return self.getTypedRuleContext(ShirotsumeParser.Select_statementContext,0)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_control_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterControl_statement" ):
                listener.enterControl_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitControl_statement" ):
                listener.exitControl_statement(self)




    def control_statement(self):

        localctx = ShirotsumeParser.Control_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_control_statement)
        try:
            self.state = 158
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 155
                self.if_statement()
                pass
            elif token in [18]:
                self.enterOuterAlt(localctx, 2)
                self.state = 156
                self.while_statement()
                pass
            elif token in [19]:
                self.enterOuterAlt(localctx, 3)
                self.state = 157
                self.select_statement()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class If_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.ExpressionContext,i)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.StatementContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.StatementContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_if_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIf_statement" ):
                listener.enterIf_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIf_statement" ):
                listener.exitIf_statement(self)




    def if_statement(self):

        localctx = ShirotsumeParser.If_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_if_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 160
            self.match(ShirotsumeParser.T__15)
            self.state = 161
            self.match(ShirotsumeParser.T__7)
            self.state = 162
            self.expression(0)
            self.state = 163
            self.match(ShirotsumeParser.T__8)
            self.state = 164
            self.match(ShirotsumeParser.T__2)
            self.state = 168
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 147714176) != 0):
                self.state = 165
                self.statement()
                self.state = 170
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 171
            self.match(ShirotsumeParser.T__3)
            self.state = 188
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 172
                    self.match(ShirotsumeParser.T__16)
                    self.state = 173
                    self.match(ShirotsumeParser.T__15)
                    self.state = 174
                    self.match(ShirotsumeParser.T__7)
                    self.state = 175
                    self.expression(0)
                    self.state = 176
                    self.match(ShirotsumeParser.T__8)
                    self.state = 177
                    self.match(ShirotsumeParser.T__2)
                    self.state = 181
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while (((_la) & ~0x3f) == 0 and ((1 << _la) & 147714176) != 0):
                        self.state = 178
                        self.statement()
                        self.state = 183
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)

                    self.state = 184
                    self.match(ShirotsumeParser.T__3) 
                self.state = 190
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

            self.state = 200
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==17:
                self.state = 191
                self.match(ShirotsumeParser.T__16)
                self.state = 192
                self.match(ShirotsumeParser.T__2)
                self.state = 196
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while (((_la) & ~0x3f) == 0 and ((1 << _la) & 147714176) != 0):
                    self.state = 193
                    self.statement()
                    self.state = 198
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 199
                self.match(ShirotsumeParser.T__3)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class While_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(ShirotsumeParser.ExpressionContext,0)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.StatementContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.StatementContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_while_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhile_statement" ):
                listener.enterWhile_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhile_statement" ):
                listener.exitWhile_statement(self)




    def while_statement(self):

        localctx = ShirotsumeParser.While_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_while_statement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 202
            self.match(ShirotsumeParser.T__17)
            self.state = 203
            self.match(ShirotsumeParser.T__7)
            self.state = 204
            self.expression(0)
            self.state = 205
            self.match(ShirotsumeParser.T__8)
            self.state = 206
            self.match(ShirotsumeParser.T__2)
            self.state = 210
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,15,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 207
                    self.statement() 
                self.state = 212
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,15,self._ctx)

            self.state = 214
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
            if la_ == 1:
                self.state = 213
                self.match(ShirotsumeParser.T__3)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Select_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def case_statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.Case_statementContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.Case_statementContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_select_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSelect_statement" ):
                listener.enterSelect_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSelect_statement" ):
                listener.exitSelect_statement(self)




    def select_statement(self):

        localctx = ShirotsumeParser.Select_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_select_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 216
            self.match(ShirotsumeParser.T__18)
            self.state = 217
            self.match(ShirotsumeParser.T__2)
            self.state = 221
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==20:
                self.state = 218
                self.case_statement()
                self.state = 223
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 224
            self.match(ShirotsumeParser.T__3)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Case_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(ShirotsumeParser.STRING, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.StatementContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.StatementContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_case_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCase_statement" ):
                listener.enterCase_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCase_statement" ):
                listener.exitCase_statement(self)




    def case_statement(self):

        localctx = ShirotsumeParser.Case_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_case_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 226
            self.match(ShirotsumeParser.T__19)
            self.state = 227
            self.match(ShirotsumeParser.STRING)
            self.state = 228
            self.match(ShirotsumeParser.T__20)
            self.state = 229
            self.match(ShirotsumeParser.T__2)
            self.state = 233
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 147714176) != 0):
                self.state = 230
                self.statement()
                self.state = 235
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 237
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,19,self._ctx)
            if la_ == 1:
                self.state = 236
                self.match(ShirotsumeParser.T__3)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Return_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_return_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturn_statement" ):
                listener.enterReturn_statement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturn_statement" ):
                listener.exitReturn_statement(self)




    def return_statement(self):

        localctx = ShirotsumeParser.Return_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_return_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 239
            _la = self._input.LA(1)
            if not(_la==22 or _la==23):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 240
            self.match(ShirotsumeParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Move_vector_itemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(ShirotsumeParser.NUMBER)
            else:
                return self.getToken(ShirotsumeParser.NUMBER, i)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_move_vector_item

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMove_vector_item" ):
                listener.enterMove_vector_item(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMove_vector_item" ):
                listener.exitMove_vector_item(self)




    def move_vector_item(self):

        localctx = ShirotsumeParser.Move_vector_itemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_move_vector_item)
        try:
            self.state = 252
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                self.enterOuterAlt(localctx, 1)
                self.state = 242
                self.match(ShirotsumeParser.T__7)
                self.state = 243
                self.match(ShirotsumeParser.NUMBER)
                self.state = 244
                self.match(ShirotsumeParser.T__10)
                self.state = 245
                self.match(ShirotsumeParser.NUMBER)
                self.state = 246
                self.match(ShirotsumeParser.T__8)
                pass
            elif token in [3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 247
                self.match(ShirotsumeParser.T__2)
                self.state = 248
                self.match(ShirotsumeParser.NUMBER)
                self.state = 249
                self.match(ShirotsumeParser.T__10)
                self.state = 250
                self.match(ShirotsumeParser.NUMBER)
                self.state = 251
                self.match(ShirotsumeParser.T__3)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Move_vectorContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def move_vector_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.Move_vector_itemContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.Move_vector_itemContext,i)


        def getRuleIndex(self):
            return ShirotsumeParser.RULE_move_vector

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMove_vector" ):
                listener.enterMove_vector(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMove_vector" ):
                listener.exitMove_vector(self)




    def move_vector(self):

        localctx = ShirotsumeParser.Move_vectorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_move_vector)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 255 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 254
                    self.move_vector_item()

                else:
                    raise NoViableAltException(self)
                self.state = 257 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(ShirotsumeParser.NUMBER, 0)

        def STRING(self):
            return self.getToken(ShirotsumeParser.STRING, 0)

        def BOOL(self):
            return self.getToken(ShirotsumeParser.BOOL, 0)

        def LITERAL(self):
            return self.getToken(ShirotsumeParser.LITERAL, 0)

        def COLOR(self):
            return self.getToken(ShirotsumeParser.COLOR, 0)

        def IDENTIFIER(self):
            return self.getToken(ShirotsumeParser.IDENTIFIER, 0)

        def move_vector(self):
            return self.getTypedRuleContext(ShirotsumeParser.Move_vectorContext,0)


        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ShirotsumeParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(ShirotsumeParser.ExpressionContext,i)


        def OPERATOR(self):
            return self.getToken(ShirotsumeParser.OPERATOR, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ShirotsumeParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 48
        self.enterRecursionRule(localctx, 48, self.RULE_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 271
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,22,self._ctx)
            if la_ == 1:
                self.state = 260
                self.match(ShirotsumeParser.NUMBER)
                pass

            elif la_ == 2:
                self.state = 261
                self.match(ShirotsumeParser.STRING)
                pass

            elif la_ == 3:
                self.state = 262
                self.match(ShirotsumeParser.BOOL)
                pass

            elif la_ == 4:
                self.state = 263
                self.match(ShirotsumeParser.LITERAL)
                pass

            elif la_ == 5:
                self.state = 264
                self.match(ShirotsumeParser.COLOR)
                pass

            elif la_ == 6:
                self.state = 265
                self.match(ShirotsumeParser.IDENTIFIER)
                pass

            elif la_ == 7:
                self.state = 266
                self.move_vector()
                pass

            elif la_ == 8:
                self.state = 267
                self.match(ShirotsumeParser.T__7)
                self.state = 268
                self.expression(0)
                self.state = 269
                self.match(ShirotsumeParser.T__8)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 278
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,23,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    localctx = ShirotsumeParser.ExpressionContext(self, _parentctx, _parentState)
                    self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                    self.state = 273
                    if not self.precpred(self._ctx, 1):
                        from antlr4.error.Errors import FailedPredicateException
                        raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                    self.state = 274
                    self.match(ShirotsumeParser.OPERATOR)
                    self.state = 275
                    self.expression(2) 
                self.state = 280
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,23,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class OperateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(ShirotsumeParser.IDENTIFIER, 0)

        def ASSIGNMENT_OPERATOR(self):
            return self.getToken(ShirotsumeParser.ASSIGNMENT_OPERATOR, 0)

        def expression(self):
            return self.getTypedRuleContext(ShirotsumeParser.ExpressionContext,0)


        def RIGHT_OPERATOR(self):
            return self.getToken(ShirotsumeParser.RIGHT_OPERATOR, 0)

        def getRuleIndex(self):
            return ShirotsumeParser.RULE_operate

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOperate" ):
                listener.enterOperate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOperate" ):
                listener.exitOperate(self)




    def operate(self):

        localctx = ShirotsumeParser.OperateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_operate)
        try:
            self.state = 286
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,24,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 281
                self.match(ShirotsumeParser.IDENTIFIER)
                self.state = 282
                self.match(ShirotsumeParser.ASSIGNMENT_OPERATOR)
                self.state = 283
                self.expression(0)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 284
                self.match(ShirotsumeParser.IDENTIFIER)
                self.state = 285
                self.match(ShirotsumeParser.RIGHT_OPERATOR)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[24] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 1)
         




