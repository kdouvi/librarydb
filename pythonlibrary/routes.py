from flask import render_template, request, redirect, session
from pythonlibrary import app, db

if __name__ == "__main__":
    app.run()

@app.route("/")
def landing():
    # checking for error messsages
    try:
        err = session['error_msg']
        session['error_msg'] = ''
    except KeyError:
        err = ''
    
    # getting the administrator's info
    cur = db.connection.cursor()
    cur.execute("select first_name, last_name, username from Users where user_type = 'Administrator';")
    adminfo = cur.fetchall()
    cur.close()

    return render_template("landing.html", error_msg = err, adminfo = adminfo)

@app.route("/login", methods = ["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    cur = db.connection.cursor()
    q = 'select password, user_type, school_id from Users where username = "'+username+'" ;' # getting the user's password and type
    cur.execute(q)
    r = cur.fetchall()
    cur.close()
    if not r:
        session['error_msg'] = "No account for this email"
        return redirect('/')
    # incorrect password
    if (password != r[0][0]):
        session['error_msg'] = "Incorrect password"
        return redirect('/')
    # saving user type
    session['user_type'] = r[0][1]
    session['username'] = username
    session['school_id'] = r[0][2]
    # redirecting to appropriate home page
    match r[0][1]:
        case 'Student':
            return redirect('/stu')
        case 'Educator':
            return redirect('/prof')
        case 'Operator':
            return redirect('/op')
        case 'Administrator':
            return redirect('/admin')

@app.route("/stu")
def stu():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type = 'Student' and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')

    cur.execute("select token from Student where username ='" + username +"';" )
    token = cur.fetchall()
    cur.close()

    return render_template("stu_home.html", token = token)

@app.route("/prof")
def prof():
    # authentication
    try:
        username = session['username']
    except KeyError:
        return redirect('/')
    cur = db.connection.cursor()
    auth_q = "select count(1) from Users where user_type = 'Educator' and username = '" + username +"';"
    cur.execute(auth_q)
    a = cur.fetchall()
    if a[0][0] == 0:
        return redirect('/')

    cur.execute("select token from Educator where username ='" + username +"';" )
    token = cur.fetchall()
    cur.close()

    return render_template("prof_home.html", token = token)


@app.route("/op")
def op():
    return render_template("op_home.html")

@app.route("/admin")
def admin():
    return render_template("admin_home.html")

@app.route("/register")
def register():
    return render_template("register.html")