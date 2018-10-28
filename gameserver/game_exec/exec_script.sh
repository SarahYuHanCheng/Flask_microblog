image=$1
compiler=$2
path=$3
file=$4 #logId_userId.

cont=$(docker run -it -d "$image" bash)
docker cp $path$file[0] "$cont":/$file[0]
docker exec -ti "$cont" sh -c "python 1_2.py"
# docker exec -ti "$cont" sh -c "$compiler $file"