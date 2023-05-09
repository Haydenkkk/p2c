{ 测试语法分析中类型声明和转化 }
{ 计算Cmn的值 }
Program Cmn(input, output) ;
function fac(x:integer) :integer;
var
    i:integer;
    a:boolean;
    b:char;
begin
    fac:=1;
    a:=x;
    { 由integer 到 boolean }
    for i:=1 to x do
        fac: =fac*i ;
    b:=fac;
    { 由integer 到 char }
end;
function c(a, b: integer) :real;
    begin
    c:=fac(a)/fac(b)*fac(a-b)
    { 由integer 到 real }

end;
begin
    write('c(9，3)=',c(9,3));
    write('c(8，5)=',c(8,5));
end.