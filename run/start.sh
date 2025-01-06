#clean any ols image
docker image prune -f

#build application 
docker build -t refresh .

#start the application
docker run --name=refresh --hostname=refresh -p 8000:8000 -e PORT=8000 -v "/home/ubuntu/repo/data:/app/db/chroma_db_jobs" --network IK_Net --rm -it refresh

