import streamlit as st
import yt_dlp
import cv2
import os
import zipfile
import io

st.set_page_config(page_title="VK Frame Extractor", layout="wide")
st.title("🎬 مستخرج مقاطع الفريمات من VK")

vk_url = st.text_input("أدخل رابط فيديو VK:")

if vk_url:
    try:
        # 1. الحصول على معلومات الفيديو والمدة
        with st.spinner('جاري فحص الفيديو...'):
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vk_url, download=False)
                duration = int(info.get('duration', 0))
                title = info.get('title', 'video')

        st.success(f"📺 فيديو: {title} | المدة: {duration} ثانية")

        # 2. تحديد المقطع
        st.subheader("حدد المقطع لاستخراج كافة الفريمات منه:")
        start_time, end_time = st.slider("اختر البداية والنهاية (بالثواني):", 
                                        0, duration, (0, min(5, duration)))
        
        if st.button("بدء استخراج الفريمات"):
            if end_time - start_time > 15:
                st.warning("⚠️ يرجى اختيار مقطع أقل من 15 ثانية لضمان سرعة المعالجة.")
            else:
                progress_bar = st.progress(0)
                status = st.empty()
                
                # 3. تحميل المقطع المحدد فقط باستخدام خاصية download_sections
                status.info(f"جاري تحميل المقطع من الثانية {start_time} إلى {end_time}...")
                
                temp_filename = "clip.mp4"
                ydl_clip_opts = {
                    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]', # جودة متوسطة للسرعة
                    'outtmpl': temp_filename,
                    'download_sections': [{'start_time': start_time, 'end_time': end_time}],
                    'force_keyframes_at_cuts': True,
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_clip_opts) as ydl:
                    ydl.download([vk_url])
                
                # 4. استخراج الفريمات من الملف المحمل
                status.info("جاري استخراج الصور من المقطع المحمل...")
                cap = cv2.VideoCapture(temp_filename)
                frames_buffer = []
                
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    # تصغير الصورة لتقليل حجم ملف الـ ZIP
                    frame_small = cv2.resize(frame, (640, 360)) 
                    _, buffer = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 60])
                    frames_buffer.append(buffer)
                
                cap.release()
                
                # 5. عرض النتائج وتحميل الـ ZIP
                if frames_buffer:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                        for idx, frame_data in enumerate(frames_buffer):
                            zip_file.writestr(f"frame_{idx:03d}.jpg", frame_data.tobytes())
                    
                    status.success(f"✅ تم استخراج {len(frames_buffer)} فريم بنجاح!")
                    st.download_button(
                        label="📥 تحميل كافة الفريمات (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="extracted_frames.zip",
                        mime="application/zip"
                    )
                    
                    # حذف الملف المؤقت
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                else:
                    st.error("فشل استخراج الصور. حاول اختيار مقطع آخر.")

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
