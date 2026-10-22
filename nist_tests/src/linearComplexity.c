#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "../include/externs.h"
#include "../include/cephes.h"  
#include <stdint.h>

/* [RaP] Berlekamp-Massey on 64-bit words.
   Same algorithm and same update conditions as the original NIST loop (C, B, L, m, N),
   with the polynomials stored as packed bit vectors: it returns the same integer L. */
static uint64_t
rp_get64(const uint64_t *a, int pos)
{
	int w = pos >> 6, b = pos & 63;
	return b ? (a[w] >> b) | (a[w+1] << (64-b)) : a[w];
}

static int
rp_linear_complexity(const BitSequence *s, int M, uint64_t *C, uint64_t *B, uint64_t *T, uint64_t *R, int W)
{
	int i, k, N_, L = 0, m = -1, shift, ws, bs;
	uint64_t d, cw, v;

	memset(C, 0, W*sizeof(uint64_t)); memset(B, 0, W*sizeof(uint64_t)); memset(R, 0, (W+1)*sizeof(uint64_t));
	C[0] = 1; B[0] = 1;
	for ( k=0; k<M; k++ )                       /* R = reversed sequence: bit k = s[M-1-k] */
		if ( s[M-1-k] )
			R[k>>6] |= (uint64_t)1 << (k&63);
	for ( N_=0; N_<M; N_++ ) {
		/* d = s[N] + sum_{i=1..L} C[i]*s[N-i]  (mod 2);  s[N-i] = R[M-1-N+i] */
		d = 0;
		for ( i=0; i<=(L>>6); i++ ) {
			cw = C[i];
			if ( i == (L>>6) && (L&63) != 63 )
				cw &= ((uint64_t)1 << ((L&63)+1)) - 1;
			d ^= cw & rp_get64(R, M-1-N_ + 64*i);
		}
		if ( __builtin_parityll(d) ) {
			memcpy(T, C, W*sizeof(uint64_t));
			shift = N_ - m; ws = shift >> 6; bs = shift & 63;   /* C = C + x^(N-m) * B */
			for ( i=W-1; i>=ws; i-- ) {
				v = B[i-ws] << bs;
				if ( bs && i-ws-1 >= 0 )
					v |= B[i-ws-1] >> (64-bs);
				C[i] ^= v;
			}
			if ( L <= N_/2 ) {
				L = N_ + 1 - L;
				m = N_;
				memcpy(B, T, W*sizeof(uint64_t));
			}
		}
	}
	return L;
}

void
LinearComplexity(int M, int n)
{
	int       i, ii, j, d, N, L, m, N_, parity, sign, K = 6;
	double    p_value, T_, mean, nu[7], chi2;
	double    pi[7] = { 0.01047, 0.03125, 0.12500, 0.50000, 0.25000, 0.06250, 0.020833 };
	BitSequence  *T = NULL, *P = NULL, *B_ = NULL, *C = NULL;
	
	N = (int)floor(n/M);
	int       rpW = (M + 63)/64 + 1;
	uint64_t  *rpC = calloc(rpW, 8), *rpB = calloc(rpW, 8), *rpT = calloc(rpW, 8), *rpR = calloc(rpW+1, 8);
	if ( ((B_ = (BitSequence *) calloc(M, sizeof(BitSequence))) == NULL) ||
		 ((C  = (BitSequence *) calloc(M, sizeof(BitSequence))) == NULL) ||
		 ((P  = (BitSequence *) calloc(M, sizeof(BitSequence))) == NULL) ||
		 ((T  = (BitSequence *) calloc(M, sizeof(BitSequence))) == NULL) ) {
		printf("Insufficient Memory for Work Space:: Linear Complexity Test\n");
		if ( B_ != NULL )
			free(B_);
		if ( C != NULL )
			free(C);
		if ( P != NULL )
			free(P);
		if ( T != NULL )
			free(T);
		return;
	}


	fprintf(stats[TEST_LINEARCOMPLEXITY], "-----------------------------------------------------\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "\tL I N E A R  C O M P L E X I T Y\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "-----------------------------------------------------\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "\tM (substring length)     = %d\n", M);
	fprintf(stats[TEST_LINEARCOMPLEXITY], "\tN (number of substrings) = %d\n", N);
	fprintf(stats[TEST_LINEARCOMPLEXITY], "-----------------------------------------------------\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "        F R E Q U E N C Y                            \n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "-----------------------------------------------------\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "  C0   C1   C2   C3   C4   C5   C6    CHI2    P-value\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "-----------------------------------------------------\n");
	fprintf(stats[TEST_LINEARCOMPLEXITY], "\tNote: %d bits were discarded!\n", n%M);

	for ( i=0; i<K+1; i++ )
		nu[i] = 0.00;
	for ( ii=0; ii<N; ii++ ) {
		/* [RaP] same L as the original Berlekamp-Massey loop, computed on 64-bit words */
		L = rp_linear_complexity(&epsilon[ii*M], M, rpC, rpB, rpT, rpR, rpW);
		if ( (parity = (M+1)%2) == 0 ) 
			sign = -1;
		else 
			sign = 1;
		mean = M/2.0 + (9.0+sign)/36.0 - 1.0/pow(2, M) * (M/3.0 + 2.0/9.0);
		if ( (parity = M%2) == 0 )
			sign = 1;
		else 
			sign = -1;
		T_ = sign * (L - mean) + 2.0/9.0;
		
		if ( T_ <= -2.5 )
			nu[0]++;
		else if ( T_ > -2.5 && T_ <= -1.5 )
			nu[1]++;
		else if ( T_ > -1.5 && T_ <= -0.5 )
			nu[2]++;
		else if ( T_ > -0.5 && T_ <= 0.5 )
			nu[3]++;
		else if ( T_ > 0.5 && T_ <= 1.5 )
			nu[4]++;
		else if ( T_ > 1.5 && T_ <= 2.5 )
			nu[5]++;
		else
			nu[6]++;
	}
	chi2 = 0.00;
	for ( i=0; i<K+1; i++ ) 
		fprintf(stats[TEST_LINEARCOMPLEXITY], "%4d ", (int)nu[i]);
	for ( i=0; i<K+1; i++ )
		chi2 += pow(nu[i]-N*pi[i], 2) / (N*pi[i]);
	p_value = cephes_igamc(K/2.0, chi2/2.0);

	fprintf(stats[TEST_LINEARCOMPLEXITY], "%9.6f%9.6f\n", chi2, p_value); fflush(stats[TEST_LINEARCOMPLEXITY]);
	fprintf(results[TEST_LINEARCOMPLEXITY], "%f\n", p_value); fflush(results[TEST_LINEARCOMPLEXITY]);

	free(B_);
	free(P);
	free(C);
	free(T);
	free(rpC); free(rpB); free(rpT); free(rpR);
}
