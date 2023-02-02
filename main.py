import time
import voice_record
import datetime
from asr_json import *
from SMS import SMS_send
from face_emotion import face_emotion
#from Serial import *

csv_record = open('record.csv', 'a')

if __name__ == "__main__":  # 主函数
    # serialStart()
    my_face = face_emotion()  # 实例化
    sad_count = 0
    tic = time.perf_counter()  # tic初始化
    el_name = '郝小子'
    sent_flag = 'False'

    #ser = serial.Serial(find_com(), 9600, timeout=0.1)  # 打开搜索到的能返回的串口
    #initSerial(ser)
   # serialCMD(ser, 'PASSION_MUSIC')     # 播放PASSION的音乐
    while 1:
        emotion = my_face.learning_face(0, "test_data/6.mp4")  # '0摄像头模式，1视频模式，2图片模式，第二参数是文件名.
        print(emotion)
        voice_record.get_audio()
        word, NLP_result = voice_API()
        print('NLP_result[0] = ' + str(NLP_result))
        now_time = datetime.datetime.now()
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.datetime.now().strftime('%H:%M')
        # 记录
        print('sad_count = ' + str(sad_count))
        if NLP_result == '0':
            word = 'None'
            sentiment = 'None'
            confidence = 'None'
            negative_prob = 'None'
        else:
            sentiment = NLP_result[0]['sentiment']
            confidence = NLP_result[0]['confidence']
            negative_prob = NLP_result[0]['negative_prob']
        if emotion == 'Sad':
            tic = time.perf_counter()
            sad_count += 1
        if time.perf_counter() - tic >= 10 * 60:  # 10分钟后无新的sad则清零sad_count
            sad_count = 0
        if sad_count >= 2:  # 10分钟内有2次记录到sad则发送短信
            serialCMD(ser, 'SOFT_MUSIC')    # 播放soft音乐并调整灯光
            sent_flag = 'Ture'
            sad_count = 0
            print('发送中')
            SMS_send('郝', '郝小子')
            print('发送成功')
        csv_record = open('record.csv', 'a')
        csv_record.write('\n' +
                         date_str + ', ' + time_str + ', ' + el_name + ', ' + emotion + ', ' + word + ', ' + str(
                        sentiment) + ', ' \
                         + str(confidence) + ', ' + str(negative_prob) + ', ' + sent_flag)
        csv_record.close()
        sent_flag = 'False'
