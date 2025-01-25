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


  
