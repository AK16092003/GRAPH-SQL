"""
Created on Sat Aug 20 10:57:00 2022
@author: Admin
"""
from win32api import GetSystemMetrics

scr_width = GetSystemMetrics(0)
scr_height = GetSystemMetrics(1)

from markupsafe import Markup
from flask import *
from flask_session import Session

import mysql.connector as mysql

from math import sin, cos , pi , atan

def rotate(origin, point, angle):
    #Rotate a point counterclockwise by a given angle around a given origin.
    #The angle should be given in radians.
    x = origin[0] + cos(angle) * (point[0] - origin[0]) - sin(angle) * (point[1] - origin[1])
    y = origin[1] + sin(angle) * (point[0] - origin[0]) + cos(angle) * (point[1] - origin[1])
    return (x, y)
    
class Node:
    Name = ''
    Age = ''
    Hobbies = ''
    Gender = ''

    
conn = mysql.connect(host = "localhost", username = "root" , passwd = "Pettaashu2003")
cur = conn.cursor()

def use_database():
    query = "use graphsql;"
    cur.execute(query)
    conn.commit()
    
def create_database_tables():
    
    try:
        query = "create database graphsql;"
        cur.execute(query)
        conn.commit()
        use_database();
        
        query = "create table nodes (name varchar(30) primary key,  age int , hobbies varchar(255) , gender varchar(10));"
        cur.execute(query)
        conn.commit()
        
        query = "create table link_connection (node1 varchar(30) , node2 varchar(30),relation varchar(255));"
        cur.execute(query)
        conn.commit()
        
    except:
        pass

        
create_database_tables()
use_database()

app = Flask(__name__)


app.secret_key = "abc"  

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)



@app.route("/home.html" , methods = ["GET" , "POST"])
def home_page():
    return render_template("home.html")
    

def create_node(node):
    
    name = node.Name
    age = node.Age
    hobbie = node.Hobbies
    gender = node.Gender
    try:
        query = "insert into nodes values('{}' , {} , '{}' , '{}');".format(name , age , hobbie , gender)
        cur.execute(query)
        conn.commit()
        return True
    except:
        return False

def create_relation(name1 , name2 , relation):
    
    try:
        query = "insert into link_connection values('{}' , '{}' , '{}');".format(name1 ,name2 ,relation)
        cur.execute(query)
        conn.commit()
        return True
    except:
        return False

def get_names():

    query = "select name from nodes;"
    cur.execute(query)
    s = ""
    for i in cur.fetchall():
        s += "<option>"+i[0]+"</option>"
    return s

def validate(node):
    
    name = node.Name
    age = node.Age
    hobbie = node.Hobbies
    gender = node.Gender
    
    if name.replace(" ","") == "":
        return "Name not entered !"
    if age.replace(" ","") == "":
        return "Age not entered !"
    if hobbie.replace(" ","") == "":
        return "Hobbie not entered !"
    if gender.replace(" ","") == "":
        return "Gender not entered !"
    age = int(age)
    if not(0<age<150):
        return "Inappropriate age"
    
    return ''

@app.route("/create.html" , methods = ["GET" , "POST"])
def create():
    
    if request.method== "POST":
        #submit
        node =  Node()
        node.Name = request.form.get("name")
        node.Age = request.form.get("age")
        node.Hobbies = request.form.get("hobbies")
        node.Gender = request.form.get("gender")
        
        err = validate(node)
        if(err):
            flash(err)
            return redirect("create.html")
        
        response = create_node(node)
        if response == False:
            flash("Name already exist")
            return redirect("create.html")
        else:
            flash("Record successfully created")
            return redirect("create.html")
            
    return render_template("create.html")

@app.route("/insert.html" , methods = ["GET" , "POST"])
def insert():
    
    
    if request.method== "POST":
        #submit
        name1 = request.form.get("name1")
        name2 = request.form.get("name2")
        
        relation = request.form.get("relation")
        
        if relation.replace(" ","") == "":
            flash("Relation not entered")
            return redirect("insert.html")
        
        if name1 == name2:
            flash("Relation cannot exist between same nodes! ")
            return redirect("insert.html")
        
        response = create_relation(name1 , name2 , relation)
        
        if response == False:
            flash("Relation already exist")
            return redirect("insert.html")
        else:
            flash("Relation successfully created")
            return redirect("insert.html")
        
    code = get_names()
    return render_template("insert.html" , msg = Markup(code))

def draw_node(name , x , y , color):
    r = len(name)*6
    color1 = "lightyellow"
    if color == "blue":
        color1 = "aqua"
        
    s = '<circle cx="{}" cy="{}" r="{}" stroke="{}" stroke-width="4" fill="{}" />'.format(x,y,r,color , color1)
    s += '<text x="{}" y="{}" fill="black">{}</text>'.format(x-len(name)*4,y,name)
    
    return s

def get_gender():
    query = "Select name , gender from nodes;"
    cur.execute(query)
    m = {}
    for (a,b) in cur.fetchall():
        m[a] = b
    return m

def mid_pt(a , b):
    x = 1
    c = (a[0] + b[0]*x)/(x+1)
    d = (a[1] + b[1]*x)/(x+1)
    return [c , d] 

def draw_line(a , b):
    
    s = '<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="#000" stroke-width="8" marker-end="url(#arrowhead)" />'.format(a[0],a[1],b[0],b[1])
    return s
    
def draw_text(pt , ang , txt):
    s = ' <text filter="url(#solid)" transform="translate({}, {}) rotate({})"  fill="red" >{}</text>'.format(pt[0] , pt[1] , ang , txt)
    return s
    
@app.route("/select.html" , methods = ["GET" , "POST"])
def select():
    
    svg_code = ''
    gender_info = get_gender()
    
    if request.method == "POST":
        name = request.form.get("name")
            
        origin = [scr_width/2,scr_height*0.70]
        other_pt = [scr_width*0.75,scr_height*0.70]
        
        
        query = "select * from link_connection where node1 like '{}' or node2 like '{}';".format(name , name)
        cur.execute(query)
        l = cur.fetchall()
        
        other_names = set()
        relation = {}
        for (a,b,c) in l:
            if a == name:
                other_names.add(b)
            if b == name:
                other_names.add(a)
            relation[(a,b)] = c
            relation[(b,a)] = c
            
                
        other_names = list(other_names)
        n = len(other_names)
        ang = 360 / n
        count = 1
        
        coordinates = {name:origin}
        
        for nodes in other_names:
            x,y = rotate(origin , other_pt , ang*count*pi/180 )
            coordinates[nodes] = (x , y)
            count += 1
            
        
        for (a,b,c) in l:
            origin = coordinates[a]
            point = coordinates[b]
            x,y = point
            relation = c
            extra = 6*len(b) + 40
            if(origin[0] >= point[0]):
                svg_code += draw_line(origin ,get_point(origin , distance(origin , point)-extra, abs(180+angle(origin , point))))
            else:
                svg_code += draw_line(origin ,get_point(origin , distance(origin , point)-extra , angle(origin , point)))
            
            svg_code += draw_text(mid_pt(origin , point ) , angle(origin , point) , relation)
        
            
        color = "pink"
        if gender_info[name] == "M":
            color = "blue"
        svg_code += draw_node(name ,coordinates[name][0] , coordinates[name][1] ,color)
        
            
        for nodes in other_names:
            color = "pink"
            if gender_info[nodes] == "M":
                color = "blue"
            svg_code += draw_node(nodes ,coordinates[nodes][0] , coordinates[nodes][1] ,color)
        
        
    code = get_names()
    return render_template("select.html" , msg = Markup(code) , svg_code = Markup(svg_code))

def angle(a,b):
    m = slope(a,b)
    ang = atan(m)
    return ang*(180/pi)

def slope(a,b):
    return (a[1] - b[1]) / (a[0] - b[0])

def get_point( o , d , angle):
    o = list(o)
    angle *= (pi/180)
    o[0] += d*cos(angle)
    o[1] += d*sin(angle)
    return o

def distance(a , b):
    
    xd = a[0] - b[0]
    yd = a[1] - b[1]
    return (xd**2 + yd**2)**0.5

    
@app.route("/view.html" , methods = ["GET" , "POST"])
def view():
    
    
    svg_code = ''
    gender_info = get_gender()
    
    origin = [scr_width/2,scr_height*0.70]
    other_pt = [scr_width*0.75,scr_height*0.70]
    query = "select * from link_connection;"
    cur.execute(query)
    l = cur.fetchall()
    
    query = "select name from nodes;"
    
    cur.execute(query)
    all_names = [i[0] for i in cur.fetchall()]
        
    relation = {}
    coordinates = {}
    
    for (a,b,c) in l:
        relation[(a,b)] = c
        relation[(b,a)] = c
            
    n = len(all_names)
    ang = 360 / n
    count = 1
    
    for nodes in all_names:
        x,y = rotate(origin , other_pt , ang*count*pi/180 )
        coordinates[nodes] = (x , y)
        count += 1
        
    for (a,b,c) in l:
        origin = coordinates[a]
        point = coordinates[b]
        x,y = point
        relation = c
        extra = 6*len(b) + 40
        if(origin[0] >= point[0]):
            svg_code += draw_line(origin ,get_point(origin , distance(origin , point)-extra, abs(180+angle(origin , point))))
        else:
            svg_code += draw_line(origin ,get_point(origin , distance(origin , point)-extra , angle(origin , point)))
        
        svg_code += draw_text(mid_pt(origin , point ) , angle(origin , point) , relation)
        
        
    for nodes in all_names:
        color = "pink"
        if gender_info[nodes] == "M":
            color = "blue"
        svg_code += draw_node(nodes ,coordinates[nodes][0] , coordinates[nodes][1] ,color)
    
    return render_template("view.html" ,  svg_code = Markup(svg_code))

app.run()