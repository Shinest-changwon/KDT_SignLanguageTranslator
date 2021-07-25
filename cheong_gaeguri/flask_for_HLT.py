from flask import Flask, render_template, redirect, url_for, request

import sys
import os

import model_load_pipeline as load
import tensorflow as tf

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def main():
    return render_template("index.html")

@app.route('/mouth',methods = ['GET', 'POST'])
def mouth(): 

    

    if request.method == 'GET':
        return render_template("mouth.html")



    if request.method == 'POST':
        sent = request.form.get("mouth")

        result = load.pipeline(sent)
        print(result)
    
        new_path = os.path.abspath(os.path.dirname(__file__))[:-14] +'morpheme_and_video_concat'
        sys.path.append(new_path)        
        
        #형태소 분석 - 어순 - 동영상 생성 스크립트
        import morpheme_and_video_concat_person as mv
        
        path = ''
        path = mv.main(result)
                
        return render_template('mouth.html' ,cont = path, res = "번역 결과 : \n\n" + str(result))
    
        
@app.route('/ear',methods = ['GET', 'POST'])
def ear():
    new_path = os.path.abspath(os.path.dirname(__file__))[:-14] + 'SLR-frog/SL-GCN'
    sys.path.append(new_path)
    import main as ktw

    if request.method=="GET":
        return render_template("ear.html")

    
    elif request.method == 'POST':

        value = list(dict(request.form).keys())[0]#영상 이름 추출
        res = ktw.pipeline(list(dict(request.form).keys())[0])#keypoints -> words
        print("this res : " + res)

        return render_template('ear.html', res=res)
    

if __name__ == "__main__":
    app.run(debug = True,port = 5000)