if [ -d "/swapfile" ]; then
	exit 0
fi

echo 'adding swap file'
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap defaults 0 0' >> /etc/fstab