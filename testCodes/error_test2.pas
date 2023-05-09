{ test2是对于语法分析的测试 }
{ 输入10个数字，求最大最小和平均值 }
Porgram ten(input,output);
{ 拼写错误 }
var
    a,s,max,min,avg:real;
    i:integer;
beign
    read(a);
    s:=a;
    max:=a;
    min:=a;
    for i:=2 to 10 
    { 文法错误 }
        begin
            read(a)p;
            s:=s+a);
            { 括号不匹配 }
            if a>max Then
                max:=a
            Else
                if a<min Then
                    min:=a;
        end;
    avg:=s/i;
    write(max,min,avg);
end.