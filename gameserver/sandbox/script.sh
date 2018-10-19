image=$1
compiler=$2
file=$3

cont=$(docker run -it -d "$image" bash)
docker cp $file "$cont":/
docker exec -ti "$cont" sh -c "$compiler $file"