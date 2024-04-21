# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
	config.vm.box = "ubuntu/trusty64" # 14.04
	config.vm.box_url = "https://atlas.hashicorp.com/ubuntu/boxes/trusty64/versions/20170504.0.0/providers/virtualbox.box"
	
	config.vm.hostname = 'dev-sklad51'	
	config.vm.network :forwarded_port, guest: 8000, host: 8000 # django dev server
	
	config.vm.provider 'virtualbox' do |vm|
		vm.memory = 2048
		vm.cpus = 1
	end
	
	config.vm.provision :shell, :path => "conf/vagrant/upgrade-python.sh"
	config.vm.provision :shell, :path => "conf/vagrant/bootstrap.sh"
	#config.vm.provision :shell, :path => "conf/vagrant/add-swapfile.sh"
end
