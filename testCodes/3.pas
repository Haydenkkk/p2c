{ 对作用域进行测试 }
program range (input, output) ;
var
    x, y : integer;
procedure p();
var
    x, z :integer;
begin
    x:=10;y:=y+1;z:=10;
    write(x, y, z);
end;
begin
    x:=1;y:=1;
    write(x, y);
    p();
    write(x, y);
end.