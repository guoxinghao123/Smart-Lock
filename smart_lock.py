import cv2
import numpy as np
from insightface.app import FaceAnalysis
import platform
import ctypes
import os
import time
import sys

# 兼容 .py 源码运行和 .exe 打包运行，确保永远能在程序旁边找到照片
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# 强制在程序本体所在的绝对路径下寻找照片
MY_FACE_PATH = os.path.join(application_path, "my_face.jpg") 

CAMERA_ID = 1                  # 你的可用摄像头编号
MISSING_TIMEOUT = 5.0          # 离开画面 5 秒后自动锁屏
SIMILARITY_THRESHOLD = 0.45    # AI 认人的严格程度 (0.4-0.5 最佳)
PROCESS_EVERY_N_FRAMES = 5     # 每 5 帧做一次深度推理，保证低 CPU 占用和画面丝滑
# ==========================================================

def lock_screen():
    """执行系统级别的锁屏指令"""
    sys_name = platform.system()
    try:
        if sys_name == 'Windows':
            ctypes.windll.user32.LockWorkStation()
        elif sys_name == 'Darwin':
            os.system('pmset displaysleepnow')
        elif sys_name == 'Linux':
            os.system('xdg-screensaver lock')
    except Exception as e:
        print(f"锁屏执行失败: {e}")

def main():
    print("==================================================")
    print("🚀 正在初始化 InsightFace 深度学习大模型 (离线模型)...")
    print("==================================================")
    
    # 强制使用 CPU 进行推理，buffalo_l 是高精度模型
    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(320, 320)) 

    print("\n正在加载你的面部“生物密钥”...")
    my_image = cv2.imread(MY_FACE_PATH)
    if my_image is None:
        print(f"❌ 读取照片失败！请确保以下路径存在照片:\n{MY_FACE_PATH}")
        input("按回车键退出...")
        return
    
    my_faces = app.get(my_image)
    if len(my_faces) == 0:
        print("❌ 照片中未检测到人脸，请重新用正脸拍照！")
        input("按回车键退出...")
        return
    
    my_embedding = my_faces[0].normed_embedding
    print("✅ 密钥加载成功！安防级别：商用级")

    video_capture = cv2.VideoCapture(CAMERA_ID)
    if not video_capture.isOpened():
        print("❌ 无法打开摄像头，请检查 CAMERA_ID 设置或设备连接！")
        input("按回车键退出...")
        return

    print(f"\n🛡️ 防窥屏安保系统已启动！")
    print("👉 请在弹出的视频窗口中按【Q 键】退出程序。")

    missing_start_time = None 
    frame_count = 0
    cached_faces = []
    status_text = "System: SECURE"
    status_color = (0, 255, 0)
    trigger_lock = False

    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue
        
        frame_count += 1

        # 【核心逻辑】：跳帧推理
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            faces = app.get(frame)
            cached_faces = []

            # 分支 1：画面里没人
            if len(faces) == 0:
                if missing_start_time is None:
                    missing_start_time = time.time()
                else:
                    elapsed_time = time.time() - missing_start_time
                    status_text = f"AWAY: Lock in {max(0, MISSING_TIMEOUT - elapsed_time):.1f}s"
                    status_color = (0, 165, 255) 
                    
                    if elapsed_time > MISSING_TIMEOUT:
                        print(f"\n⚠️ 连续 {MISSING_TIMEOUT} 秒未检测到主人，触发离开锁屏！")
                        trigger_lock = True
                        missing_start_time = None 
            
            # 分支 2：画面里有人
            else:
                missing_start_time = None 
                status_text = "System: SECURE"
                status_color = (0, 255, 0)
                
                for face in faces:
                    bbox = face.bbox.astype(int)
                    left, top, right, bottom = bbox[0], bbox[1], bbox[2], bbox[3]
                    
                    face_embedding = face.normed_embedding
                    similarity = np.dot(my_embedding, face_embedding)

                    if similarity > SIMILARITY_THRESHOLD:
                        name = f"SAFE ({similarity:.2f})" 
                        box_color = (0, 255, 0)
                    else:
                        name = f"WARNING!!! ({similarity:.2f})"
                        box_color = (0, 0, 255)
                        status_text = "System: INTRUDER DETECTED!"
                        status_color = (0, 0, 255)
                        trigger_lock = True
                        print(f"\n🚨 警报：发现非授权人员！(相似度: {similarity:.2f})")

                    cached_faces.append(((top, right, bottom, left), name, box_color))

        # ============ UI 绘制 (确保每一帧都执行，保持画面丝滑) ============
        for (top, right, bottom, left), name, box_color in cached_faces:
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, status_color, 2)
        cv2.imshow('Smart Lock AI Radar - Ultimate', frame)

        # 键盘退出监听
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("手动退出监控系统。")
            break

        # 锁屏触发逻辑
        if trigger_lock:
            lock_screen()
            print("程序休眠 5 秒...")
            time.sleep(5) 
            print("🛡️ 重新开始监控...")
            trigger_lock = False
            missing_start_time = None 

    # 释放资源
    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()