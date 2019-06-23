#/usr/bin/env sh
apt-get update
apt-get install python3-setuptools -y
apt-get install git -y
apt-get install build-essential -y 
apt-get install cmake -y
apt-get install python3-pip -y
apt-get install python3-pytest-cov -y

python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements_dev.txt



mkdir setup
cd setup

git clone -b next https://github.com/aquynh/capstone
cd capstone
CAPSTONE_ARCHS="arm aarch64 x86" ./make.sh
./make.sh install
mkdir /usr/lib/python3.5/site-packages/

cd bindings
cd python
python3 setup.py build install
cd ..
cd ..
cd ..

git clone https://github.com/keystone-engine/keystone
cd keystone
mkdir build
cd build
#../make-share.sh
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=ON -DLLVM_TARGETS_TO_BUILD="AArch64;X86" -G "Unix Makefiles" ..
make -j8
sudo make install
sudo ldconfig
#make install
kstool x32 "add eax, ebx"
cd ..
cd bindings
cd python
python3 setup.py install
cd ..
cd ..
cd ..

git clone https://github.com/unicorn-engine/unicorn
cd unicorn
UNICORN_QEMU_FLAGS="--python=/usr/bin/python2.7" ./make.sh
./make.sh install
cd bindings
cd python
python3 setup.py install
cd ..
cd ..
cd ..

# out of setup
cd ..
pwd
echo "does it work here?"
python3 simple.py


cd db
python3 setup.py install
cd ..
python3 ./db/test.py
python3 ./test/run.py


#pytest --cov=test test/test_coveralls.py
python3 -m pytest --cov=test test/test_coveralls.py
python3 -m coveralls