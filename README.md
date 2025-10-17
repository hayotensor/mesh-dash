# Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# How to run

### Start Blockchain
See blockchain repository and start blockchain node in a separate CLI
```bash
./target/release/solochain-template-node --dev
```

### Start Bootnode & Bootnode API (subnet)
See docs on how to start your bootnode: https://docs.hypertensor.org
```bash
mesh-dht-api \ 
  --host_maddrs /ip4/0.0.0.0/tcp/31330 /ip4/0.0.0.0/udp/31330/quic \
  --announce_maddrs /ip4/127.0.0.1/tcp/31330 /ip4/127.0.0.1/udp/31330/quic \
  --identity_path pk.id
```

### Start App
```bash
uvicorn app.main:app --reload --port 8001
```

