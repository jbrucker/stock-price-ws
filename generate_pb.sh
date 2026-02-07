# Generate stock_pb2.py class from 'stock.proto' definition.
SRC_DIR=app/protos

# Output directory for generated code
DST_DIR=app/protos

if [ ! -d $SRC_DIR ]; then
	echo "Source directory $SRC_DIR does not exist"
	exit 1
elif [ ! -d $DST_DIR ]; then
	echo "Output directory $DST_DIR does not exist"
	exit 1
fi
 
# There are two ways to do this, depending on installed packages.

# 1. Using protobuf alone
#    pip install protobuf protobuf-protoc-bin

# then run:
protoc --proto_path=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/stock.proto

# or
# 2. Using protobuf and grpcio-tools packages
#    pip install protobuf grpcio-tools
# then run:
#python -m grpc_tools.protoc -I$SRC_DIR --python_out=$DST_DIR $SRC_DIR/stock.proto
