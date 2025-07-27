from flask import Flask, request, jsonify, make_response,render_template,session
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kWcEgnVkFXU7xJkl'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        return f(*args, **kwargs)
    return decorated







@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'logged in currently'
@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] and request.form['password'] =='123456':
        session['logged_in'] = True
        token = jwt.encode({
            'user': request.form['username'],
            'exp': datetime.utcnow() + timedelta(seconds=120)
        },
        app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')}), 200
    else:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})  


if __name__ == '__main__':
    app.run(debug=True)