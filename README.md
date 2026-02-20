## Historical Stock Prices using YFinance

The purpose of this code is to illustrate how a web service can return data
in Protobuf format, and to compare the size of large messages
using JSON and Protobuf format for some realistic data.

The application returns historical stock price data for a single stock from YFinance.

After you install dependencies and run the application server,
it will expose a single endpoint:

```
GET /stock/{symbol}?limit=ndays
```
where `?limit=ndays` is an optional query parameter (default is 100 days).

The endpoint returns either JSON or Protobuf format stock quote data.

Use the HTTP `Accepts:` header to specify either `application/json` or `application/protobuf`:
```
GET /stock/MSFT
Accepts: application/protobuf
```

The service also has interacive OpenAPI docs at <http://localhost:8000/docs>

## Run Application and Get Stock Price Data

1.  Create and activate a virtual env. In the virtual env, enter:

    ```shell
    pip install -r requirements.txt
    ```

2.  Then run the REST server, listening on port 8000:

    ```shell
    python -m app.main
    ```

3.  In a separate terminal window, get some historical price data. This example uses Microsoft (MSFT) and 200 days of data. It uses `curl`, but you could also use `wget`.

    ```shell
    curl -H "Accepts: application/json" -o msft.json 'http://localhost:8000/stock/MSFT?limit=200'
    curl -H "Accepts: application/protobuf" -o msft.pb 'http://localhost:8000/stock/MSFT?limit=200'
    ```

    The data is saved to files `msft.json` and `msft.pb`.

4.  How much smaller is the protobuf file? Please let me know.

> `curl` is a useful command-line tool for interacting with web services.


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

```shell
pip install protobuf 
pip install protobuf-protoc-bin  # for 'protoc' binary
protoc --proto_path=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/stock.proto
```

with `SRC_DIR=app/protos` and `DST_DIR=app/protos`.

On my machine, both commands produced identical output `protos/stock_pb2.py`.
For the final code, I used the `protoc` command to generate Python code.

## Historical Stock Prices

For each day that the stock market is open for trading, there is one
line of stock price data. It contains the fields:

Field  | Description
-------|---------------------
Date   | Date string in format "yyyy-mm-dd"
Open   | Opening price on that day
Close  | Closing price on that day
High   | Highest price for the day
Low    | Lowest price for the day
Volume | Number of shares traded during trading hours
Dividend | Optional. Dividend earned on that day (X-Div date)
Split  | Optional. Share split effective on that day

## Resources

- [YFinance Github Repo](https://github.com/ranaroussi/yfinance)
- [Protobuf Documentation](https://protobuf.dev/) and Protobuf [Python Tutorial](https://protobuf.dev/getting-started/pythontutorial/)
