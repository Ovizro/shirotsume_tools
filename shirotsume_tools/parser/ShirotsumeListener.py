# Generated from ./Shirotsume.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .ShirotsumeParser import ShirotsumeParser
else:
    from ShirotsumeParser import ShirotsumeParser

# This class defines a complete listener for a parse tree produced by ShirotsumeParser.
class ShirotsumeListener(ParseTreeListener):

    # Enter a parse tree produced by ShirotsumeParser#program.
    def enterProgram(self, ctx:ShirotsumeParser.ProgramContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#program.
    def exitProgram(self, ctx:ShirotsumeParser.ProgramContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#declaration.
    def enterDeclaration(self, ctx:ShirotsumeParser.DeclarationContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#declaration.
    def exitDeclaration(self, ctx:ShirotsumeParser.DeclarationContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#macro_declaration.
    def enterMacro_declaration(self, ctx:ShirotsumeParser.Macro_declarationContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#macro_declaration.
    def exitMacro_declaration(self, ctx:ShirotsumeParser.Macro_declarationContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#class_declaration.
    def enterClass_declaration(self, ctx:ShirotsumeParser.Class_declarationContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#class_declaration.
    def exitClass_declaration(self, ctx:ShirotsumeParser.Class_declarationContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#method_declaration.
    def enterMethod_declaration(self, ctx:ShirotsumeParser.Method_declarationContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#method_declaration.
    def exitMethod_declaration(self, ctx:ShirotsumeParser.Method_declarationContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#method_body.
    def enterMethod_body(self, ctx:ShirotsumeParser.Method_bodyContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#method_body.
    def exitMethod_body(self, ctx:ShirotsumeParser.Method_bodyContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#page_declaration.
    def enterPage_declaration(self, ctx:ShirotsumeParser.Page_declarationContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#page_declaration.
    def exitPage_declaration(self, ctx:ShirotsumeParser.Page_declarationContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#page_body.
    def enterPage_body(self, ctx:ShirotsumeParser.Page_bodyContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#page_body.
    def exitPage_body(self, ctx:ShirotsumeParser.Page_bodyContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#statement.
    def enterStatement(self, ctx:ShirotsumeParser.StatementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#statement.
    def exitStatement(self, ctx:ShirotsumeParser.StatementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#operate_statement.
    def enterOperate_statement(self, ctx:ShirotsumeParser.Operate_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#operate_statement.
    def exitOperate_statement(self, ctx:ShirotsumeParser.Operate_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#function_call.
    def enterFunction_call(self, ctx:ShirotsumeParser.Function_callContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#function_call.
    def exitFunction_call(self, ctx:ShirotsumeParser.Function_callContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#function_arguments.
    def enterFunction_arguments(self, ctx:ShirotsumeParser.Function_argumentsContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#function_arguments.
    def exitFunction_arguments(self, ctx:ShirotsumeParser.Function_argumentsContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#wait_statement.
    def enterWait_statement(self, ctx:ShirotsumeParser.Wait_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#wait_statement.
    def exitWait_statement(self, ctx:ShirotsumeParser.Wait_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#call_statement.
    def enterCall_statement(self, ctx:ShirotsumeParser.Call_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#call_statement.
    def exitCall_statement(self, ctx:ShirotsumeParser.Call_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#far_call_statement.
    def enterFar_call_statement(self, ctx:ShirotsumeParser.Far_call_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#far_call_statement.
    def exitFar_call_statement(self, ctx:ShirotsumeParser.Far_call_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#shift_statement.
    def enterShift_statement(self, ctx:ShirotsumeParser.Shift_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#shift_statement.
    def exitShift_statement(self, ctx:ShirotsumeParser.Shift_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#control_statement.
    def enterControl_statement(self, ctx:ShirotsumeParser.Control_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#control_statement.
    def exitControl_statement(self, ctx:ShirotsumeParser.Control_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#if_statement.
    def enterIf_statement(self, ctx:ShirotsumeParser.If_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#if_statement.
    def exitIf_statement(self, ctx:ShirotsumeParser.If_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#while_statement.
    def enterWhile_statement(self, ctx:ShirotsumeParser.While_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#while_statement.
    def exitWhile_statement(self, ctx:ShirotsumeParser.While_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#select_statement.
    def enterSelect_statement(self, ctx:ShirotsumeParser.Select_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#select_statement.
    def exitSelect_statement(self, ctx:ShirotsumeParser.Select_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#case_statement.
    def enterCase_statement(self, ctx:ShirotsumeParser.Case_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#case_statement.
    def exitCase_statement(self, ctx:ShirotsumeParser.Case_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#return_statement.
    def enterReturn_statement(self, ctx:ShirotsumeParser.Return_statementContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#return_statement.
    def exitReturn_statement(self, ctx:ShirotsumeParser.Return_statementContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#move_vector_item.
    def enterMove_vector_item(self, ctx:ShirotsumeParser.Move_vector_itemContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#move_vector_item.
    def exitMove_vector_item(self, ctx:ShirotsumeParser.Move_vector_itemContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#move_vector.
    def enterMove_vector(self, ctx:ShirotsumeParser.Move_vectorContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#move_vector.
    def exitMove_vector(self, ctx:ShirotsumeParser.Move_vectorContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#expression.
    def enterExpression(self, ctx:ShirotsumeParser.ExpressionContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#expression.
    def exitExpression(self, ctx:ShirotsumeParser.ExpressionContext):
        pass


    # Enter a parse tree produced by ShirotsumeParser#operate.
    def enterOperate(self, ctx:ShirotsumeParser.OperateContext):
        pass

    # Exit a parse tree produced by ShirotsumeParser#operate.
    def exitOperate(self, ctx:ShirotsumeParser.OperateContext):
        pass



del ShirotsumeParser