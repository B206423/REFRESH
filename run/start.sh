#stop container if present and remove it 
docker stop refresh
docker rm refresh

#clean any ols image
docker image prune -f

#build application 
docker build -t refresh .

# Make sure chorma db (chroma.sqlite3) is in folder ~/repo/data (Example below)
#ubuntu@ip-172-31-64-248:~/repo/data$ ls -la
#total 4170608
#drwxrwxr-x 3 ubuntu ubuntu       4096 Jan  5 23:35 .
#drwxrwxr-x 4 ubuntu ubuntu       4096 Jan  5 23:22 ..
#-rw-rw-r-- 1 ubuntu ubuntu 4270686208 Dec 13 20:30 chroma.sqlite3

#start the application
docker run --name=refresh -d --hostname=refresh -p 8000:8000 -e PORT=8000 -v "/home/ubuntu/repo/data:/app/db/chroma_db_jobs" --network IK_Net --restart always -it refresh

