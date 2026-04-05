import streamlit as st
import yt_dlp
import cv2
import os
import zipfile
import io

st.set_page_config(page_title="VK Frame Extractor", layout="wide")
st.title("🎬 مستخرج مقاطع الفريمات من VK")

# 1. إدخال الرابط والحصول على معلومات الفيديو أولاً
vk_url = st.text_input("أدخل رابط فيديو VK:")

if vk_url:
    try:
        with st.spinner('جاري فحص مدة الفيديو...'):
            ydl_opts = {'format': 'worst', 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vk_url, download=False)
                duration = info.get('duration', 0)
                video_url = info['url']
                title = info.get('title', 'video')

        st.success(f"📺 فيديو: {title} | المدة: {duration} ثانية")

        # 2. واجهة اختيار المقطع الزمني
        st.subheader("حدد المقطع لاستخراج كافة الفريمات منه:")
        start_time, end_time = st.slider("اختر البداية والنهاية (بالثواني):", 
                                        0, duration, (0, min(5, duration)))
        
        if st.button("استخراج كافة فريمات المقطع"):
            if end_time - start_time > 10:
                st.warning("⚠️ يرجى اختيار مقطع أقل من 10 ثوانٍ لتجنب بطء السيرفر.")
            else:
                progress_bar = st.progress(0)
                status = st.empty()
                
                # تحميل المقطع الصغير فقط
                status.info("جاري معالجة المقطع المختار...")
                cap = cv2.VideoCapture(video_url)
                fps = cap.get(cv2.CAP_PROP_FPS)
                start_frame = int(start_time * fps)
                end_frame = int(end_time * fps)
                
                cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
                
                frames_buffer = []
                current_frame = start_frame
                
                # استخراج الفريمات
                while current_frame <= end_frame:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    # تصغير حجم الصورة لتقليل المساحة
                    frame_small = cv2.resize(frame, (480, 270)) 
                    _, buffer = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 50])
                    frames_buffer.append(buffer)
                    
                    current_frame += 1
                    progress_bar.progress(min((current_frame - start_frame) / (end_frame - start_frame), 1.0))

                cap.release()
                
                # 3. تجهيز ملف ZIP للتحميل
                if frames_buffer:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                        for idx, frame_data in enumerate(frames_buffer):
                            zip_file.writestr(f"frame_{idx}.jpg", frame_data.tobytes())
                    
                    st.success(f"✅ تم استخراج {len(frames_buffer)} فريم!")
                    st.download_button(
                        label="📥 تحميل كافة الفريمات (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="extracted_frames.zip",
                        mime="application/zip"
                    )
                    
                    # عرض عينة صغيرة (أول 4 فريمات)
                    st.write("معاينة لأول 4 فريمات:")
                    cols = st.columns(4)
                    for i in range(min(4, len(frames_buffer))):
                        cols[i].image(frames_buffer[i].tobytes())

    except Exception as e:
        st.error(f"خطأ: {e}")
