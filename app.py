import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, clean_txt, is_number, checkpas_strong, is_integer, is_phone

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///fixphone.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show all devices and apply some filters"""
    devices = db.execute("select * from devices as d,clients as c,breakdowns as b \
                where d.id_client = c.id AND d.problem_init = b.init_break")
    print("this index devices show all what we have",devices)
    return render_template("index.html",devices=devices)


@app.route("/devices_table/<fixed>/<returned>/<like>/<filter>/<phone_like>")
@login_required
def devices_list_index(fixed,returned,like,filter,phone_like):
    txt =""

    
    print("and the statment is ",fixed,returned,like,filter,phone_like)
    #if filtrage is checked
    if filter == "1":
        #if the phone name field is not empty
        if phone_like !="None":
            devices_list = db.execute("select * from devices as d,clients as c,breakdowns as b \
                                where d.id_client = c.id AND d.problem_init = b.init_break and fixed=? and returned=? and (brand || ' '|| name) like ?;",fixed,returned,"%"+phone_like+"%")
            return render_template("devices_table.html",devices=devices_list)
        # if the client name field is not empty
        if like != "None":
            devices_list = db.execute("select * from devices as d,clients as c,breakdowns as b \
                                where d.id_client = c.id AND d.problem_init = b.init_break and fixed=? and returned=? and (first_name || ' '|| last_name) like ?;",fixed,returned,"%"+like+"%")
            print("the list is :",devices_list)
            return render_template("devices_table.html",devices=devices_list)
        # client name field is not empty
        else:
            devices_list = db.execute("select * from devices as d,clients as c,breakdowns as b \
                                where d.id_client = c.id AND d.problem_init = b.init_break and fixed=? and returned=?;",fixed,returned)
            print("the list is :",devices_list)
            return render_template("devices_table.html",devices=devices_list)
    #if the filtrage is not checked
    else:
        if phone_like !="None":
            devices_list = db.execute("select * from devices as d,clients as c,breakdowns as b \
                                where d.id_client = c.id AND d.problem_init = b.init_break and (brand || ' '|| name) like ?;","%"+phone_like+"%")
            return render_template("devices_table.html",devices=devices_list)
        if like != "None":
            devices_list = db.execute("select * from devices as d,clients as c,breakdowns as b \
                                where d.id_client = c.id AND d.problem_init = b.init_break and (first_name || ' '|| last_name) like ?;","%"+like+"%")
            print("the list is :",devices_list)
            return render_template("devices_table.html",devices=devices_list)
        else:
            devices_list = db.execute("select * from devices as d,clients as c,breakdowns as b \
                                where d.id_client = c.id AND d.problem_init = b.init_break ;")
            print("the list is :",devices_list)
            return render_template("devices_table.html",devices=devices_list)

        




@app.route("/drop_off", methods=["GET", "POST"])
@login_required
def drop_off():
    """Drop-off a device"""
    txt = ""
    clients = db.execute("SELECT * FROM clients order by first_name,last_name;")
    print(clients)

    if request.method == "POST":
        #post for repair phone 
        print(request.form.get("desc")) 
        print(request.form.get("problem_select_list")) 
        print(request.form.get("price")) 
        print(request.form.get("id_device")) 
        print( request.form.get("id_client"))
        if request.form.get("desc") is None or request.form.get("problem_select_list") is None or request.form.get("price") is None or request.form.get("id_client")is None or request.form.get("id_device") is None:
            return [{"txt":"something is wrong in reparation device submition"}]
        desc = request.form.get("desc")
        price = request.form.get("price")
        id_client = request.form.get("id_client")
        id_device = request.form.get("id_device")
        init_problem = request.form.get("problem_select_list")
        print("hello this is reparation post")      
        #check if phone exist and is not fixed yet
        row = db.execute("select * from devices where id = ? and fixed=0;",id_device)
        if len(row)!=1:
            return [{"txt":"this device is not exist or it was already fixed"}]
        if clean_txt(desc) !="" and clean_txt(price) !="" and clean_txt(id_client) !="" and clean_txt(id_device) !="" and clean_txt(init_problem)!="":
            db.execute("update devices set problem_init=?,descr=?,fixed=1 where id_client = ? and id = ?;",init_problem,desc,id_client,id_device)
            db.execute("update clients set total_cost = total_cost + ? ,rest = rest + ? where id = ?",price,price,id_client)
            #add the reparation in the history table
            db.execute("insert into history  (id_device,id_client,action) values (?,?,?)",id_device,-1,"Reparation")

            #refreshe the device list
            devices = db.execute("SELECT devices.*,first_name,last_name,phone FROM devices,clients WHERE id_client = ? and clients.id = id_client order by fixed,returned,brand,name;",id_client)
            return render_template("devices_list.html",devices=devices)
        
        # post for adding a new client
        if request.form.get("phone_brand") is None:
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            phone = request.form.get("phone")
            if  not first_name is None and clean_txt(first_name) !="" and not is_number(clean_txt(first_name)):
                first_name = clean_txt(first_name)
                print("fisrt name drop_off() ",first_name) 
            else:
                print("show modal because of this first name = ",first_name)
                return render_template("drop_off.html",title="Information",text="you have to renter the first name",showmodal=True)

            if not last_name is None and clean_txt(last_name) !="" and not is_number(clean_txt(last_name)): 
                last_name = clean_txt(last_name)
                print(last_name)
            else:
                print("show modal because of this last name = ",last_name)
                return render_template("drop_off.html",title="Information",text="you have to renter the last name",showmodal=True)
            
            if not phone is None and clean_txt(phone) !="" and is_phone(clean_txt(phone)): 
                phone = clean_txt(phone)
                print("",phone)
            else:
                print("show modal because of this phone number = ",phone)
                return render_template("drop_off.html",title="Information",text="you have to renter the first name",showmodal=True)
            
            clients = db.execute("SELECT * FROM clients \
                                WHERE first_name = ? \
                                AND last_name =? \
                                AND phone=?;",first_name,last_name,phone)
            
            
            if len(clients)>0 :
                print("exist")
                return render_template("drop_off.html",title="Information",text="this client already exist",showmodal=True)
            else:
                print("not exist")
                db.execute("INSERT INTO clients (first_name,last_name,total_cost,deposit,rest,phone) VALUES (?,?,0,0,0,?);",first_name,last_name,phone)
            #refresh the select list with the new one
            clients = db.execute("SELECT * FROM clients order by first_name,last_name;")
            return render_template("drop_off.html",clients=clients, txt="operation has succeeded")
        
    # if get method
    else:

        print("this is the clients list ", clients)
        return render_template("drop_off.html", clients=clients,txt=txt)


@app.route("/history")
@login_required
def history():
    """Show history of all depos"""
    history = db.execute("select action,at from  history order by at")
    
    
    return render_template("history.html",histo=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    """ when the user post """
    if request.method == "POST":
        """check the username input if i is not empty and must not exist"""
        if request.form.get("username") == "":
            return apology("User Name is missing maybe?")
        else:
            user = request.form.get("username")

            db.execute("begin TRANSACTION;")
            user_db = db.execute(" select * from users where username = ?;", user)
            db.execute("commit;")
            print(user)
            print(user_db)
            if len(user_db) > 0 and user_db[0]['username'] == user:
                return apology("User Name already exist ")
            else:
                """check the username input if i is not empty and must not exist"""
                if request.form.get("password") == "":
                    return apology("Password is missing maybe?")

                if request.form.get("confirmation") == "":
                    return apology("confirmation Password is empty?")

                if request.form.get("password") != request.form.get("confirmation"):
                    return apology("sorry check your password again ")

                if not checkpas_strong(request.form.get("password")):
                    return apology("Password Must Have 0-9 a-b And /?$!* and more than 6 characters")

                hash = generate_password_hash(request.form.get("password"))
                db.execute("begin TRANSACTION;")
                db.execute(' insert into users (username,hash) values(?,?) ;', user, hash)
                db.execute("commit;")
                return redirect("/")
    else:
        return render_template("register.html")


@app.route("/pick_up", methods=["GET", "POST"])
@login_required
def pick_up():
    """pick up a device"""
    txt = ""
    #post request
    if request.method == "POST":
        print(request.form.get("id_client"))
        print(request.form.get("id_device"))
        print(request.form.get("all_paied"))
        if request.form.get("id_client") is None or request.form.get("id_device") is None:
            return [{"txt":"something is wrong"}]
        if clean_txt(request.form.get("id_client")) =="" or clean_txt(request.form.get("id_device")) =="":
            return[{"txt":"id client or device must not be empty"}]
        id_client = clean_txt(request.form.get("id_client"))
        id_device = clean_txt(request.form.get("id_device"))
        if request.form.get("all_paied") is None:
            all_paied = False
        else:
            all_paied = True

        repaired = db.execute("select * from devices where id = ?",id_device)
        print("this device is ",repaired)
        if all_paied == True:
            print(all_paied)
            if repaired[0]["fixed"] == 1:
                #select the price of the device reparation
                price = db.execute("SELECT b.price FROM devices as d,breakdowns as b\
                                   WHERE id = ? and problem_init = init_break;",id_device)
                db.execute("update devices set returned = 1 where id = ?",id_device)
                db.execute("update clients set deposit = deposit + ? ,rest = rest - ? where id=? ",price[0]["price"],price[0]["price"],id_client)
                 # log the rerutned device
                db.execute("insert into history (id_client,id_device,action) values (?,?,?)",-1,id_device,"Return Device To The Client with reparation")

                # refresh devices list
                devices = db.execute("SELECT devices.*,first_name,last_name,phone FROM devices,clients WHERE id_client = ? and clients.id = id_client order by fixed,returned,brand,name;",id_client)
                print (db.execute("select * from devices where id = ? and fixed =1",id_device))
                return render_template("devices_list.html",devices=devices)
            else:
                return [{"txt":"could you ?!!!"}]
        elif repaired[0]["fixed"] ==1:
            return[{"txt":"payement is a must"}]
        else:
            #device returned without reparation
            print("device returned without reparation")
            db.execute("update devices set returned=1 where id = ? ",id_device)
            # log the rerutned device
            db.execute("insert into history (id_client,id_device,action) values (?,?,?)",-1,id_device,"Return Device To The Client without reparation")
            # refresh devices list
            devices = db.execute("SELECT devices.*,first_name,last_name,phone FROM devices,clients WHERE id_client = ? and clients.id = id_client order by fixed,returned,brand,name;",id_client)
            return render_template("devices_list.html",devices=devices)

    #get request 
    else:
        return render_template("pick_up.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    return render_template("settings.html")


@app.route("/delete_client", methods=["GET","POST"])
@login_required
def delete():
    print("delete client  ")
    print("delete client  ")
    print("delete client  ")
    if request.method == "POST":
        clients = db.execute("SELECT * FROM clients order by first_name,last_name;")
        id = request.form.get("id")
        if id is None or not is_integer(id):
            print("the id is none or not integer " ,type(id))
            return [{"txt":"The ID is None Or Not Integer"}]
        else:
            ids = db.execute("SELECT id FROM clients order by id;")
            #print(ids)
            this_id = dict()
            this_id["id"]=int(id)
            #print(this_id)
            print("i will delete it now id = ",id)
            if not this_id in ids:
                print("it's not exist")
                return [{"txt":"The Client Is Not Exist"}]
            
            #delete all devices in our database that belong to this client
            db.execute("DELETE FROM devices WHERE id_client=?;",id) 
             # log the deleted client
            db.execute("insert into history (id_client,id_device,action) values (?,?,?)",id,-1,"Delete Client")
            db.execute("DELETE FROM clients WHERE id=?;",id)
            #refresh the client list
            clients = db.execute("SELECT * FROM clients order by first_name,last_name;")
            return render_template("add_client.html",clients=clients) 
            

#api to show device list client
@app.route("/devices_list")
@login_required
def devices_list():
    id_client = request.args.get("id_client")
    if id_client == None or not is_integer(id_client):
        return render_template("devices_list.html",devices=False)
    else:
        devices = db.execute("SELECT devices.*,first_name,last_name,phone FROM devices,clients WHERE id_client = ? and clients.id = id_client order by fixed,returned,brand,name;", id_client)
        print("here is the devices ",devices)
        return render_template("devices_list.html",devices=devices)


#api to show problems list
@app.route("/problems_list",methods=["GET", "POST"])
@login_required
def problems_list():
    if request.method == "POST":
        return "do somthing here"
    else:
        problems = db.execute("select * from breakdowns order by desc_break ")
        print(problems)
        return render_template("problems_list.html",problems=problems)

#add client with ajax post "dont need to refresh the page"
@app.route("/add_client", methods=["GET", "POST"])
@login_required
def add_client():
    
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    phone = request.form.get("phone")
    if  not first_name is None and clean_txt(first_name) !="" and not is_number(clean_txt(first_name)):
        first_name = clean_txt(first_name)
        print("fisrt name",first_name)
    else:
        print("show modal because of this first name = ",first_name)
        return [{"txt":"Check The First Name "}]

    if not last_name is None and clean_txt(last_name) !="" and not is_number(clean_txt(last_name)): 
        last_name = clean_txt(last_name)
        print(last_name)
    else:
        print("show modal because of this last name = ",last_name)
        return [{"txt":"Check The Last Name"}]

    if not phone is None and clean_txt(phone) !="" and is_phone(clean_txt(phone)): 
        phone = clean_txt(phone)
        print("",phone)
    else:
        print("show modal because of this phone number = ",phone)
        return [{"txt":"Check The Phone Number"}]

    clients = db.execute("SELECT * FROM clients \
                        WHERE first_name = ? \
                        AND last_name =? \
                        AND phone=?;",first_name,last_name,phone)
    
    
    if len(clients)>0 :
        print("exist")
        return [{"txt":"This Client Exist"}]
    else:
        print("not exist")
        db.execute("INSERT INTO clients (first_name,last_name,total_cost,deposit,rest,phone) VALUES (?,?,0,0,0,?);",first_name,last_name,phone)
        client_id = db.execute("select max(id) as id from clients")
        #log the new client in history
        db.execute("insert into history (id_client,id_device,action) values (?,?,?)",client_id[0]["id"],-1,"Add New Client")
    
    #refresh the select list with the new one
    clients = db.execute("SELECT * FROM clients order by first_name,last_name;")
    print("list refreshed")
    return render_template("add_client.html",clients=clients) 



#add device with ajax post "dont need to refresh the page"
@app.route("/add_device", methods=["GET", "POST"])
@login_required
def add_device():
    
    id_client_dev = request.form.get("id_client_dev")
    phone_brand = request.form.get("phone_brand")
    phone_name = request.form.get("phone_name") 
    issue_init = request.form.get("problem_select_list_add_device")
    issue_desc = request.form.get("issue_desc")
    

    if id_client_dev is None or phone_brand is None or phone_name is None or issue_init is None or issue_desc is None:
        return [{"txt":"there is no data"}]
    if clean_txt(id_client_dev) =="" or not is_integer(id_client_dev) or clean_txt(phone_brand) =="" or clean_txt(phone_name) =="" or clean_txt(issue_init) =="":
        return [{"txt":"check what you entered"}]
    id_client_dev = int(clean_txt(id_client_dev))
    phone_brand = clean_txt(phone_brand)
    phone_name = clean_txt(phone_name) 
    issue_init = clean_txt(issue_init)
    issue_desc = clean_txt(issue_desc)
    print(id_client_dev)
    print(phone_brand)
    print(phone_name)
    print(issue_init)
    print(issue_desc)
    #check if the client exist
    ids = db.execute("SELECT id FROM clients order by id;")
    print(ids)
    this_id = dict()
    this_id["id"]=id_client_dev
    print(this_id)
    if not this_id in ids:
        return [{"txt":"this client is not exist"}]
    
    #add the device 
    db.execute("insert into devices (id_client,brand,name,problem_init,descr) VALUES (?,?,?,?,?);",id_client_dev, phone_brand, phone_name, issue_init, issue_desc)
    device_id = db.execute("select max(id) as id from devices")
    #log the new device in history
    db.execute("insert into history (id_device,id_client,action) values (?,?,?)",device_id[0]["id"],-1,"Add New Device")
    #refreshe the devices list
    devices = db.execute("SELECT devices.*,first_name,last_name,phone FROM devices,clients WHERE id_client = ? and clients.id = id_client order by fixed,returned,brand,name;",id_client_dev)
    return render_template("devices_list.html",devices=devices)


@app.route("/del_device", methods=["GET","POST"])
@login_required
def del_device():
    print("delete device  ")
    print("delete device  ")
    print("delete device  ")
    if request.method == "POST":
        
        id_device = request.form.get("id_device")
        id_client = request.form.get("id_client")
        if id_device is None or not is_integer(id_device) or id_client is None or not is_integer(id_client):
            print("the id_device/id is none or not integer ")
            return render_template("del_device.html",devices=False)
        else:
            ids = db.execute("SELECT id FROM devices order by id;")
            #print(ids)
            this_id = dict()
            this_id["id"]=int(id_device)
            #print(this_id)
            print("i will delete it now id_device = ",id_device,"id_client ",id_client)
            if not this_id in ids:
                print("it's not exist")
                return [{"txt":"The Device Is Not Exist"}]
            else:
                db.execute("DELETE FROM devices WHERE id=? and id_client= ?;",id_device,id_client)
                #log the deleted device in history
                db.execute("insert into history (id_device,id_client,action) values (?,?,?)",id_device,-1,"Delete Device")
                #refresh the devices list
                devices = db.execute("SELECT * FROM devices WHERE id_client = ? order by brand,name;", id_client)
                print(devices)
                return render_template("del_device.html",devices=devices)


@app.route("/get_init_problem", methods=["GET", "POST"])
@login_required
def get_init_problem():
    
    if not request.args.get("ss") is None:
        ss = clean_txt(request.args.get("ss"))
        
        list = db.execute("select * from breakdowns where init_break like ? order by init_break","%"+ss+"%")
        print(list)
        return render_template("get_init_problem.html",list=list)
    return("no")
