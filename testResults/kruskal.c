#include <stdio.h>
int a[101],b[101],v[101],p[101];
int n, m, i, ans, tot, x, y;
void __func_sort(int l,int r) {
	int i, j, x, y;
	i=l;
	j=r;
	x=v[(l+r)div2];
	while(i<=j) {
		while(v[i]<x) {
			i=i+1;
		}
		while(x<v[j]) {
			j=j-1;
		}
		if(None) {
			y=v[i];
			v[i]=v[j];
			v[j]=y;
			y=a[i];
			a[i]=a[j];
			a[j]=y;
			y=b[i];
			b[i]=b[j];
			b[j]=y;
			i=i+1;
			j=j-1;
		}
	}
	if(l<j) {
		__func_sort(l,j);
	}
	if(i<r) {
		__func_sort(i,r);
	}
}
int __func_doit(int x) {
	int doit;
	if(p[x]==x) {
		ans=x;
		doit=x;
	}
	else {
		p[x]=ans;
		doit=__func_doit(p[x]);
	}
	return doit;
}
int main() {
	scanf("%d%d", &n, &m);
	for(int i = 1; i <= m; i ++) {
		scanf("%d%d%d", &a[i], &b[i], &v[i]);
	}
	__func_sort(1,m);
	for(int i = 1; i <= n; i ++) {
		p[i]=i;
	}
	for(int i = 1; i <= m; i ++) {
		x=__func_doit(a[i]);
		y=__func_doit(b[i]);
		if((x<>y)) {
			p[x]=y;
			tot=tot+v[i];
		}
	}
	printf("%d\n", tot);
	return 0;
}
