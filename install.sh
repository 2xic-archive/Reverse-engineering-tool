pip3 install -r requirements.txt


sudo apt-get install cmake -y

mkdir setup
cd setup

git clone -b next https://github.com/aquynh/capstone
cd capstone
./make.sh
sudo ./make.sh install

git clone https://github.com/keystone-engine/keystone
cd keystone
mkdir build
cd build
../make-share.sh
sudo make install
cd ..
cd ..

echo "should be ready to go"