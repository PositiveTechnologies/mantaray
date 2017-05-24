int isqrt(int a, int guess) {
	int x;
	if (guess == (x = (guess + a/guess)/2))
		return guess;
	return isqrt(a, x);
}

int num;
float f;

void main(void) {
	num = iread();
	iprint(isqrt(num, num/2));

	f = fread();
	fprint(f * 2.0);
}