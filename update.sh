#!/bin/bash

# --·-·-·-·-·-·-
# 更新系统GCC版本
# --·-·-·-·-·-·-

echo "Updating GCC version..."
sudo yum groupinstall "Development Tools" -y
sudo yum install mpfr-devel gmp-devel libmpc-devel -y

# ** 更新GMP库 **
echo "Installing GMP..."
wget https://ftp.gnu.org/gnu/gmp/gmp-6.2.1.tar.xz
tar -xvf gmp-6.2.1.tar.xz
cd gmp-6.2.1

./configure --prefix=$HOME/usr
make -j$(nproc)
make install
cd ..

# ** 更新MPFR库 **
echo "Installing MPFR..."
wget https://ftp.gnu.org/gnu/mpfr/mpfr-4.1.0.tar.xz
tar -xvf mpfr-4.1.0.tar.xz
cd mpfr-4.1.0

./configure --prefix=$HOME/usr --with-gmp=$HOME/usr
make -j$(nproc)
make install
cd ..

# ** 更新MPC库 **
echo "Installing MPC..."
wget https://ftp.gnu.org/gnu/mpc/mpc-1.2.1.tar.gz
tar -xvzf mpc-1.2.1.tar.gz
cd mpc-1.2.1

./configure --prefix=$HOME/usr --with-gmp=$HOME/usr --with-mpfr=$HOME/usr
make -j$(nproc)
make install
cd ..

# ** 更新GCC版本 **
echo "Installing GCC..."
wget http://ftp.gnu.org/gnu/gcc/gcc-8.4.0/gcc-8.4.0.tar.gz
tar -xzvf gcc-8.4.0.tar.gz
cd gcc-8.4.0

./configure --prefix=$HOME/usr \
            --enable-languages=c,c++ \
            --with-gmp=$HOME/usr \
            --with-mpfr=$HOME/usr \
            --with-mpc=$HOME/usr \
            --disable-multilib
make -j$(nproc)  # 使用所有可用的 CPU 核心加速编译
sudo make install
cd ..

# ** 更新环境变量 **
echo "Updating environment variables..."
export PATH=$HOME/usr/bin:$PATH
export LD_LIBRARY_PATH=$HOME/usr/lib:$HOME/usr/lib64:$LD_LIBRARY_PATH

echo "export PATH=$HOME/usr/bin:$PATH" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=$HOME/usr/lib:$HOME/usr/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc
source ~/.bashrc

# --·-·-·-·-·-·-·-
# 更新系统Python版本
# --·-·-·-·-·-·-·-

# ** 设置环境变量 **
echo "Setting environment variables..."
echo "export PATH=\$HOME/usr/bin:\$PATH" >> $HOME/.bashrc
echo "export LD_LIBRARY_PATH=\$HOME/usr/lib:\$HOME/usr/lib64:\$LD_LIBRARY_PATH" >> $HOME/.bashrc
echo "export C_INCLUDE_PATH=\$HOME/usr/include:\$C_INCLUDE_PATH" >> $HOME/.bashrc
source $HOME/.bashrc

# ** 安装依赖项 **
echo "Installing dependencies..."
sudo yum install -y libffi-devel openssl-devel sqlite-devel

# ** 更新 sqlite3 **
echo "Updating SQLite..."
wget https://www.sqlite.org/2023/sqlite-autoconf-3440200.tar.gz
tar -xzvf sqlite-autoconf-3440200.tar.gz
cd sqlite-autoconf-3440200
./configure
make install
cd ..

# ** 安装 OpenSSL **
echo "Installing OpenSSL..."
wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz
tar -zxvf openssl-1.1.1w.tar.gz
cd openssl-1.1.1w
bash ./config --prefix=$HOME/usr/openssl-1.1.1w
make
make install
cd ..

# ** 安装 libffi（如果需要则添加）**
# echo "Skipping libffi installation (if needed, uncomment below)..."
# wget https://github.com/libffi/libffi/releases/download/v3.4.4/libffi-3.4.4.tar.gz
# tar -zxvf libffi-3.4.4.tar.gz
# cd libffi-3.4.4
# bash ./configure --prefix=$HOME/usr
# make -j8
# make install
# cd ..

# ** 安装 glibc（如果需要则添加）**
# echo "Skipping glibc installation (if needed, uncomment below)..."
# wget https://ftp.gnu.org/gnu/glibc/glibc-2.38.tar.gz
# tar -zxvf glibc-2.38.tar.gz
# mkdir glibc-build
# cd glibc-build
# ../glibc-2.38/configure --prefix=$HOME/usr
# make
# make install
# cd ..

# ** 安装 Python **
echo "Installing Python..."
wget https://www.python.org/ftp/python/3.10.13/Python-3.10.13.tar.xz
tar xf Python-3.10.13.tar.xz
cd Python-3.10.13
LD_RUN_PATH=/usr/local/lib ./configure --prefix=$HOME/usr \
        --with-openssl=$HOME/usr/openssl-1.1.1w \
        --with-openssl-rpath=auto \
        --enable-loadable-sqlite-extensions
make -j$(nproc)
make install
cd ..

# ** 更新环境变量 **
echo "Updating Python environment variables..."
echo "export PATH=$HOME/usr/bin:$PATH" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=$HOME/usr/lib:$HOME/usr/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc
echo "export C_INCLUDE_PATH=$HOME/usr/include:$C_INCLUDE_PATH" >> ~/.bashrc
source ~/.bashrc

echo "Installation completed successfully!"
