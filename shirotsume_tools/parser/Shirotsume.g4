grammar Shirotsume;

// 文法规则
program : macro_declaration* declaration+;

declaration : class_declaration
            | page_declaration;

// 宏声明
macro_declaration : '#base_path' STRING;

// 类声明
class_declaration : 'class' (LITERAL | TEXT) '{' method_declaration* '}';

// 方法声明
method_declaration : 'method' (LITERAL | TEXT) '{' method_body '}';

// 方法体
method_body : statement*;

// 页面声明
page_declaration : 'page' (LITERAL | TEXT) '{' page_body '}';

// 页面体
page_body : statement*;

// 语句
statement : operate_statement
          | function_call
          | wait_statement
          | call_statement
          | far_call_statement
          | shift_statement
          | control_statement
          | return_statement
          ;

// 函数调用
operate_statement : 'Operate' '(' operate ')' ';';

function_call : LITERAL '(' function_arguments? ')' ';';

// 函数参数
function_arguments : expression (',' expression)*;

wait_statement : 'wait' NUMBER ';';

call_statement : 'call' (LITERAL | STRING | TEXT) ';';

far_call_statement : 'far_call' (LITERAL | STRING | TEXT) ',' LITERAL ';';

shift_statement : 'shift' TEXT ';';

// 控制语句
control_statement : if_statement
                  | while_statement
                  | select_statement;

if_statement : 'if' '(' expression ')' '{' statement* '}' ('else' 'if' '(' expression ')' '{' statement* '}')* ( 'else' '{' statement* '}' )?;

while_statement : 'while' '(' expression ')' '{' statement* '}'?;

select_statement : 'select' '{' case_statement* '}';

case_statement : 'case' STRING ':' '{' statement* '}'?;

return_statement : ('return' | 'scene_return')  ';';

move_vector_item : ('(' NUMBER ',' NUMBER ')') | ('{' NUMBER ',' NUMBER '}');
move_vector : move_vector_item+;

// 表达式
expression : NUMBER
           | STRING
           | BOOL
           | LITERAL
           | COLOR
           | IDENTIFIER
           | move_vector
           | '(' expression ')'
           | expression OPERATOR expression;

operate : IDENTIFIER ASSIGNMENT_OPERATOR expression
        | IDENTIFIER RIGHT_OPERATOR;

// 声明
IDENTIFIER : ('$' | '@') NUMBER;

// 数字
NUMBER : ('+' | '-')? [0-9]+;

// 布尔值
BOOL : 'true' | 'false';

// 字符串
fragment UNICODE_START: [\u00A1-\uFFFF];
fragment UNICODE_CONTINUE: [\u00A0-\uFFFF];

LITERAL : [a-zA-Z_][a-zA-Z0-9_]*;
STRING : '"' (~["] | '\\"')* '"';
TEXT: UNICODE_START UNICODE_CONTINUE*;

// color
COLOR : '#'[0-9a-fA-F]+;

// 运算符
OPERATOR
    : '+'
    | '-'
    | '*'
    | '/'
    | '%'
    | '=='
    | '!='
    | '>='
    | '<='
    | '>'
    | '<'
    | '&&'
    | '||'
    ;

ASSIGNMENT_OPERATOR
    : '='
    | '+='
    | '-='
    | '*='
    | '/='
    | '%='
    | '&='
    | '^='
    | '|='
    ;

RIGHT_OPERATOR
    : '++'
    | '--'
    ;

// 多行注释
COMMENT : '/*' .*? '*/' -> skip;

// 单行注释
LINE_COMMENT : '//' ~[\r\n]* -> skip;

// 空格
WS : [ \t\r\n]+ -> skip;
