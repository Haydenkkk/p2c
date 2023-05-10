#include <stdio.h>
int a[5];
int x, y;
void __func_readarray() {
	int i;
	i=0;
	while(i<5) {
		scanf("%d", &y);
		a[i]=y;
		i=i+1;
	}
}
void __func_quicksort(int l,int h) {
	int i, j, k, m;
	i=l;
	j=h;
	k=a[i];
	if(l<h) {
		while(i<j) {
			while((a[j]>=k)&&(i<j)) {
				j=j-1;
			}
			a[i]=a[j];
			while((a[i]<=k)&&(i<j)) {
				i=i+1;
			}
			a[j]=a[i];
		}
		a[i]=k;
		__func_quicksort(l,i-1);
		__func_quicksort(j+1,h);
	}
	else {
		m=0;
	}
}
int main() {
	x=0;
	__func_readarray();
	__func_quicksort(0,4);
	while(x<5) {
		y=a[x];
		printf("%d\n", y);
		x=x+1;
	}
	return 0;
}
