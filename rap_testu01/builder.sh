mkdir testu01lib
CUR_DIR=$(pwd)

cd TestU01-2009

./configure --prefix="$CUR_DIR"/testu01lib
make clean
make
make install

cd ..

mkdir build
cd build
cmake ..
make