## Historical Stock Prices using YFinance

The purpose of this code is to illustrate how to return data
in Protobuf format, and to compare the size of large messages
using JSON and Protobuf format for some realistic data.

The application returns historical stock price data from YFinance.

After you install dependencies and run the application server,
it will expose a single endpoint:
```
GET /stock/{symbol}?limit=ndays
```
where `?limit=ndays` is an optional query parameter (default is 100 days).

Use the HTTP `Accepts:` header to choose `application/json` or `applicatoin/protobuf` format:
```
GET /stock/MSFT
Accepts: application/protobuf
```

It also provides interactive OpenAPI docs at <http://localhost:8000/docs>

### Compare JSON and Protobuf - Download Price History

To compare the size of Protobuf and JSON, download the same price data in both
formats and save to a file.  You can do this using the `curl` command line utility:

```shell
curl -H "application/json" -o msft.json '/stock/MSFT?limit=200'
curl -H "application/protobuf" -o msft.pb '/stock/MSFT?limit=200'
```

How much smaller is the protobuf file?

`curl` is a handy command-line tool for interacting with web services.

### Configure the Application

Create and activate a virtual env. In the virtual env, enter:

```
pip install -r requirements.txt
```

### Run the stock price service (in virtual env)

```
python -m app.main
```

## How to Compile the Protobuf Definition File

(You don't need to do this. The resulting `protos/stock_pb2.py` is included.)

The file [app/proto/stock.proto](./app/proto/stock.proto)
contains the Protocol Buffers definition for a single day's stock data.
During development, you have to compile this to generate a Python class used 
to serialize and deserialize Protobuf format data.

One way is using the `grpcio-tools` package:
```
pip install protobuf grpcio-tools
python -m grpc_tools.protoc -Iapp/protos --python_out=app/protos app/protos/stock.proto
```

The output is a file named `app/protos/stock_pb2.py`.

According to the [protobuf documentation](https://protobuf.dev/getting-started/pythontutorial/),
another way to compile the Protobuf definition file is:

```
pip install protobuf 
pip install protobuf-protoc-bin  # for 'protoc' binary
protoc --proto_path=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/stock.proto
```

with `SRC_DIR=app/protos` and `DST_DIR=app/protos`.

On my machine, both commands produced identical output `protos/stock_pb2.py`.
For the final code, I used the `protoc` command to generate Python code.

## Resources

- [YFinance Github Repo](https://github.com/ranaroussi/yfinance)
- [Protobuf Documentation](https://protobuf.dev/) and [Python Tutorial](https://protobuf.dev/getting-started/pythontutorial/)
