#!/bin/bash

#Always execute the default actions

#stop container if present and remove it 
docker stop refresh && docker rm refresh || echo "Failed to stop/remove container"

#build application 

# Check if the first argument is provided
if [ -n "$1" ] && [ "$1" -eq 3 ]; then
    echo "Pruning unused Docker images..."
    docker image prune -f
    echo "Rebuilding Docker image without cache..."
    docker build -f $HOME/repo/REFRESH/Dockerfile --no-cache -t refresh .
else 
    echo "Building Docker image..."
    docker build -f $HOME/repo/REFRESH/Dockerfile -t refresh .
fi

# Make sure chorma db (chroma.sqlite3) is in folder ~/repo/data (Example below)
#ubuntu@ip-172-31-64-248:~/repo/data$ ls -la
#total 4170608
#drwxrwxr-x 3 ubuntu ubuntu       4096 Jan  5 23:35 .
#drwxrwxr-x 4 ubuntu ubuntu       4096 Jan  5 23:22 ..
#-rw-rw-r-- 1 ubuntu ubuntu 4270686208 Dec 13 20:30 chroma.sqlite3

#start the application
docker run --name=refresh -d --hostname=refresh -p 8000:8000 -e PORT=8000 -v "$HOME/repo/data:/app/db/chroma_db_jobs" --network IK_Net --restart always -it refresh

# If parameter is passed, check its value
# Handle optional parameters
if [ ! -z "$1" ]; then
    case "$1" in
        1) docker logs -f refresh ;;
        2) docker image prune ;;
        3) docker logs -f refresh ;;
        *) echo "Invalid parameter. Please provide 1, 2, or 3." ;;
    esac
fi
