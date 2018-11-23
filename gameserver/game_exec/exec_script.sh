image=$1
compiler=$2
path=$3
file=$4
link=$5
log_id=$6

echo ii"$file"

if [ "$link" -eq "0" ]; then
	
	cont=$(docker run --name "$log_id$file" -ti -d 41f2086aefd8 bash)
    echo "$compiler"
    docker cp $path$file "$cont":/$file
    docker exec -i "$cont" sh -c "$compiler $file"
else
	cont=$(docker run --name "$file" --link "$link" -ti -d "$image" bash)
    echo "$path$file"the"$cont"
    docker cp $path$file "$cont":/$file
    docker exec -i "$cont" sh -c "$compiler $file"
fi

