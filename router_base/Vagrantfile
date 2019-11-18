# -*- mode: ruby -*-
# vi: set ft=ruby :

$INSTALL_BASE = <<SCRIPT
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get -y upgrade
  apt-get -y install build-essential vim vim-nox emacs git
  apt-get -y install python  python-dev  python-setuptools  python-pip
  apt-get -y install python3 python3-dev python3-setuptools python3-pip
  apt-get -y install flex bison traceroute libbz2-dev libssl-dev

  apt-get -y install mininet expect
  apt-get -y install xauth
  apt-get -y install libzeroc-ice-dev
SCRIPT

$INSTALL2 = <<SCRIPT
  pip2 install pip --upgrade
  pip3 install pip --upgrade

  /usr/local/bin/pip2 install zeroc-ice
  /usr/local/bin/pip3 install zeroc-ice

  rm -Rf /opt/pox
  mkdir -p /opt/pox
  # Install POX controller
  git clone -b eel https://github.com/noxrepo/pox /opt/pox

  # Install packet redirector to simpler router and run it as a service
  git clone https://github.com/aa-fiu-classes/py-riddikulus-connector /opt/py-riddikulus-connector
  (cd /opt/py-riddikulus-connector; python2.7 setup.py install)

  cp /vagrant/pox.service /etc/systemd/system/
  systemctl daemon-reload
  systemctl enable pox.service
  systemctl start pox.service
SCRIPT

Vagrant.configure(2) do |config|
  config.vm.box = "generic/ubuntu1804"
  config.vm.provision "shell", privileged: true, inline: $INSTALL_BASE
  config.vm.provision "shell", privileged: true, inline: $INSTALL2
  config.vm.synced_folder ".", "/vagrant"

  config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
  end
end


