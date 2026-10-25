#!/usr/bin/env bash
# Instala y levanta MySQL 8.4.10 (configuración por defecto, ONLY_FULL_GROUP_BY incluido)
# en Colab o cualquier Linux x86_64. Uso:  bash scripts/instalar_mysql_colab.sh
set -e
URL="https://downloads.mysql.com/archives/get/p/23/file/mysql-8.4.10-linux-glibc2.17-x86_64-minimal.tar.xz"

if [ ! -x /opt/mysql/bin/mysqld ]; then
  apt-get -qq update >/dev/null
  apt-get -qq install -y libaio1 libnuma1 >/dev/null 2>&1 || {
    # Ubuntu 24.04 renombró libaio1 -> libaio1t64
    apt-get -qq install -y libaio1t64 libnuma1 >/dev/null
    ln -sf /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
  }
  wget -q "$URL" -O /tmp/mysql.tar.xz
  tar xf /tmp/mysql.tar.xz -C /opt
  mv /opt/mysql-8.4.10-linux-glibc2.17-x86_64-minimal /opt/mysql
fi

if ! /opt/mysql/bin/mysqladmin -uroot -S /tmp/mysql.sock ping >/dev/null 2>&1; then
  if [ ! -d /opt/mysql-data/mysql ]; then
    mkdir -p /opt/mysql-data
    /opt/mysql/bin/mysqld --initialize-insecure --user=root --datadir=/opt/mysql-data >/tmp/mysql-init.log 2>&1
  fi
  nohup /opt/mysql/bin/mysqld --user=root --datadir=/opt/mysql-data --socket=/tmp/mysql.sock \
        --port=3306 --mysqlx=OFF > /tmp/mysqld.log 2>&1 &
  for i in $(seq 1 60); do
    /opt/mysql/bin/mysqladmin -uroot -S /tmp/mysql.sock ping >/dev/null 2>&1 && break
    sleep 1
  done
fi
/opt/mysql/bin/mysql -uroot -S /tmp/mysql.sock -e "SELECT VERSION() AS version, @@sql_mode AS sql_mode;"
