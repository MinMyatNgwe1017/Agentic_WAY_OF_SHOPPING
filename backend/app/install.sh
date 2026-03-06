sudo apt upgrade
sudo apt update
python3 -m pip install --upgrade meson ninja
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

apt install pkg-config libcairo2-dev

pip install -r requirement.txt

sudo apt-get remove -y nodejs npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

sudo apt-get install -y nodejs

sudo dpkg --configure -a
sudo apt autoremove
sudo apt --fix-broken install
