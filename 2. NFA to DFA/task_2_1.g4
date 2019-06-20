grammar task_2_1;

REG     : ('AX'|'BX'|'CX'|'DX');
MEM     : '['REG']';
INT	    : [0-9]+;
BIN     : [0-1]+'b';
CMD_1   : 'AAA';
CMD_2   : ('ADD'|'INC');
COMMA   : ',' -> skip;
SPACE   : ' ' -> skip;
IGNORE  : [\r\n\t]+ -> skip;

expr: CMD_1
    | CMD_2 REG (INT|BIN);

start: (expr)*;