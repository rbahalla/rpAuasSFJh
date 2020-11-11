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
    return '''<h1>User API for Genesys Interview</h1>
<p>Prototype for Genesys Interview.</p>'''


@app.route('/api/v1/users/all', methods=['GET'])
def get_all():
    conn = sqlite3.connect('users.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_users = cur.execute('SELECT id,name,email FROM users;').fetchall()

    return jsonify({'count':len(all_users), 'results': all_users})


@app.errorhandler(404)
def page_not_found(e):
    return  jsonify({'errors': 'The resource could not be found'}), 404


@app.route('/api/v1/users', methods=['GET'])
def user_filter():
    try:
        conn = sqlite3.connect('users.db')
        conn.row_factory = dict_factory
        cur = conn.cursor()
        msg = ""
        query_parameters = request.args
        id = query_parameters.get('id')
        fullname = query_parameters.get('name')
        email = query_parameters.get('email')
        
        query = "SELECT id,name,email FROM users WHERE "
        filter_values = []
        filter_list = []
       
        if id:        
            filter_list.append("id=?")
            filter_values.append(id)
        if fullname:
            filter_list.append("name=?")
            filter_values.append(fullname)
        if email:
            filter_list.append("email=?")
            filter_values.append(email)        
        if not (id or fullname or email):
            msg =  page_not_found(404)
            return 
        
        query += " AND ".join(filter_list)        

        results = cur.execute(query, filter_values).fetchall()
        msg = jsonify({'count':len(results), 'results': results})
    except:
        conn.rollback()
        msg = jsonify({'errors': 'Error Encountered while retrieving record'}), 400
    
    finally:
        conn.close()
        return msg
    
@app.route('/api/v1/users', methods=['POST'])
def create():
    try:
        conn = sqlite3.connect('users.db')        
        cur = conn.cursor()
        name = request.form.get('name')
        email = request.form.get('email')                
        password = request.form.get('password')               
        query = 'INSERT INTO users (Name, Email, Password) VALUES (?,?,?)'

        if not (name and email and password):
            msg = jsonify({'errors': 'Invalid Request. Check your parameters'}), 400
            return 

        cur.execute(query, (name, email, password))
        conn.commit()
        msg = jsonify({'success': 'Record Created'})
    except:
        conn.rollback()
        msg = jsonify({'errors': 'Error Encountered while creating record'}), 400
    
    finally:
        conn.close()
        return msg
        
@app.route('/api/v1/users', methods=['PUT'])
def update():
    try:
        conn = sqlite3.connect('users.db')   
        query_parameters = request.args
        msg = ""
        update_values = []
        update_list = []
        id = query_parameters.get('id')     
        if not (id):
            msg = page_not_found(404)  
            return  
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")   
        
        query = 'UPDATE users set '        
        if password:            
            update_list.append("Password = ?")            
            update_values.append(password)            
        if name:           
            update_list.append("Name = ?")
            update_values.append(name)
        if email:         
            update_list.append("Email = ?")
            update_values.append(email)
        if id:
            query += ",".join(update_list)+" WHERE Id = ?"            
            update_values.append(id)
        if not (name or email or password):
            msg = jsonify({'errors': 'Invalid Request. Check your parameters'}), 400
            return 

        msg = query             
        cur = conn.cursor()
        cur.execute(query, update_values)
        conn.commit()
        msg = jsonify({'success': 'Record Updated'}), 200
    except:
        conn.rollback()
        msg = jsonify({'errors': 'Error Encountered while updating record'}), 400
    
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
        msg = jsonify({'success': 'Record Deleted'})
    except:
        conn.rollback()
        msg = jsonify({'errors': 'Error Encountered while deleting record'}), 400
    
    finally:
        conn.close()
        return msg
      
@app.route('/api/v1/users/login', methods=['POST'])
def login():
    try:
        conn = sqlite3.connect('users.db')
        email = request.form.get('email') 
        password = request.form.get('password')
        if not (email and password):
            msg = jsonify({'errors': 'Invalid Request. Check your parameters'}), 400
            return 
        msg = ""        
        query = 'SELECT id,name,email FROM users WHERE Email = ? AND Password = ?'
        conn.row_factory = dict_factory
        cur = conn.cursor()

        login_user = cur.execute(query, (email.strip(), password.strip())).fetchone()     
        if login_user:
            msg =  jsonify(login_user)
        else:
            msg = jsonify({"invalid": "Invalid Username or Password"}), 401        
    except:
        conn.rollback()
        msg = "Error Encountered while logging in"
    
    finally:
        conn.close()
        return msg

app.run()