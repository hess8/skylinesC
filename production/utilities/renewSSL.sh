#run on nginx machine
systemctl restart nginx
sudo certbot certonly -d skylinescondor.com
sudo certbot certonly -d soardata.org
