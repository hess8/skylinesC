#install on an Ubuntu 18+ machine

sudo apt-get update
sudo apt-get install nginx

sudo apt-get install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot

cd /etc/nginx/
sudo cp nginx.conf nginx.conf.orig

sudo cp sites-available/default sites-available/skylinescondor.com
sudo ln -s /etc/nginx/sites-available/skylinescondor.com /etc/nginx/sites-enabled/
sudo rm sites-enabled/default

sudo vim sites-available/skylinescondor.com
#replace;
   server_name _;
#with 
	server_name skylinescondor.com;
	location ^~ /.well-known/acme-challenge/ {
		allow all;
  		default_type "text/plain";
	}
sudo service nginx reload


#!!!!!!!!!!!!! Make sure you forward port 80 to this machine before the below!!!!!!!!!
sudo certbot certonly --dry-run --webroot --webroot-path=/var/www/html -d skylinescondor.com
##### if that works, remove --dry-run and run again 
#success!
#Test renewal.  Certbot has a cron job running to do the renewal automatically:
#This tests it:

sudo certbot renew --dry-run


sudo ls -l /etc/letsencrypt/live/skylinescondor.com
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

sudo mkdir snippets
sudo vim /etc/nginx/snippets/ssl-skylinescondor.com.conf
#paste:
    ssl_certificate /etc/letsencrypt/live/skylinescondor.com/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/skylinescondor.com/privkey.pem;

sudo vim /etc/nginx/snippets/ssl-params.conf
#paste:	
	# from https://cipherli.st/
	# and https://raymii.org/s/tutorials/Strong_SSL_Security_On_nginx.html

	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	ssl_prefer_server_ciphers on;
	ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
	ssl_ecdh_curve secp384r1;
	ssl_session_cache shared:SSL:10m;
	ssl_session_tickets off;
	ssl_stapling on;
	ssl_stapling_verify on;
	resolver 8.8.8.8 8.8.4.4 valid=300s;
	resolver_timeout 5s;
	# Disable preloading HSTS for now.  You can use the commented out header line that includes
	# the "preload" directive if you understand the implications.
	#add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
	add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
	#add_header X-Frame-Options DENY;#needs to be deactivated because of keycloak
	add_header X-Content-Type-Options nosniff;

	ssl_dhparam /etc/ssl/certs/dhparam.pem;

sudo vim sites-available/skylinescondor.com
#replace server with:
	upstream ember {
	    server 192.168.1.220;
	  }

	server {
		    listen 80;
		    listen [::]:80;

		    listen 443 ssl default_server;
		    listen [::]:443 ssl default_server;

		    include snippets/ssl-skylinescondor.com.conf;
		    include snippets/ssl-params.conf;
		    server_name skylinescondor.com;
	    	    location / {
	      		proxy_pass http://ember;

	          proxy_http_version 1.1;

	          proxy_set_header Host               $host;
	          proxy_set_header X-Real-IP          $remote_addr;
	          proxy_set_header X-Forwarded-For    $proxy_add_x_forwarded_for;
	          proxy_set_header X-Forwarded-Proto  $scheme;

	    	    }
		}

sudo service nginx reload

#at this point localhost points to sudo https://skylinescondor.com  and should show the ember server, which is on a Ubuntu 14 machine 
#forward port 80 to this nginx machine (ubuntu 18+) and then test at 
https://www.ssllabs.com/ssltest/ 

Success!

See https://www.nginx.com/blog/monitoring-nginx/ 
Go to https://amplify.nginx.com/dashboard 