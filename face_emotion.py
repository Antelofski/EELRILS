import dlib  # 人脸识别
import cv2  # 图像处理
import time


class face_emotion():

    def __init__(self):
        # 使用特征提取器get_frontal_face_detector
        self.detector = dlib.get_frontal_face_detector()
        # dlib的68点模型，使用dlib库官方训练好的特征预测器
        self.predictor = dlib.shape_predictor("predictor/shape_predictor_68_face_landmarks.dat")
        # 建cv2摄像头对象，这里使用电脑自带摄像头，如果接了外部摄像头，则自动切换到外部摄像头
        self.cap = cv2.VideoCapture(0)
        self.cap = cv2.VideoCapture("2.mp4")  # 打开视频
        # 设置视频参数，propId设置的视频参数，value设置的参数值
        self.cap.set(3, 480)

    def distance2(self, x1, y1, x2, y2):  # 计算两点欧式距离的平方
        dis = pow(x1 - x2, 2) + pow(y1 - y2, 2)
        return dis

    def learning_face(self, mode, fileName):
        flag_e = 0
        def distance(p1, p2):  # 计算两点欧式距离的平方（输入mark点即可计算）
            dis = pow((shape.part(p1).x - shape.part(p2).x), 2) + pow((shape.part(p1).y - shape.part(p2).y), 2)
            return dis

        if mode == 0:  # 模式选择
            self.cap = cv2.VideoCapture(0)  # 打开摄像头
        else:
            self.cap = cv2.VideoCapture(fileName)  # 打开视频
        # 参数初始化
        areaLastFace = 1
        count_nan = 0
        count_warning = 0
        count_break = 0
        status_code = 0  # 0Natural 1Sad
        tic = time.perf_counter()
        while (self.cap.isOpened()):
            if time.perf_counter() - tic >= 10:  # 10s退出
                break
            flag, im_rd = self.cap.read()
            k = cv2.waitKey(1)
            # 取灰度以适应
            try:
                try:
                    img_gray = cv2.cvtColor(im_rd, cv2.COLOR_RGB2GRAY)
                    img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)
                except:
                    img_gray = im_rd
                    img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)  # 表示高斯内核的长与宽都是3，标准差取0
            except:
                break
            # 使用人脸检测器检测图像中的人脸
            faces = self.detector(img_gray, 0)
            # 字体
            font = cv2.FONT_HERSHEY_SIMPLEX
            # 如果检测到人脸
            if (len(faces) != 0):
                # 对每个人脸都标出68个特征点
                areaMaxFace = 0
                for i in range(len(faces)):  # 选出最大面积的脸
                    if faces[i].area() > areaMaxFace:
                        areaMaxFace = faces[i].area()
                        indexMax = i
                    print("第" + str(i) + "个脸面积：" + str(faces[i].area()))
                print("最大脸面积：" + str(faces[indexMax].area()) + "\n")  # 打印出最大的脸
                print(faces[indexMax])
                for i in range(len(faces)):
                    for k, d in enumerate(faces):  # enumerate方法同时返回数据对象的索引和数据，k为索引，d为faces中的对象
                        # 对所有面部进行框选（但不是对所有面部处理）
                        # 用红色矩形框出人脸
                        cv2.rectangle(im_rd, (d.left(), d.top()), (d.right(), d.bottom()), (0, 0, 255))
                        # 计算人脸热别框边长
                        self.face_width = d.right() - d.left()
                        if indexMax != k:  # 进入下面后，仅处理最大的面部
                            continue
                        if (faces[indexMax].area() / areaLastFace) < 0.3:  # 如果面积变为原来的一半或更小，则进入等待状态（增加追踪头部的稳定性）
                            count_nan += 1
                            if count_nan >= 10:
                                areaLastFace = faces[indexMax].area()  # 在脸部面积上，10次都没有找到应追踪的面部，则接受最新的最大面部面积
                                count_nan = 0
                            continue
                        else:
                            areaLastFace = faces[indexMax].area()  # 若没有缩小则继续下面的程序
                        # 使用预测器得到68点数据的坐标
                        shape = self.predictor(img_gray, d)
                        # 圆圈显示每个特征点
                        for i in range(68):
                            cv2.circle(im_rd, (shape.part(i).x, shape.part(i).y), 2, (0, 255, 0), -1, 8)
                        # 计算提取的特征参数D2、D3、D4、D5
                        D2 = self.distance2((shape.part(20).x + shape.part(25).x) / 2,
                                            (shape.part(20).y + shape.part(25).y) / 2,
                                            (shape.part(42).x + shape.part(47).x) / 2,
                                            (shape.part(42).y + shape.part(47).y) / 2) / faces[k].area()
                        D3 = (distance(45, 47) + distance(44, 48) + distance(39, 41) + distance(38, 42)) / 4 / faces[
                            k].area()
                        D4 = distance(52, 58) / faces[k].area()
                        D5 = distance(49, 55) / faces[k].area()

                        print(D2, D3, D4, D5)

                        th4 = 0.038845
                        th5 = 0.059244
                        th2 = 0.017198
                        th3 = 0.12
                        th5_2 = 0.0334201
                        # 分情况讨论
                        if D4 < th4 and D5 < th5 and D2 > th2 and D5 > th5_2 or D3 < th3:
                            status_code = 1  # Sad
                            cv2.putText(im_rd, "Sad", (d.left(), d.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 255), 2, 4)
                        else:
                            status_code = 0  # Natural
                            cv2.putText(im_rd, "Natural", (d.left(), d.bottom() + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                        (0, 0, 255), 2, 4)

                # 标出人脸数
                cv2.putText(im_rd, "Faces: " + str(len(faces)), (20, 50), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
            else:
                # 没有检测到人脸
                cv2.putText(im_rd, "No Face", (20, 50), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
                status_code = 0
            # 窗口显示
            cv2.imshow('Caring System', im_rd)  # imshow需要输入gbk编码的中文字符，解决方案并不完美，这里使用英文
            k = cv2.waitKey(10)
            if status_code == 1:
                count_warning += 1
            if status_code == 0:
                count_warning = 0
            if count_warning >= 5:
                flag_e = 1
            # while 1:
            #     if count_warning != 0:
            #         count_break += 1
            #         if count_break >= 10:
            #             count_warning = 0
            #             count_break = 0
            #     if status_code == 0:  # Natural正常
            #         break
            #     elif status_code == 1:  # Sad悲伤
            #         count_warning += 1
            #         if count_warning <= 5:
            #             break
            #         else:
            #             flag = 1
            #             break
            # 如果图片模式,则在此暂停，避免错误
            if mode == 2:
                input()
        # 释放摄像头/视频源
        self.cap.release()
        # 删除窗口
        cv2.destroyAllWindows()
        if flag_e == 1:
            return 'Sad'
        else:
            return 'Natural'
