
#create a repo folder at Home directory
#mkdir ~/repo 
#Clone the REFRESH repo

#execute this command 
#~/repo/REFRESH/run/1stSetup.sh

#create a data folder at repo directory
mkdir ~/repo/data

#copy chomadb from google drive to aws vm
wget -c -O ~\repo\data\chroma.sqlite3 --progress=bar "https://drive.usercontent.google.com/download?id=1-4S5_8LqUeoHvowqmWsD1em-52bnYaNm&export=download&confirm=t"

#check docker is running 
docker ps

#create docker network 
docker network create --driver bridge IK_Net

#install ollama on IK_Net Network
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --restart always --network IK_Net --name ollama ollama/ollama

#download the model
docker exec -it ollama ollama run llama3.2


