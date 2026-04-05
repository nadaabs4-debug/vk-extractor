import streamlit as st
import yt_dlp
import cv2
import os
import zipfile
import io
import numpy as np

# إعداد الصفحة لتكون بسيطة
st.set_page_config(page_title="VK HD Extractor")

st.title("🎬 مستخرج فريمات VK بجودة أصلية")

vk_url = st.text_input("أدخل رابط فيديو VK:")

if vk_url:
    try:
        # جلب معلومات الفيديو
        ydl_opts = {'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(vk_url, download=False)
            duration = int(info.get('duration', 0))
            title = info.get('title', 'video')

        st.success(f"✅ متصل: {title}")

        # تحديد النطاق الزمني
        start_time, end_time = st.slider("اختر الثواني (البداية والنهاية):", 
                                        0, duration, (0, min(2, duration)))
        
        if st.button("🚀 استخراج الصور"):
            if end_time - start_time > 10:
                st.warning("⚠️ اختر مقطعاً أقل من 10 ثوانٍ.")
            else:
                with st.status("جاري المعالجة... (قد تستغرق دقيقة)", expanded=True) as status:
                    temp_file = "clip.mp4"
                    
                    # تحميل المقطع بأفضل جودة
                    ydl_args = {
                        'format': 'bestvideo/best',
                        'outtmpl': temp_file,
                        'download_sections': [{'start_time': start_time, 'end_time': end_time}],
                        'force_keyframes_at_cuts': True,
                        'quiet': True
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_args) as ydl:
                        ydl.download([vk_url])
                    
                    # استخراج الصور وحفظها في ZIP مباشرة
                    cap = cv2.VideoCapture(temp_file)
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                        count = 0
                        while True:
                            ret, frame = cap.read()
                            if not ret: break
                            
                            # جودة عالية (95) وبدون تصغير الحجم
                            _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                            zip_file.writestr(f"frame_{count:03d}.jpg", img_encoded.tobytes())
                            count += 1
                    
                    cap.release()
                    
                    if count > 0:
                        status.update(label="✅ اكتمل الاستخراج!", state="complete")
                        st.download_button(
                            label="📥 تحميل ملف الصور (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="high_res_frames.zip",
                            mime="application/zip"
                        )
                    
                    if os.path.exists(temp_file):
                        os.remove(temp_file)

    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
