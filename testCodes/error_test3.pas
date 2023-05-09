{ test3是对于语义分析的测试 }
{ 求1！+2！+...+10！的和 }
Program sum_fac(input, output) ;
var
    i, j, m: integer;
begin
    s:=0;
    { 无定义，未声明 }
    for j:=1 to 10 do
        begin
        m:=1;
        for j:=1 to i do
            m : =m*j;
        s:=s+m;
    end;
end.