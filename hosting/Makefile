
# provides HTTP_PORT, HTTPS_PORT, and DOMAIN
$(shell cp -f ../image/.env objects/.env)
$(shell sed -e "s/=/:=/g" -i objects/.env)

include objects/.env

SOCKET = /run/uwsgi/$(FORM_NAME)/socket.sock

ifeq ($(DOMAIN_ONLY),1)
	ifeq ($(REQUIRE_EMBED),1)
VALID_REFERERS = *.$(domain_)
	else
VALID_REFERERS = none *.$(domain_)
	endif
else
# not modifying the referers
endif


export DOMAIN
export VALID_REFERERS

# empty rule to require specifying what to do
all:

.phony: install

clean:
	rm -rf objects

objects/:
	mkdir --parent objects

objects/install: host_nginx_config ../image/.env objects/
	rm -f objects/_temp_test_config
	$(foreach domain_,$(DOMAIN),sed \
	-e "s/'{DOMAIN_NAME}'/$(domain_)/g" \
	-e "s;'{SOCKET}';$(SOCKET);g" \
	-e "s;'{VALID_REFERERS}';$(VALID_REFERERS);g" \
	$< >> objects/_temp_test_config;)
	
	cp -f objects/_temp_test_config /etc/nginx/sites-enabled/contact-form-$(FORM_NAME)
	
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
