import streamlit as st
import yt_dlp
import cv2
import os

st.set_page_config(page_title="VK Video Frames", layout="wide")
st.title("🖼️ مستخرج فريمات فيديو VK")

vk_url = st.text_input("أدخل رابط الفيديو:")

if st.button("ابدأ المعالجة"):
    if vk_url:
        status = st.empty()
        progress_bar = st.progress(0)
        
        try:
            # 1. إعدادات التحميل (تحميل أقل جودة لتوفير الوقت والسعة)
            status.info("جاري فحص الفيديو وتجهيزه...")
            ydl_opts = {
                'format': 'worst', # نختار أقل جودة لأننا نريد صوراً فقط
                'outtmpl': 'temp_video.mp4',
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                status.info("جاري تحميل مقطع صغير للمعالجة...")
                ydl.download([vk_url])
            
            # 2. فتح ملف الفيديو المحمل
            cap = cv2.VideoCapture('temp_video.mp4')
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames > 0:
                status.success("تم التحميل بنجاح! جاري استخراج الصور...")
                cols = st.columns(4)
                for i in range(1, 5):
                    # اختيار فريمات موزعة
                    frame_pos = (total_frames // 5) * i
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = cap.read()
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        with cols[i-1]:
                            st.image(frame_rgb, caption=f"فريم {i}")
                    progress_bar.progress(i * 25)
            else:
                st.error("فشل في قراءة ملف الفيديو.")
                
            cap.release()
            # حذف الملف المؤقت لتوفير المساحة
            if os.path.exists("temp_video.mp4"):
                os.remove("temp_video.mp4")
                
        except Exception as e:
            st.error(f"حدث خطأ تقني: {e}")
    else:
        st.warning("يرجى وضع الرابط أولاً.")
