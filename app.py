import streamlit as st
import yt_dlp
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="VK Video Frames", layout="wide")

st.title("🖼️ مستخرج فريمات فيديو VK")
st.write("ضع رابط الفيديو من vkvideo.ru بالأسفل لاستخراج صور منه.")

vk_url = st.text_input("أدخل رابط الفيديو:")

if st.button("ابدأ المعالجة"):
    if vk_url:
        with st.spinner('جاري استخراج الرابط والمعالجة...'):
            try:
                # إعدادات yt-dlp للحصول على الرابط المباشر
                ydl_opts = {'format': 'best'}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(vk_url, download=False)
                    video_url = info['url']
                    st.success(f"تم العثور على: {info.get('title', 'Video')}")

                # استخدام OpenCV لفتح الفيديو من الرابط المباشر
                cap = cv2.VideoCapture(video_url)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                if total_frames > 0:
                    cols = st.columns(4)
                    # استخراج 8 صور موزعة على طول الفيديو
                    for i in range(1, 9):
                        frame_pos = (total_frames // 9) * i
                        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                        ret, frame = cap.read()
                        if ret:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            with cols[(i-1)%4]:
                                st.image(frame_rgb, caption=f"صورة {i}")
                cap.release()
            except Exception as e:
                st.error(f"خطأ: {e}")
    else:
        st.warning("يرجى إدخال الرابط أولاً.")
