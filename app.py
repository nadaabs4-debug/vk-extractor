import streamlit as st
import yt_dlp
import cv2
import os
import zipfile
import io

st.set_page_config(page_title="VK HD Frame Extractor", layout="wide")

# تنسيق العنوان والواجهة
st.markdown("<h1 style='text-align: center;'>🎬 مستخرج فريمات VK بأعلى جودة</h1>", unsafe_allow_html=True)

vk_url = st.text_input("أدخل رابط فيديو VK:")

if vk_url:
    try:
        # 1. جلب معلومات الفيديو والمدة
        with st.spinner('جاري فحص جودة الفيديو المتوفرة...'):
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(vk_url, download=False)
                duration = int(info.get('duration', 0))
                title = info.get('title', 'video')

        st.info(f"📺 فيديو: {title} | المدة الكاملة: {duration} ثانية")

        # 2. تحديد النطاق الزمني
        st.subheader("حدد المقطع بدقة (سيتم استخراج كل الفريمات):")
        start_time, end_time = st.slider("اختر البداية والنهاية (بالثواني):", 
                                        0, duration, (0, min(3, duration)))
        
        if st.button("🚀 بدء استخراج الفريمات بجودة عالية"):
            # تحديد حد أقصى للثواني لضمان عدم توقف السيرفر (10 ثوانٍ كافية جداً)
            if end_time - start_time > 10:
                st.warning("⚠️ يرجى اختيار مقطع أقل من 10 ثوانٍ للحفاظ على جودة الصور وسرعة التحميل.")
            else:
                progress_bar = st.progress(0)
                status = st.empty()
                
                # 3. تحميل المقطع بأفضل جودة متوفرة (Best Quality)
                status.info(f"جاري تحميل المقطع بدقة عالية من {start_time} إلى {end_time}...")
                
                temp_filename = "high_res_clip.mp4"
                ydl_clip_opts = {
                    'format': 'bestvideo+bestaudio/best', # طلب أفضل جودة فيديو متوفرة
                    'outtmpl': temp_filename,
                    'download_sections': [{'start_time': start_time, 'end_time': end_time}],
                    'force_keyframes_at_cuts': True,
                    'quiet': True
                }
                
                with yt_dlp.YoutubeDL(ydl_clip_opts) as ydl:
                    ydl.download([vk_url])
                
                # 4. معالجة الفيديو واستخراج الفريمات
                status.info("جاري معالجة الفريمات الأصلية...")
                cap = cv2.VideoCapture(temp_filename)
                frames_buffer = []
                
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    
                    # حفظ الصورة بجودتها الأصلية (بدون تصغير) وبضغط قليل جداً
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    frames_buffer.append(buffer)
                
                cap.release()
                
                # 5. التعبئة في ملف ZIP وعرض النتائج
                if frames_buffer:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                        for idx, frame_data in enumerate(frames_buffer):
                            zip_file.writestr(f"frame_highres_{idx:03d}.jpg", frame_data.tobytes())
                    
                    status.success(f"✅ تم استخراج {len(frames_buffer)} فريم بجودة عالية!")
                    
                    # زر التحميل
                    st.download_button(
                        label="📥 تحميل كافة الفريمات الأصلية (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name=f"{title}_frames.zip",
                        mime="application/zip"
                    )
                    
                    # عرض عينة مكبرة للمعاينة
                    st.write("معاينة لأول فريم مستخرج:")
                    st.image(frames_buffer[0].tobytes(), use_column_width=True)
                    
                    # تنظيف الملفات المؤقتة
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
                else:
                    st.error("لم يتم العثور على فريمات. تأكد من أن المقطع المختار يحتوي على محتوى.")

    except Exception as e:
        st.error(f"حدث خطأ: {e}")
