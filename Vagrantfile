# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/bionic64"
    config.vm.network "forwarded_port", guest: 8000, host: 8000
    config.vm.network "forwarded_port", guest: 8025, host: 8025
    config.vm.provision "shell", inline: $shell
    config.vm.provision "shell", path: "get-mailhog.bash"
end

$shell = <<-'CONTENTS'
  apt update
  apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib
  pip3 install --upgrade pip
  pip3 install -r /vagrant/requirements.txt
CONTENTS

# Don't forget to run the DB Install Script as postgres user: make-db
