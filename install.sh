#/usr/bin/env sh
apt-get install python-setuptools
python -m pip install -r requirements.txt

apt-get update
apt-get install git -y
apt-get install build-essential -y 
apt-get install cmake -y
apt-get install python2.7 -y

mkdir setup
cd setup

git clone -b next https://github.com/aquynh/capstone
cd capstone
./make.sh
./make.sh install

cd bindings
cd python
python setup.py install
cd ..
cd ..

cd ..

git clone https://github.com/keystone-engine/keystone
cd keystone
mkdir build
cd build
../make-share.sh
make install
cd ..
cd bindings
cd python
python setup.py install
cd ..
cd ..
cd ..

git clone https://github.com/unicorn-engine/unicorn
cd unicorn
UNICORN_QEMU_FLAGS="--python=/usr/bin/python2.7" ./make.sh
./make.sh install
cd bindings
cd python
python setup.py install
cd ..
cd ..

cd ..
cd ..

cd db
python setup.py install
cd ..

ldconfig

echo "should be ready to go"
