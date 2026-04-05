import streamlit as st
import yt_dlp
import cv2
import os
import zipfile
import io
import numpy as np

# إعداد الصفحة
st.set_page_config(page_title="VK HD Extractor", layout="wide")
st.title("🎬 مستخرج فريمات VK بجودة أصلية")

vk_url = st.text_input("أدخل رابط فيديو VK:")

if vk_url:
    try:
        # 1. جلب معلومات الفيديو
        with st.spinner('جاري فحص الفيديو...'):
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vk_url, download=False)
                duration = int(info.get('duration', 0))
                title = info.get('title', 'video')

        st.success(f"✅ متصل: {title} ({duration} ثانية)")

        # 2. واجهة التحكم
        start_time, end_time = st.slider("اختر النطاق الزمني (بالثواني):", 
                                        0, duration, (0, min(2, duration)))
        
        if st.button("🚀 استخراج الفريمات الأصلية"):
            if end_time - start_time > 10:
                st.warning("⚠️ يرجى اختيار مقطع أقل من 10 ثوانٍ لضمان استقرار السيرفر.")
            else:
                progress_bar = st.progress(0)
                status = st.empty()
                
                # 3. تحميل المقطع (بأفضل جودة فيديو متوفرة)
                temp_file = "high_res_clip.mp4"
                status.info("جاري تحميل المقطع المختار بأعلى جودة...")
                
                ydl_args = {
                    'format': 'bestvideo/best', # نركز على أفضل جودة فيديو
                    'outtmpl': temp_file,
                    'download_sections': [{'start_time': start_time, 'end_time': end_time}],
                    'force_keyframes_at_cuts': True,
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_args) as ydl:
                    ydl.download([vk_url])
                
                # 4. استخراج الصور
                status.info("جاري معالجة الفريمات...")
                cap = cv2.VideoCapture(temp_file)
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                    count = 0
                    while True:
                        ret, frame = cap.read()
                        if not ret: break
                        
                        # تحويل الفريم لصورة JPG عالية الجودة (95%)
                        _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        zip_file.writestr(f"frame_{count:03d}.jpg", img_encoded.tobytes())
                        count += 1
                
                cap.release()
                
                if count > 0:
                    status.success(f"✅ تم استخراج {count} فريم بنجاح!")
                    st.download_button(
                        label="📥 تحميل ملف الصور (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name=f"{title}_HD_frames.zip",
                        mime="application/zip"
                    )
                else:
                    st.error("فشل استخراج الصور، حاول مرة أخرى.")
                
                # حذف الملف المؤقت فوراً لتوفير مساحة السيرفر
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    except Exception as e:
        st.error(f"خطأ تقني: {e}")
