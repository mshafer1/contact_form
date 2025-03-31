# Conact_Form

A simple flask based contact form built on:
- [Flask](https://pypi.org/project/Flask/) (for the routing and form handling)
- [Flask-WTF](https://pypi.org/project/Flask-WTF/) (handing [csrf](https://owasp.org/www-community/attacks/csrf) setup/validation)
- [nginx](https://nginx.org/) as a reverse proxy / web-server
- [python-decouple](https://pypi.org/project/python-decouple/) to handle deployment time variables
- [sendgrid](https://pypi.org/project/sendgrid/) Python api (handles the actual sending)
- [uWSGI](https://pypi.org/project/uWSGI/) (production server to tie NGINX and Flask together)

This was largely based on [this article on using Flask and Flask-WTF to write secure forms](https://mailtrap.io/blog/flask-contact-form/) and is similar to the result of following this [Geeks for Geeks article on creating a form](https://www.geeksforgeeks.org/create-contact-us-using-wtforms-in-flask/), although this article stops short of actually sending the emails.


## Why?

I needed a web-contact form that:
* Works embeded on static sites (or on sites that I can't control the server)
* Requires basic "are you human" authentication (more on this later)
* Was deployed in a way that (despite being embeded in a static site) does not expose API keys or similar
* Can handle ~100 emails / day without cost
* Allows me to set the "reply-to" field on the emails to the submitted address on the form (to simplify responding)

In the end, I landed on hosting my own form on a [Digital Ocean droplet / VPS](https://m.do.co/c/e62a2722d8d4) (referal link) ($6/mo, this is is also not the only use) that is served behind a [CloudFlare 0 Trust Tunnel](https://www.cloudflare.com/plans/zero-trust-services/) (free plan) that provides the human/threat management.
For the actual email sending, I am using SendGrid (now, Twilio SendGrid) API which [permits 100 emails per day](https://sendgrid.com/content/dam/sendgrid/legacy/documents/Twilio-SendGrid-Email-API-Plan-Comparison.pdf?ver=1696571602881)

### Doesn't Google Forms have a script API you could use to email on submission?
Yes it does; however, (at the time of writing) the number of emails per day sent in this manner is limited to 100 [source: Email recipients per day](https://developers.google.com/apps-script/guides/services/quotas#note1).

Problems with this route for what I was working on:
- Limited ability to plug in ReCaptcha, or CludFlare 0 Trust "human verification"
- Limited ability to control the email such that it is "from" a trusted sender, but sets the "reply-to" the form submitter.


### What about Twilio serverless?

[reference](https://www.twilio.com/code-exchange/email-contact-form-with-sendgrid)

At the time of writing, the Twilio serverless Functions is free for 10k calls per month and then charges 1¢ ($0.01) per 100 calls.

Problems with this route:
- If I need to store the API key and then provide it to Twilio, I have to run my own server anyways

### What about Cognito Forms?

[reference](https://www.cognitoforms.com/pricing)

At the time of writing, free plan limits to 500 entries / month. For a form that I want to work for up to 100 / day, I need a plan that allows 3k / Month. 
Their first plan that offers that costs $20/mo. By comparison, it is cheaper to [rent a VPS](https://techit.mandmshafer.com/Blog/website_hosting_platforms_review.html#high-level-comparison).

Problems with this route:
- Cost for the scale I want is prohibitive

### What about FormSpree?

[reference](https://community.cloudflare.com/t/emailing-through-a-contact-form-on-a-static-site-is-possible-right/680464/4)

At the time of writing, the free plan limits to 50 submissions / month. For a form that I want to work for up to 100 / day, I need a plan that allows 3k / Month. 
Their first plan that offers that costs $60/mo. That's $720 /yr. 


  
## Setup

Prerequisites:
- A domain name (pointing at your server through some method, I'm using CloudFlare Tunnel [reference](https://youtu.be/ey4u7OUAF3c?si=e1oBcK_ufDrghS7A&t=320))
- An [nginx server](https://github.com/mshafer1/ansible-configs?tab=readme-ov-file#bootstrapping-an-nginx-server) (running, setup will configure the site with nginx)

Steps:
1. `git clone https://github.com/mshafer1/contact_form`

1. `cd contact_form`

1. Edit `./image/.env` with values for the following variables:
    ```bash
    #./image.env
    VALID_REFERERS=
    DOMAIN=
    SECRET_KEY=
    FORM_NAME=

    SENDGRID_API_KEY=
    SENDGRID_SENDER_ADDRESS=
    SENDGRID_CONTACT_ADDRESS=
    ```

    - `VALID_REFERERS=` this should be a space separated list of domains that you want to allow to embed this form (see [nginx docs](https://nginx.org/en/docs/http/ngx_http_referer_module.html#valid_referers) -> setup will populate this value with the `valid_referers server_names` prefix). If you do not want any, put "none" (without the quotes)

    - `DOMAIN=` the domain it should be served (will be used to tell nginx to handle the site). If using multiple domain names, just least each separated by a space (wrap the whole list in single quotes - `'`)

    - `FORM_NAME=` name used for the nginx and uwsgi socket files (just an identifier, "contact_form" would be fine if this is the only instance running)

    - `SECRET_KEY=` make up something long and random (a GUID should work). Used by flask as basis for secrets

    - `SENDGRID_API_KEY=` your API from https://app.sendgrid.com/settings/api_keys

    - `SENCGRID_SENDER_ADDRESS=` the email address you have authorized on Sendgrid as a sender, and you would like to have be the origin of the emails from the form.

    - `SENDGRID_CONTACT_ADDRESS=` the email address to send messages to.

    **NOTE:** To handle multiple domains with different recipients based on the form domain
        
      1. Remove `SENDGRID_SENDER_ADDRESS` and `SENDGRID_CONTACT_ADDRESS` from the `.env` file.
      1. Create a `.config.yaml` (location defaults to the `contact_form` folder, and can be configured by `CONFIG_DIR` in the `.env` file)
      1. Format `.config.yaml` as a list containing dictionaries. Each dictionary needs to provide:
       
            * `pattern`, the `fnmatch` glob used to determine if the submitted form's domain is for this set (use '*' for all)
            * `sender_address`, the sender for this domain
            * `recipient_address`, the recipient of the contact form for this domain

      1. Place groups in order of precedence (first match is taken)
    
      ```yaml
      # example .config.yaml
      - pattern: '*.example.com'
        sender_address: 'no-reply@example.com'
        recipient_address: admin@example.com
      - pattern: domain2.com
        sender_address: 'no-reply@domain2.com'
        recipient_address: admin@domain2.com
      ```

    - (Optional) Use `DOMAIN_ONLY=1` to require the current domain for embed / referrer (as opposed to all domains)

    - (Optional) Use `REQUIRE_EMBED=1` to disallow "none" as a valid referrer (only takes affect if `DOMAIN_ONLY=1` is used)

1. Bring up the service container
    
    `pushd ./image && docker compose build && docker compose up -d && popd`

1. Configure nginx site (run as root, or replace "make" with "sudo make")
    
    `pushd ./hosting && make install && popd`

1. (Optional) if hosting directly (exposed ports on server), use certbot to setup SSL cert to serve app over https -> (Alternative setup, see [Network Chuck's Video on using CloudFlare Tunnel](https://www.youtube.com/watch?v=ey4u7OUAF3c&t=188s&pp=ygUlbmV0d29ya2NodWNrIGV4cG9zZSB5b3VyIGhvbWUgbmV0d29yaw%3D%3D))

    (run as root, or replace "make" with "sudo make")

    `pushd ./hosting && make install_ssl && popd`


## Testing a deployment.

If a site is setup to require a given referer, one can use cURL to fetch the page and validate.

NOTE: this following command assumes the domain name is not pointing at the server yet, so it accomplishes http by talking to localhost and specifying the host header.

```bash
curl -H 'Host: {domain name}' --referer '{refering url}' http://127.0.0.1/
```

(replacing "{domain name}" and "{refering domain}" with the appropriate values)


## Firewall rules

If using external domain:
```
ufw allow http
ufw allow https
```

If using a docker based tunnel:
```
ufw allow from 172.0.0.0/8 proto tcp to any port 80
ufw allow in on DOCKER0 proto tcp to any port 80
```

(assuming TLS is handled outside the tunnel)
