# zqhf-oj 入门手册



## 部署

**Requirments:**

- Ubuntu Linux(>=18.04 *建议版本*),Debian Linux (>=10 *建议版本*)或CentOS(>=7)

- GCC/G++ Compiler

- Python3

- Git

  

**Setup:**

- 安装Python3

  **Debian-like系统** `sudo apt install python3`

  **CentOS系统**

  - 安装编译依赖: `yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel libffi-devel openssl`

  - 下载python3源码: `wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz`

  - 安装python3:

    ```bash
    mkdir -p /usr/local/python3
    tar -zxvf Python-3.7.3.tgz
    cd Python-3.7.3
    ./configure --prefix=/usr/local/python3
    make && make install
    ln -s /usr/local/python3/bin/python3 /usr/bin/python3
    echo "export PATH=$PATH:$HOME/bin:/usr/local/python3/bin" >> ~/.bash_profile
    source ~/.bash_profile
    
    # 设置setuptools
    wget --no-check-certificate  https://pypi.python.org/packages/source/s/setuptools/setuptools-19.6.tar.gz
    tar -zxvf setuptools-19.6.tar.gz
    cd setuptools-19.6
    python3 setup.py build
    python3 setup.py install
    
    # 设置pip
    wget --no-check-certificate  https://pypi.python.org/packages/source/p/pip/pip-8.0.2.tar.gz
    tar -zxvf pip-8.0.2.tar.gz
    cd pip-8.0.2
    python3 setup.py build
    python3 setup.py install
    ```

- 安装Git

  **Debian-like系统**: `sudo apt install git`

  **CentOS**: `yum install git`

- 安装编译工具

  **Debian-like系统:** `sudo apt install build-essential`

  **CentOS:** `yum groupinstall "Development Tools"`

- 拉取源代码: `git clone https://github.com.cnpmjs.org/XtherDevTeam/zqhf-oj`

- 进入仓库目录: `cd zqhf-oj`

- 初始化环境: `make init`

- 初始化数据库:

  ```bash
  chou@ubuntu:~/zqhf-oj$ python3
  Python 3.9.5 (default, May 11 2021, 08:20:37)
  [GCC 10.3.0] on linux
  >> import database.init
  >> ^D
  ```

  

- 新开一个tty或terminal标签页执行数据库后端: `python3 ./database_server.py`

- 在主terminal标签页或tty执行: `python3 ./server.py`



## 使用

默认用户为admin，密码为admin

注册邀请码为`enFoZi1pbnZpdGUtY29kZQ==`

**注意:** 目前还有一些功能例如题单等没有完善，开发者将在不久后完成这些功能

Thanks for using! 感谢使用!



> zqhf-oj 华南师范大学附属肇庆学校在线评测系统
>
> Developed by xiaokang00010 由学校学生自行开发

