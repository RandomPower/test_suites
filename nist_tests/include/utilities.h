/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
              U T I L I T Y  F U N C T I O N  P R O T O T Y P E S 
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

int		displayGeneratorOptions();
int		generatorOptions(char** streamFile);
void	chooseTests();
void	fixParameters();
void	fileBasedBitStreams(char *streamFile,int bitmode);
void	readBinaryDigitsInASCIIFormat(FILE *fp, char *streamFile);
void	readHexDigitsInBinaryFormat(FILE *fp);
int		convertToBits(BYTE *x, int xBitLength, int bitsNeeded, int *num_0s, int *num_1s, int *bitsRead);
void	openOutputStreams(int option, int numberofbitstreams);
void	invokeTestSuite(int option, char *streamFile, int bitmode);
void	nist_test_suite();
//char*	NISTFOLDER;
