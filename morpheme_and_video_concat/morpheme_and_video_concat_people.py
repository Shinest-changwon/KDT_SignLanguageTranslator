from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import cv2
import json
import imutils
import pandas as pd
from PIL import ImageFont, ImageDraw, Image
import numpy as np

tmp = ""
for i in os.path.realpath(__file__):
    tmp+=i 
    if "morpheme_and_video_concat" in tmp:
        break

os.chdir(tmp)

"""
이 코드는 STT로 음성을 한글 문장으로 변환한 후 형태소 분해 리스트를 입력으로 받아 concated video 파일을 생성하고 그 경로를 반환하는 코드.

# 예시
입력: stnc_pos = ['마을버스', '일번']
출력: path = main(stnc_pos)
      path 변수에 concated video 파일 경로가 저장된다.
"""

"""
파일 경로  
root  
  ├morpheme  
  │ └1.Training
  │   ├[라벨링]01_real_word_morpheme  
  │   │ └morpheme 
  │   │   ├01  
  │   │   │├NIA_SL_WORD0001_REAL01_D_morpheme.json  
  │   │   │├NIA_SL_WORD0001_REAL01_F_morpheme.json  
  │   │   │├NIA_SL_WORD0001_REAL01_L_morpheme.json  
  │   │   │├NIA_SL_WORD0001_REAL01_R_morpheme.json  
  │   │   │├NIA_SL_WORD0001_REAL01_U_morpheme.json  
  │   │   │├...  
  │   │   │└NIA_SL_WORD3000_REAL01_U_morpheme.json # 3,000개 단어  
  │   │   ├...
  │   │   │
  │   │   └16
  │   │   
  │   └[라벨링]01_real_sen_morpheme  
  │      └morpheme 
  │        ├01  
  │        │├NIA_SL_SEN0001_REAL01_D_morpheme.json  
  │        │├NIA_SL_SEN0001_REAL01_F_morpheme.json  
  │        │├NIA_SL_SEN0001_REAL01_L_morpheme.json  
  │        │├NIA_SL_SEN0001_REAL01_R_morpheme.json  
  │        │├NIA_SL_SEN0001_REAL01_U_morpheme.json  
  │        │├...  
  │        │└NIA_SL_SEN2000_REAL01_U_morpheme.json # 2,000개 문장  
  │        │
  │        ├...  
  │        │
  │        └16
  │  
  └video
    ├word # 0~1500번 영상은 짝수 폴더, 1501~3000번 영상은 홀수 폴더
    │  ├[원천]01_real_word_video
    │  │  └01-1
    │  │    ├NIA_SL_WORD1501_REAL_D.mp4  
    │  │    ├NIA_SL_WORD1501_REAL_F.mp4
    │  │    ├NIA_SL_WORD1501_REAL_L.mp4
    │  │    ├NIA_SL_WORD1501_REAL_R.mp4
    │  │    ├NIA_SL_WORD1501_REAL_U.mp4
    │  │    ├...
    │  │    └NIA_SL_WORD3001_REAL_F.mp4 # '데려가다' 추가(3001번)
    │  ├[원천]02_real_word_video
    │  │  └01
    │  │    ├NIA_SL_WORD0001_REAL_D.mp4  
    │  │    ├NIA_SL_WORD0001_REAL_F.mp4
    │  │    ├NIA_SL_WORD0001_REAL_L.mp4
    │  │    ├NIA_SL_WORD0001_REAL_R.mp4
    │  │    ├NIA_SL_WORD0001_REAL_U.mp4
    │  │    ├...
    │  │    └NIA_SL_WORD1500_REAL_U.mp4
    │  │  
    │  ├...
    │  │
    │  └[원천]32_real_word_video
    │
    └sen # 0~1500번 영상은 홀수 폴더, 1501~3000번 영상은 짝수 폴더
       ├[원천]01_real_sen_video
       │  └01
       │    ├NIA_SL_SEN0001_REAL_D.mp4  
       │    ├NIA_SL_SEN0001_REAL_F.mp4
       │    ├NIA_SL_SEN0001_REAL_L.mp4
       │    ├NIA_SL_SEN0001_REAL_R.mp4
       │    ├NIA_SL_SEN0001_REAL_U.mp4
       │    ├...
       │    └NIA_SL_SEN1500_REAL_U.mp4
       ├[원천]02_real_word_video
       │  └01-1
       │    ├NIA_SL_SEN1501_REAL_D.mp4  
       │    ├NIA_SL_SEN1501_REAL_F.mp4
       │    ├NIA_SL_SEN1501_REAL_L.mp4
       │    ├NIA_SL_SEN1501_REAL_R.mp4
       │    ├NIA_SL_SEN1501_REAL_U.mp4
       │    ├...
       │    └NIA_SL_SEN3000_REAL_U.mp4
       │  
       ├...
       │
       └[원천]32_real_word_video
  
"""

# 문장 번호 찾기
def find_sen_num(stnc_pos): # stnc_pos = ['여기', '1호', '되다']
    
    df = pd.read_csv('sen.csv',encoding = 'utf-8')
    
    # 컬럼 리스트 만들기
    col_list = df.columns[4:] # ['한국수어 형태소', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11']
    # 형태소와 일치하는 문장 csv파일에서 찾기
    for i in range(len(stnc_pos)):
        if i == 0:
            new = df[df[col_list[i]] == stnc_pos[i]]
        else:
            new = new[new[col_list[i]] == stnc_pos[i]]
    # index 번호 초기화
    new = new.reset_index(drop=True)

    # 문장 번호 찾기
    # 조건에 맞는 문장이 2개 이상일 경우 청인에게 선택하게 한 후 결정하고 싶다면 아래 코드 주석 해제
    # if new.shape[0]>=2:
    #     print('동일한 수어 형태소에 해당하는 한국어 문장을 2개 이상 발견했습니다. 정확한 표현의 번호를 입력해주세요.')
    #     for i in range(new.shape[0]):
    #         print('"'+new.iloc[i,2]+'" 는 '+str(i))
    #     while True:
    #         idx_num = int(input('번호를 입력해주세요: '))
    #         if idx_num in [n for n in range(new.shape[0])]:
    #             num = new.iloc[idx_num,0]
    #             break
    #         else:
    #             print('잘못된 입력입니다. 다시 입력해주세요.')
    # else: num = new.iloc[0,0]

    # 첫 번째 행이 정답일 때 문장 번호(위 코드 주석해제했다면 아래 코드 주석 적용)
    num = new.iloc[0,0]            
    return num

# 문장 영상 나누기(morpheme json 파일로부터 시작 프레임과 끝 프레임 알아내기)
def redefine_frame(num, i, rand_idx):
    # morpheme json 불러오기
    word_sen = 'sen'
    basic_path = os.getcwd() + '/morpheme/1.Training'
    print(basic_path)

    # 각 단어별 다른 사람을 사용하기 위해 morpheme json 파일 따로 불러오기
    person_num = str(i+rand_idx).zfill(2)
    json_path = basic_path+'/[라벨링]01_real_'+word_sen+'_morpheme/morpheme/'+person_num+'/NIA_SL_'+word_sen.upper()+str(num).zfill(4)+'_REAL'+person_num+'_F_morpheme.json'
    with open(json_path, 'r') as morpheme_json:
        morpheme_data = json.load(morpheme_json)
        fps = 30
        start_frame = int(round(morpheme_data['data'][i]['start']*fps,-1))
        end_frame = int(round(morpheme_data['data'][i]['end']*fps))
        text_in = morpheme_data['data'][i]['attributes'][0]['name']
    return start_frame, end_frame, person_num, text_in

# 해당하는 동영상 경로 찾기
def find_video_path(num, person_num):
    word_sen = 'sen'
    basic_path = os.getcwd()+'/video/'+word_sen+'/[원천]'
    print(basic_path)
    
    if word_sen == 'word': 
        if 0 <= num <=1500:
            vid_person_num = str(int(person_num)*2 - 1).zfill(2)
            vid_person_num_sub = person_num + '-1'
        else:
            vid_person_num = str(int(person_num)*2).zfill(2)
            vid_person_num_sub = person_num
    else:
        if 0 <= num <=1500:
            vid_person_num = str(int(person_num)*2 - 1).zfill(2)
            vid_person_num_sub = person_num
        else:
            vid_person_num = str(int(person_num)*2).zfill(2)
            vid_person_num_sub = person_num + '-1'
    vid_path = basic_path+vid_person_num+'_real_'+word_sen+'_video/'+vid_person_num_sub+'/NIA_SL_'+word_sen.upper()+str(num).zfill(4)+'_REAL'+person_num+'_F.mp4'
    return vid_path

def find_width_height_fps(vid_path):
    cap = cv2.VideoCapture(vid_path)
    w_frame, h_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return w_frame, h_frame, fps

# 새로운 frame & 영상 경로를 이용해 영상 자르고 mp4파일로 저장
def cut_frame_and_save(vid_path,start_frame,end_frame,idx, text_in):
    cap = cv2.VideoCapture(vid_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    file_name = 'result_'+str(idx)+'.mp4'
    w_frame, h_frame, fps = find_width_height_fps(vid_path)
    out = cv2.VideoWriter(file_name, fourcc, fps, (w_frame, h_frame))
    cnt=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        cnt+=1
        # Avoid problems when video finish
        if ret:
            # Saving from the desired frames
            if start_frame <= cnt <= end_frame:
                print('if 실행')
                try:
                    image2 = Image.fromarray(frame)
                    draw = ImageDraw.Draw(image2)
                    ######################kyeong-debug
                    # print(f"kyeong - debug -------- {w_frame//2-(len(text_in)*25)}")
                    # print(f"kyeong - debug -------- {int(h_frame*0.77)}")
                    # print(f"kyeong - debug -------- {text_in}")
                    try:
                        draw.text((w_frame//2-(len(text_in)*25),int(h_frame*0.77)), text_in, font=ImageFont.truetype("./NotoSansCJK-Black.ttc", 50), fill=(255,255,255))
                    except Exception as e:
                        print(e)
                    #222 - exception occured
                    # draw.text((w_frame//2-(len(text_in)*25),int(h_frame*0.77)), text_in, font=ImageFont.truetype("./NotoSansCJK-Black.ttc", 50), fill=(255,255,255))
                   
                    image3 = np.array(image2)
                    out.write(image3)
                    print('!!write 성공 !!')
                except Exception as e: 
                    print(f"cut_frame_and_save(method) : {e}")
        else:
            break
    cap.release()
    out.release()

# 형태소 리스트로부터 각 형태소에 해당하는 영상 잘라서 저장
def main1(stnc_pos):
    # 문장 번호 찾기
    num = find_sen_num(stnc_pos)
    print('num: ', num)
    # 사람 번호 랜덤으로 선정
    import random
    rand_idx = random.randint(1,15)
    print('rand_idx: ', rand_idx)
    # 반복문(형태소 개수만큼)
    for i in range(len(stnc_pos)):
        print('{}번째 시작'.format(i))
        start_frame, end_frame, person_num, text_in = redefine_frame(num, i, rand_idx)
        print('start_frame: {}, end_frame: {}, person_num: {}'.format(start_frame, end_frame, person_num))
        vid_path = find_video_path(num, person_num)
        print('vid path: ', vid_path)
        cut_frame_and_save(vid_path,start_frame,end_frame,i, text_in)

# 디렉토리에 있는 잘라진 영상 이어붙이기
def main2(stnc_pos):
    if len(stnc_pos) > 1:
        file_list = os.listdir(os.getcwd())
        video_list = [file_name for file_name in file_list if file_name.startswith('result')]
        video_list.sort()
        print('video list: ', video_list)
        caps = []
        for video in video_list:
            try:
                print(video)
                cap = VideoFileClip(video)
                caps.append(cap)

            except: print('실패!!')
        
        # 입력된 비디오 모두 concatenate
        final_clip = concatenate_videoclips(caps)
        new_path = os.path.abspath(os.path.dirname(__file__))[:-25] +'cheong_gaeguri'
        
        path = new_path+'/static/videos/final.mp4'
        final_clip.write_videofile(path)
    elif len(stnc_pos) == 1: print('영상 1개뿐.')
    else: print('영상 없음.')
    
def main(stnc_pos, is_ani=False):
    stnc_pos = stnc_pos.split(" ")[:-2]
    if not is_ani: # 실제 촬영 영상 짜집기 출력
        main1(stnc_pos)
        print('main1 완료')
        main2(stnc_pos)
        # concat한 비디오 경로 반환
        new_path = os.path.abspath(os.path.dirname(__file__))[:-25] +'cheong_gaeguri'
        
        path = new_path+'/static/videos/final.mp4'

    else: # 애니메이션 영상 경로 반환
        path = os.getcwd() + '/Ani_' + str(num) + '.mp4'
        """
        애니메이션 번호별 의미
        1157: 내가 데려다 드릴게요
        148: 마을버스 일번이요
        83: 여기서 1호선을 탈 수 있습니다. 
        """
  
    return path

# 코드 합칠 때에는 아래는 주석 처리
if __name__ == '__main__':
    """
    [시나리오 1번] - 영등포로 가고 싶은 농인
    문장번호 발화자
    (354)    농: 안녕하세요
    (116)    농: 1호선을 타는 곳은 어디인가요?
    (83)     청: 여기서 1호선을 탈 수 있습니다. --수어 구조 변환--> ['여기', '일호', '되다']

    [시나리오 2번] - 신도림역에서
    문장번호 발화자
    (1359)   농: 서울대학교 방향으로 가려면 어떻게 가나요?
    (385)    청: 지하철 갈아타는 곳으로 안내해 드릴까요? --수어 구조 변환--> ['지하철', '곳', '안내하다']
    (355)    농: 감사합니다.
    """    
    # # stnc_pos = ['지하철', '곳', '안내하다']
    # # stnc_pos =  ['여기', '1호', '되다']
    # # stnc_pos = "여기서 1호선을 탈 수 있습니다"
    # path = main(stnc_pos)
    # print('final path: ',path)
    