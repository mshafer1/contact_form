
# provides HTTP_PORT, HTTPS_PORT, and DOMAIN
include ../image/.env

SOCKET := /run/uwsgi/$(DOMAIN)/socket.sock

export DOMAIN
export VALID_REFERERS

# empty rule to require specifying what to do
all:

.phony: install

clean:
	rm -rf objects

objects/:
	mkdir --parent objects

../image/nginx/config: ../image/config/nginx_config
	mkdir --parent $(@D)
	envsubst < $< > $@

objects/image_nginx_config: ../image/nginx/config objects/
	touch $@

objects/install: host_nginx_config objects/
	sed \
	-e "s/'{DOMAIN_NAME}'/$(DOMAIN)/g" \
	-e "s;'{SOCKET}';$(SOCKET);g" \
	-e "s;'{VALID_REFERERS}';$(VALID_REFERERS);g" \
	$< > objects/_temp_test_config && \
	cp -f objects/_temp_test_config /etc/nginx/sites-enabled/$(DOMAIN)
	nginx -t
	systemctl restart nginx
	touch $@

objects/install_ssl: objects/install
	certbot --nginx -d $(DOMAIN) --redirect
	nginx -t
	systemctl restart nginx
	touch $@

install: objects/install

install_ssl: objects/install_ssl
