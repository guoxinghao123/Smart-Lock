import cv2
import face_recognition

# 记得根据你的实际情况，确认这里是 0 还是 1
cap = cv2.VideoCapture(1) 

if not cap.isOpened():
    print("❌ 无法打开摄像头！")
    exit()

print("\n🚀 【智能人脸雷达】已启动！")
print("👉 请正对摄像头，等待画面中你的脸被【绿色方框】圈中。")
print("👉 只有出现绿框时，按下【空格键】保存才有效！")
print("👉 按下【Q 键】退出。")

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    # 缩小画面加快检测速度 (缩小到 1/2)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    
    # 【修复核心】：使用 OpenCV 原生函数进行颜色转换，保证内存连续性
    # 顺便兼容一下 iVCam 等虚拟摄像头可能输出的 4 通道(BGRA)画面
    if small_frame.shape[2] == 4:
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGRA2RGB)
    else:
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # 实时呼叫底层算法检测人脸
    face_locations = face_recognition.face_locations(rgb_small_frame)

    # 如果检测到了人脸
    if face_locations:
        for (top, right, bottom, left) in face_locations:
            # 将坐标放大回原图尺寸
            top *= 2; right *= 2; bottom *= 2; left *= 2
            # 画一个绿色的框
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        
        cv2.putText(frame, "Face Locked! Press SPACE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        # 没检测到人脸时提示红色文字
        cv2.putText(frame, "No Face! Adjust lighting/angle", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Smart AI Radar", frame)
    
    key = cv2.waitKey(1)
    
    if key == 32:  # 按下空格键
        if face_locations:
            # 只有在检测到人脸时才允许保存
            cv2.imwrite("my_face.jpg", frame)
            print("\n🎉 完美！AI 已经牢牢记住了你的脸，照片已保存为 'my_face.jpg'")
            break
        else:
            print("⚠️ 别急！AI 还没看清你的脸，请等绿框出现再按空格！")
            
    elif key == ord('q') or key == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()