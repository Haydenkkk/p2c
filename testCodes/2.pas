{ 测试引用传递转化到C时的情况 }
{ Pascal-S的输出应该为 1 6 3 }
Program example(input, output);
var
    x,y,z:integer;
procedure s (x : integer; var y:integer);
var
    z:integer;
begin
    x:=5; y:=6; z:=7;
end;
begin
    x:=1; y:=2; z:=3;
    s(x,y);
    write(x,y,z);
end.