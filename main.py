import dotenv
import os
from flask import Flask, redirect, url_for, session,request
from authlib.integrations.flask_client import OAuth
from web3 import Web3 

dotenv.load_dotenv()
kyc_info_path = os.getcwd() + "/kyc_info/"
# create kycpath if not exist
if not os.path.exists(kyc_info_path):
    os.mkdir(kyc_info_path)

github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")

github_authorize_url = 'https://github.com/login/oauth/authorize'
github_access_token_url = 'https://github.com/login/oauth/access_token'
github_scope = {'scope': 'read:user'}
github_client_kwargs={'token_endpoint_auth_method': 'client_secret_basic'}
github_api_base_url='https://api.github.com/user'
website_base_url = os.getenv("WEBSITE_BASE_URL")

app = Flask(__name__)
app.secret_key = "thisissecret"
github_oauth = OAuth()
github_oauth.init_app(app)

github_oauth.register(
    name='github',
    client_id=github_client_id,
    client_secret=github_client_secret,
    authorize_url=github_authorize_url,
    authorize_params=github_scope,
    access_token_url=github_access_token_url,
    # request_token_url='https://github.com/login/oauth/access_token', # no request_token_url in ouath 2.0
    client_kwargs=github_client_kwargs,
    api_base_url=github_api_base_url,
)

@app.route('/<path:path>')
def catch_all(path):
    return {'status': 'error', 'message': 'Not found'}

@app.route('/auth/github')
def auth_github():
    redirect_uri = url_for('github_callback', _external=True, _scheme='http')
    redirect_uri = website_base_url + "callback/github"
    rv = github_oauth.github.create_authorization_url(redirect_uri)
    print(request.args)
    github_oauth.github.save_authorize_data(redirect_uri=redirect_uri, **rv)
    print("redirect uri: ",redirect_uri)
    return github_oauth.github.authorize_redirect(redirect_uri)

@app.route('/callback/github')
def github_callback():
    github_oauth.github.authorize_access_token()
    user = github_oauth.github.get('user').json()
    session['github'] = user
    
    session['github']['username'] = user['login']
    return redirect('/kyc', code=302)

@app.route('/logout')
def logout():
    session.pop('github', None)
    return redirect('/')

@app.route('/kyc/submitAddress',methods=['POST'])
def submitAddress():
    if 'github' not in session:
        return "error"
    data = request.get_json()
    print(data)
    crypto_address = data['crypto_address']
    platform_name = request.args.get('platform_name')
    platform_name = "github"
    username = session['github']['username']
    print("username: ",username)
    print("crypto_address: ",crypto_address)
    print("platform_name: ",platform_name)
    
    session['crypto_address'] = crypto_address
    store_kyc_info(username,crypto_address,platform_name)
    return redirect('/kyc', code=302, Response="success")

@app.route('/kyc/getAddress')
def getAddress():
    username = getUsername()
    path = kyc_info_path + "github" + "/" + username
    if os.path.exists(path):
        crypto_address = open(path).read()
        print(crypto_address)
        return crypto_address
    else:
        print("ERRR")
        return "error"
    
@app.route('/kyc/getUsername')
def getUsername():
    if 'github' not in session:
        return "error"
    username = session['github']['username']
    return username

@app.route('/api/<platform>/<username>')
def api(platform, username):
    platform = platform.lower()
    path = kyc_info_path + platform + "/" + username
    if os.path.exists(path):
        crypto_address = open(path).read()
        account_sig = Web3.solidity_keccak(['string','bytes32'],[username,crypto_address]).hex()
        j = {"username":username,"crypto_address":crypto_address,"account_sig":account_sig}
        return j
    return {'status': 'error', 'message': 'Not found','account_sig':''}

def store_kyc_info(username,crypto_address,platform_name):
    path = kyc_info_path + platform_name
    if not os.path.exists(path):
        os.mkdir(path)
    
    with open (path+"/"+username,"w") as f:
        f.write(crypto_address)
    
if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)