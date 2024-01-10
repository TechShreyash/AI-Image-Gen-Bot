sudo docker rm -f bingai
git pull
sudo docker build -t bingai .
sudo docker run -d --name bingai bingai