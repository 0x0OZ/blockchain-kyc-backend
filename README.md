# Blockchain-KYC Backend

The backend server is responsible for oauth, storing users information for KYC, and serving REST-API for the oracles, it stands behind a reverse proxy.

# Requirements 

- Install the following libraries
```sh
pip3 install flask authlib web3 python-dotenv waitress
```

# Setup Configuration
- Copy `.env.example` to `.env` then add your client id and secret to `GITHUB_CLIENT_ID`, and `GITHUB_CLIENT_SECRET` 
- Run `main.py` using python3 `$ python3 main.py` 
- Enjoy!