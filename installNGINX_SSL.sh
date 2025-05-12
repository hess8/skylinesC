#to renew SSL certificate:
sudo unlink /etc/nginx/sites-enabled/skylinescondor.com
sudo ln -s /etc/nginx/sites-available/acme-challenge /etc/nginx/sites-enabled
ngrestart
sudo certbot renew --dry-run # remove --dry run part after testing
sudo unlink /etc/nginx/sites-enabled/acme-challenge
sudo ln -s /etc/nginx/sites-available/skylinescondor.com /etc/nginx/sites-enabled
ngrestart

# Automatic renewals.  See https://onepagezen.com/letsencrypt-auto-renew-certbot-apache/#step1
0 0 */28 * * bash /home/bret/skylinesC/production/utilities/renewSSL.sh # every 28 days crontab line.  sudo crontab -e

renewSSL.sh #don't need sudo because crontab runs as root.  Try after sudo -i to get to root
	unlink /etc/nginx/sites-enabled/skylinescondor.com
	ln -s /etc/nginx/sites-available/acme-challenge /etc/nginx/sites-enabled
	systemctl restart nginx
	certbot renew # remove --dry run part after testing
	unlink /etc/nginx/sites-enabled/acme-challenge
	ln -s /etc/nginx/sites-available/skylinescondor.com /etc/nginx/sites-enabled
	systemctl restart nginx

#install on an Ubuntu 18+ machine
sudo apt-get update
sudo apt-get install nginx

sudo apt-get install software-properties-common -y
sudo add-apt-repository ppa:certbot/certbot -y
sudo apt-get update
sudo apt-get install certbot -y

cd /etc/nginx/
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.orig


sudo cp /etc/nginx/sites-available/default sites-available/acme-challenge
sudo ln -s /etc/nginx/sites-available/acme-challenge /etc/nginx/sites-enabled/
#sudo rm /etc/nginx/sites-enabled/default

sudo vim /etc/nginx/sites-available/acme-challenge
#replace;
   server_name _;
#with
	server_name skylinescondor.com;
	location ^~ /.well-known/acme-challenge/ {
		allow all;
  		default_type "text/plain";
	}
sudo service nginx reload

hostnamectl set-hostname soardata.org # Certificate is tied to hostname, so to make it portable

#!!!!!!!!!!!!! Make sure you forward port 80 to this machine before the below!!!!!!!!!
# ...to other machines, they must all have this hostname.
sudo certbot certonly --dry-run --webroot --webroot-path=/var/www/html -d soardata.org
##### if that works, remove --dry-run and run again
#success!

sudo ls -l /etc/letsencrypt/live/skylinescondor.com
#sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
sudo openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048

#Make the real server:
sudo unlink /etc/nginx/sites-enabled/acme-challenge
#sudo cp /etc/nginx/sites-available/default sites-available/skylinescondor.com  #only if it doesn't exist
sudo ln -s /etc/nginx/sites-available/skylinescondor.com /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/soardata.org /etc/nginx/sites-enabled/
sudo vim /etc/nginx/sites-available/skylinescondor.com
#replace server with:
upstream ember {
    server 192.168.1.167:4200;
  }

server {
	    client_max_body_size 4M;

	    listen 443 ssl default_server;
	    listen [::]:443 ssl default_server;

	    server_name skylinescondor.com;
    	    location / {
    	    	root /var/www/nginx-default/;
      		 	if (-f $document_root/maintenance.html) {
                return 503;
            	}
           	proxy_pass http://ember;
		#change to this location for renewing certificate:
		#location ^~ /.well-known/acme-challenge/ {
		allow all;
  		default_type "text/plain";
          proxy_http_version 1.1;

          proxy_set_header Host               $host;
          proxy_set_header X-Real-IP          $remote_addr;
          proxy_set_header X-Forwarded-For    $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto  $scheme;

    	    }
    	error_page 503 @maintenance;
        	location @maintenance {
                rewrite ^(.*)$ /maintenance.html break;}

    ssl_certificate /etc/letsencrypt/live/skylinescondor.com/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/skylinescondor.com/privkey.pem; # managed by Certbot
}


server {
    if ($host = skylinescondor.com) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


	    listen 80;
	    listen [::]:80;
	    server_name skylinescondor.com;
    return 404; # managed by Certbot


}


# make sure Apache isn't using port 80
sudo service nginx reload

if /etc/letsencrypt is missing options-ssl-nginx.conf, get if from https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
and make sure that ssl_ciphers above makes sense with it.
#at this point localhost points to sudo https://skylinescondor.com  and should show the ember server, which is on a Ubuntu 14 machine
#forward port 80 to this nginx machine (ubuntu 18+) and then test at
https://www.ssllabs.com/ssltest/

Success!

See https://www.nginx.com/blog/monitoring-nginx/
Go to https://amplify.nginx.com/dashboard


### Nginx Amplify agent (run on both U14 and U18 machines)
#curl -sS -L -O https://github.com/nginxinc/nginx-amplify-agent/raw/master/packages/install.sh && API_KEY='59c5a93cf3596a889d01a0efa4754897' sh ./install.sh
# Check status with
#ps ax | grep -i 'amplify\-'
