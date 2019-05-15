from flask import Flask, render_template, request,jsonify,redirect,session
from flask_uploads import UploadSet, configure_uploads, ALL
import warnings
from save_result import get_result
from flaskext.mysql import MySQL
from glob import glob
import os
import json
warnings.filterwarnings('ignore')
app = Flask(__name__)
files = UploadSet('files', ALL)
app.config['UPLOADS_DEFAULT_DEST'] = 'uploads'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='cancersys'
mysql=MySQL()
mysql.init_app(app)
configure_uploads(app, files)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'media' in request.files:
        mhdfile=request.files['media']
        files.save(mhdfile)
        info=dict()
        info['msg']='success'
        filename=mhdfile.filename
        if filename.endswith('.mhd'):
            return jsonify(info)
        else:
            raw_path='./uploads/files/'+filename
            username=request.cookies.get('uname')
            print(username)
            connect = mysql.connect()
            cursor = connect.cursor()
            sql = "Insert into image_save(username,img_path) values(%s,%s)"
            try:
                cursor.execute(sql, (username, raw_path))
                connect.commit()
            except:
                connect.rollback()
            connect.close()
            return jsonify(info)
    return render_template('upload.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        connect=mysql.connect()
        cursor=connect.cursor()
        sql="Insert into info(username,password) values(%s,%s)"
        try:
            cursor.execute(sql,(username,password))
            connect.commit()
        except:
            connect.rollback()
        connect.close()
        return render_template('index.html')
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        print('username:',username)
        connect=mysql.connect()
        cursor=connect.cursor()
        sql="Select * from info where username='"+username+"'"
        print(sql)
        cursor.execute(sql)
        data=cursor.fetchone()
        connect.close()
        info={}
        if data is None:
            flag=1
            return render_template('Middle.html',flag=flag)
        else:
            psw=data[1]
            if psw==password:
                info['status']=200
                info['message']='successfully logged！'
                response=redirect('index')
                response.set_cookie('uname',username)
            else:
                flag=2
                return render_template('Middle.html',flag=flag)
            return response
    return render_template('login.html')

@app.route('/showresult',methods=['GET','POST'])
def showresult():
    # ctime_dict={}
    # path='./uploads/files'
    # names=os.listdir(path)
    # names=[name for name in names if name.endswith('.mhd')]
    # for f in names:
    #     file_path=os.path.join(path,f)
    #     ctime=os.path.getctime(file_path)
    #     ctime_dict[f]=ctime
    # sort_dict=sorted(ctime_dict.items(),key=lambda item:item[1],reverse=True)
    # filename=sort_dict[0][0].split('.')[0]
    connect = mysql.connect()
    cursor = connect.cursor()
    username=request.cookies.get('uname')
    sql="Select * from image_save where username='"+username+"'"
    cursor.execute(sql)
    all_data=cursor.fetchall()
    length=len(all_data)
    data=all_data[length-1]
    filepath=data[1]
    filename=filepath.split('/')[3]
    filename=filename.split('.')[0]
    n,result,kind,prob=get_result(filename)
    if n==-1:
        return render_template("showMiddle.html")
    else:
        flag=1
    return render_template('showresult.html',num=n,flag=flag,filename=filename,result=result,kind=kind,prob=prob)
@app.route('/searchhistory',methods=['GET','POST'])
def search_history():
    connect = mysql.connect()
    cursor = connect.cursor()
    username = request.cookies.get('uname')
    sql = "Select * from image_save where username='" + username + "'"
    cursor.execute(sql)
    all_data = cursor.fetchall()
    file_list=[]
    for temp in all_data:
        filename = temp[1].split('/')[3]
        file_list.append(filename)
    return render_template('show_history.html',files=file_list)
@app.route('/test/<name>',methods=['GET','POST'])
def test(name):
    print(name.split('(')[1].split(',')[1].replace(')',""))
    file_name=name.split('(')[1].split(',')[1].replace(')',"").split('.')[0]
    n, result, kind, prob = get_result(file_name)
    if n==-1:
        return render_template("showMiddle.html")
    else:
        flag = 1
    return render_template('showresult.html', num=n, flag=flag, filename=file_name, result=result, kind=kind, prob=prob)
if __name__ =='__main__':
    app.run(debug=True)
