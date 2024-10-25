#!/bin/bash

# Обновление списка пакетов
sudo apt-get update

export DEBIAN_FRONTEND=noninteractive

# Установка необходимых пакетов
sudo apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" nvidia-driver-550-server
sudo apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" nvidia-utils-550-server
sudo apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" python3-pip
sudo apt install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" python3-venv

# Создание директории для виртуальных окружений
mkdir -p environments

# Создание виртуального окружения
python3 -m venv environments/hack

# Активация виртуального окружения
source environments/hack/bin/activate

# Установка Jupyter и основных библиотек
sudo pip install jupyter
sudo pip install numpy pandas scikit-learn torch transformers  # Библиотеки для ML и NLP

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Установка завершена."