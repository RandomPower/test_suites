#pragma once

struct Running_Test
{
    Running_Test() : test_size(0), test_number(0) {}
    Running_Test(int ta, int tb)
    {
        test_number = tb;
        test_size = ta;
    }
    Running_Test(const Running_Test &rStruct)
    {
        test_size = rStruct.test_size;
        test_number = rStruct.test_number;
        // std::cout << "in copy contructor" << std::endl;
    }
    int test_size;
    int test_number;
};

#define USE_LONGLONG

#define CRUSH_NUM  96
#define THOUSAND 1000
#define MILLION (THOUSAND * THOUSAND)
#define BILLION (THOUSAND * MILLION)

// Here the list of the tests in Crush  format: NAME - required number of data . Position in list is array position

#define SERIALOVER_T2 Running_Test(500 * MILLION, 1) // Starting at position 1 - 0 position is always 0
#define SERIALOVER_T4 Running_Test(300 * MILLION, 2)

#define COLLISIONOVER_T2 Running_Test(100 * MILLION, 3)
#define COLLISIONOVER_T2_10 Running_Test(100 * MILLION, 4)
#define COLLISIONOVER_T4 Running_Test(100 * MILLION, 5)
#define COLLISIONOVER_T4_20 Running_Test(100 * MILLION, 6)
#define COLLISIONOVER_T8 Running_Test(100 * MILLION, 7)
#define COLLISIONOVER_T8_25 Running_Test(100 * MILLION, 8)
#define COLLISIONOVER_T20 Running_Test(100 * MILLION, 9)
#define COLLISIONOVER_T20_28 Running_Test(100 * MILLION, 10)

#ifdef USE_LONGLONG

#if LONG_MAX <= 2147483647L
#define SMARSA_BIRTHDAY_SPACINGS_2 Running_Test(200 * MILLION, 11)
#else

#define SMARSA_BIRTHDAY_SPACINGS_2 Running_Test(200 * MILLION, 11)
#endif

#define SMARSA_BIRTHDAY_SPACINGS_3 Running_Test(300 * MILLION, 12)
#define SMARSA_BIRTHDAY_SPACINGS_4 Running_Test(400 * MILLION, 13)
#define SMARSA_BIRTHDAY_SPACINGS_7_0 Running_Test(420 * MILLION, 14)
#define SMARSA_BIRTHDAY_SPACINGS_7_7 Running_Test(420 * MILLION, 15)
#define SMARSA_BIRTHDAY_SPACINGS_8_14 Running_Test(480 * MILLION, 16)
#define SMARSA_BIRTHDAY_SPACINGS_8_22 Running_Test(480 * MILLION, 17)

#else

#define SMARSA_BIRTHDAY_SPACINGS_2_10 Running_Test(4 * MILLION / 10, 11) // do not USE_LONG
#define SMARSA_BIRTHDAY_SPACINGS_3 Running_Test(4 * MILLION / 10, 12)
#define SMARSA_BIRTHDAY_SPACINGS_4 Running_Test(4 * MILLION / 10, 13)
#define SMARSA_BIRTHDAY_SPACINGS_13_0 Running_Test(4 * MILLION / 10, 14)
#define SMARSA_BIRTHDAY_SPACINGS_13_10 Running_Test(4 * MILLION / 10, 15)
#define SMARSA_BIRTHDAY_SPACINGS_13_20 Running_Test(4 * MILLION / 10, 16)
#define SMARSA_BIRTHDAY_SPACINGS_13_26 Running_Test(4 * MILLION / 10, 17)

#endif // end of ifdef USE_LONG_LONG - starting from 17

#define CLOSEPAIRS_2 Running_Test(40 * MILLION, 18)
#define CLOSEPAIRS_3 Running_Test(60 * MILLION, 19)
#define CLOSEPAIRS_7 Running_Test(70 * MILLION, 20)
#define CLOSEPAIRSBITMATCH_2 Running_Test(32 * MILLION, 21)
#define CLOSEPAIRSBITMATCH_4 Running_Test(32 * MILLION, 22)

#define SIMPOKER_16_0 Running_Test(640 * MILLION, 23)
#define SIMPOKER_16_26 Running_Test(640 * MILLION, 24)
#define SIMPOKER_64_0 Running_Test(640 * MILLION, 25)
#define SIMPOKER_64_24 Running_Test(640 * MILLION, 26)

#define COUPONCOLLECTOR_4_0 Running_Test(400 * MILLION, 27)
#define COUPONCOLLECTOR_4_28 Running_Test(400 * MILLION, 28)
#define COUPONCOLLECTOR_16_0 Running_Test(500 * MILLION, 29)
#define COUPONCOLLECTOR_16_26 Running_Test(500 * MILLION, 30)

#define GAP_0_0 Running_Test(800 * MILLION, 31)
#define GAP_27_0 Running_Test(800 * MILLION, 32)
#define GAP_0_256 Running_Test(1280 * MILLION, 33)
#define GAP_27_256 Running_Test(1280 * MILLION, 34)

#define U01_R0 Running_Test(500 * MILLION, 35)
#define U01_R15 Running_Test(500 * MILLION, 36)

#define PERMUTATION_0 Running_Test(500 * MILLION, 37)
#define PERMUTATION_15 Running_Test(500 * MILLION, 38)

#define COLLPERMUTATION_0 Running_Test(650 * MILLION, 39)
#define COLLPERMUTATION_15 Running_Test(650 * MILLION, 40)

#define MAXOFT_5 Running_Test(500 * MILLION, 41)
// #define MAXOFT_AD_5 Running_Test(500*MILLION,41)

#define MAXOFT_10 Running_Test(500 * MILLION, 42)
// #define MAXOFT_AD_10 Running_Test(10*MILLION,43)

#define MAXOFT_20 Running_Test(200 * MILLION, 43)
// #define MAXOFT_AD_20 Running_Test(10*MILLION,45)

#define MAXOFT_30 Running_Test(300 * MILLION, 44)
// #define MAXOFT_AD_30 Running_Test(10*MILLION,47)

#define SAMPLEPROD_10 Running_Test(100 * MILLION, 45)
#define SAMPLEPROD_30 Running_Test(300 * MILLION, 46)

#define SAMPLEMEAN Running_Test(200 * MILLION, 47)

#define SAMPLECORR Running_Test(500 * MILLION, 48)

#define APPEARENCESPACINGS_0 Running_Test(205 * MILLION, 49)
#define APPEARENCESPACINGS_20 Running_Test(220 * MILLION, 50)

#define WEIGHTDISTRIB_0 Running_Test(512 * MILLION, 51)
#define WEIGHTDISTRIB_8 Running_Test(512 * MILLION, 52)
#define WEIGHTDISTRIB_16 Running_Test(512 * MILLION, 53)
#define WEIGHTDISTRIB_24 Running_Test(512 * MILLION, 54)

#define SUMCOLLECTOR Running_Test(200 * MILLION, 55) // To be checked

#define MATRIXRANK_60x60_0 Running_Test(534 * MILLION, 56)
#define MATRIXRANK_60x60_1 Running_Test(360 * MILLION, 57)
#define MATRIXRANK_300x300_0 Running_Test(150 * MILLION, 58)
#define MATRIXRANK_300x300_1 Running_Test(450 * MILLION, 59)
#define MATRIXRANK_1200x1200_0 Running_Test(96 * MILLION, 60)
#define MATRIXRANK_1200x1200_1 Running_Test(288 * MILLION, 61)

#define SAVIR2 Running_Test(600 * MILLION, 62)

#define GCD_0 Running_Test(200 * MILLION, 63)
#define GCD_10 Running_Test(80000168, 64) // 81*MILLION,64)

#define RWALK_L90_0 Running_Test(150 * MILLION, 65)
#define RWALK_L90_1 Running_Test(90 * MILLION, 66)
#define RWALK_L1000_0 Running_Test(170 * MILLION, 67)
#define RWALK_L1000_1 Running_Test(100 * MILLION, 68)
#define RWALK_L10000_0 Running_Test(167 * MILLION, 69)
#define RWALK_L10000_1 Running_Test(100 * MILLION, 70)

#define LINEARCOMP_0 Running_Test(120 * THOUSAND, 71)  // to be revised
#define LINEARCOMP_29 Running_Test(120 * THOUSAND, 72) // on athos changed to 120*MILLION

#define LEMPELZIV Running_Test(12 * MILLION, 73)

#define FOURIER3_0 Running_Test(27350 * THOUSAND, 74)
#define FOURIER3_20 Running_Test(81950 * THOUSAND, 75)

#define LONGEST_HEAD_0 Running_Test(333334 * THOUSAND, 76)
#define LONGEST_HEAD_20 Running_Test(300000600, 77)

#define PERIOD_IN_STRINGS_0 Running_Test(300 * MILLION, 78)
#define PERIOD_IN_STRINGS_15 Running_Test(300 * MILLION, 79)

#define HAMMING_WEIGHT_2_0 Running_Test(333340 * THOUSAND, 80)
#define HAMMING_WEIGHT_2_20 Running_Test(300 * MILLION, 81)

#define HAMMING_CORR_30 Running_Test(500 * MILLION, 82)
#define HAMMING_CORR_300 Running_Test(500 * MILLION, 83)
#define HAMMING_CORR_1200 Running_Test(400 * MILLION, 84)

#define HAMMING_INDEP_30_0_30 Running_Test(600 * MILLION, 85)
#define HAMMING_INDEP_30_20_30 Running_Test(600 * MILLION, 86)
#define HAMMING_INDEP_300_0_30 Running_Test(600 * MILLION, 87)
#define HAMMING_INDEP_300_20_30 Running_Test(600 * MILLION, 88)
#define HAMMING_INDEP_1200_0_30 Running_Test(800 * MILLION, 89)
#define HAMMING_INDEP_1200_20_30 Running_Test(240 * MILLION, 90)

#define STRING_RUN_0_30 Running_Test(133336000, 91)
#define STRING_RUN_20_10 Running_Test(400 * MILLION, 92)

#define AUTOCOR_0_30_1 Running_Test(333333350, 93)
#define AUTOCOR_20_10_1 Running_Test(500000010, 94)
#define AUTOCOR_0_30_30 Running_Test(333333350, 95)
#define AUTOCOR_20_10_10 Running_Test(500000010, 96)
