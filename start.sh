sudo docker build -t refresh .
sudo docker run --name=refresh --hostname=refresh -p 8000:8000 -e PORT=8000 -v "chromadb:/app/db/chroma_db_jobs" --rm -it refresh

