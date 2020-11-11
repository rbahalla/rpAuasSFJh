import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


@app.route('/api/v1/users/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect('users.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_users = cur.execute('SELECT id,name,email FROM users;').fetchall()

    return jsonify(all_users)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/users', methods=['GET'])
def user_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    fullname = query_parameters.get('fullname')
    email = query_parameters.get('email')

    query = "SELECT id,name,email FROM users WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if fullname:
        query += ' Name=? AND'
        to_filter.append(fullname)
    if email:
        query += ' Email=? AND'
        to_filter.append(email)
    if not (id or fullname or email):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('users.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)
    
@app.route('/api/v1/users', methods=['POST'])
def create():
    try:
        name = request.form['name']
        email = request.form['email']                
        password = request.form['password']                
        query = 'INSERT INTO users (Name, Email, Password) VALUES (?,?,?)'
        conn = sqlite3.connect('users.db')        
        cur = conn.cursor()

        cur.execute(query, (name, email, password))
        conn.commit()
        msg = "Record Created"
    except:
        conn.rollback()
        msg = "Error Encountered while creating record"
    
    finally:
        conn.close()
        return msg
        
@app.route('/api/v1/users', methods=['PUT'])
def update():
    try:
        query_parameters = request.args
        id = query_parameters.get('id')
        name = request.form['name']
        email = request.form['email'] 
        password = request.form['password']    
        
        query = 'UPDATE users set Name = ?, Email = ?, Password = ? WHERE Id = ?'
        conn = sqlite3.connect('users.db')        
        cur = conn.cursor()

        cur.execute(query, (name, email, password, id))
        conn.commit()
        msg = "Record Updated"
    except:
        conn.rollback()
        msg = "Error Encountered while updating record"
    
    finally:
        conn.close()
        return msg
        
@app.route('/api/v1/users', methods=['DELETE'])
def delete():
    try:
        query_parameters = request.args
        id = query_parameters.get('id')            
        query = 'DELETE FROM users WHERE Id = ?'
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        cur.execute(query, id)
        conn.commit()
        msg = "Record Deleted"
    except:
        conn.rollback()
        msg = "Error Encountered while deleting record"
    
    finally:
        conn.close()
        return msg
      
@app.route('/api/v1/users/login', methods=['POST'])
def login():
    try:
        email = request.form['email'].strip() 
        password = request.form['password'].strip()
           
        conn = sqlite3.connect('users.db')
        query = 'SELECT id,name,email FROM users WHERE Email = ? AND Password = ?'
        conn.row_factory = dict_factory
        cur = conn.cursor()
       
        login_user = cur.execute(query, (email, password)).fetchone()        

        return jsonify(login_user)
    except:
        conn.rollback()
        msg = "Error Encountered while logging in"
    
    finally:
        conn.close()
        #return msg

app.run()