ALLOCATE_IP = ../get-next-ip.sh
RETURN_IP = ../return-ip.sh


.PHONY: clean clean-ips

# setup

setup: .vagrant/machines/default/virtualbox/id


.vagrant/machines/default/virtualbox/id: Vagrantfile
	vagrant up

Vagrantfile: ip.1
	bash mkVagrantfile.sh $$(cat ip.1) > Vagrantfile

ip.1:
	echo $$(${ALLOCATE_IP}) > ip.1





# teardown

clean:
	vagrant destroy -f
	$(MAKE) clean-ips
	rm Vagrantfile

clean-ips:
	cat ip.* | ${RETURN_IP}
	rm ip.*