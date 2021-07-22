from flask import Flask, render_template, redirect, url_for, request

import sys
import os
# from konlpy.tag import Mecab

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
        # sent = str(request.form['mouth'])
        sent = request.form.get("mouth")

        result = load.pipeline(sent)
        print(result)
        # mecab = Mecab()
        # stnc_pos = mecab.pos(sent)

        # nouns = [n for n, tag in stnc_pos if tag in ["NR","NNG","NNP","NP","VV","VV+EC"] ]
        # print(f"this is nouns = {nouns}")
        # ###########################태깅 후 애니메이션 처리된 페이지 반환#######################
        new_path = os.path.abspath(os.path.dirname(__file__))[:-14] +'morpheme_and_video_concat'
        print('new_path: ',new_path)
        sys.path.append(new_path)        
        
        # 사람 한 명이 수화
        import morpheme_and_video_concat_person as mv

        # 사람 여러 명이 수화
        # import morpheme_and_video_concat_people as mv
        
        path = ''
        path = mv.main(result)
        print(path+"-----------------------------------------")
        # tmp = ''
        # for i in range(len(path)):
        #     tmp += path[i]

        #     if path[i] == '/':

        #         tmp = ''
        #         continue
            # elif tmp == 'cheong_gaeguri':
            #     path = '/' + path[i+2:]
            #     print(path)
            #     break
                
        return render_template('mouth.html' ,cont = path, res = "번역 결과 : \n\n" + str(result))
    
        
@app.route('/ear',methods = ['GET', 'POST'])
def ear():
    new_path = os.path.abspath(os.path.dirname(__file__))[:-14] + 'SLR-frog/SL-GCN'
    sys.path.append(new_path)
    import main as ktw

    if request.method=="GET":
        return render_template("ear.html")

    
    elif request.method == 'POST':
        
        # js_variable = request.form
        value = list(dict(request.form).keys())[0]#영상 이름 추출
        res = ktw.pipeline(list(dict(request.form).keys())[0])#keypoints -> words
        print("this res : " + res)
        
        # res = request.form.get("ear_me")
        # print(res+"aa")

        return render_template('ear.html', res=res)
    

if __name__ == "__main__":
    app.run(debug = True,port = 5000)