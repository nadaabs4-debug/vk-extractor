import streamlit as st
import yt_dlp
import cv2
import numpy as np

st.set_page_config(page_title="VK Video Frames", layout="wide")
st.title("🖼️ مستخرج فريمات فيديو VK")

vk_url = st.text_input("أدخل رابط الفيديو:")

if st.button("ابدأ المعالجة"):
    if vk_url:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text('جاري استخراج الرابط المباشر...')
            ydl_opts = {'format': 'best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vk_url, download=False)
                video_url = info['url']
            
            status_text.text('جاري فتح الفيديو ومعالجة الفريمات...')
            cap = cv2.VideoCapture(video_url)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames <= 0:
                st.error("عذراً، لا يمكن معالجة هذا الفيديو (قد يكون بث مباشر أو محمي).")
            else:
                cols = st.columns(4)
                # سنستخرج 4 صور فقط لتجربة السرعة أولاً
                for i in range(1, 5):
                    frame_pos = (total_frames // 5) * i
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
                    ret, frame = cap.read()
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        with cols[i-1]:
                            st.image(frame_rgb, caption=f"صورة {i}")
                    progress_bar.progress(i * 25)
                
                status_text.text('✅ اكتملت العملية!')
            cap.release()
            
        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {e}")
    else:
        st.warning("يرجى إدخال الرابط.")
