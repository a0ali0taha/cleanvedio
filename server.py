from flask import Flask, render_template, request, flash
import os
import requests
from main import *

app = Flask(__name__, static_folder='final')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/final')
def show_final_videos():
    final_path = 'final'
    if not os.path.exists(final_path):
        return "Final directory does not exist"
        
    videos = []
    for file in os.listdir(final_path):
        if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
            videos.append({
                'name': file,
                'path': os.path.join(final_path, file)
            })
            
    return render_template('videos.html', videos=videos)

@app.route('/process', methods=['POST'])
def process():
    source = request.form['source']
    output_folder = request.form.get('output_folder', '').strip()
    is_playlist = 'playlist' in request.form
    upload_to_telegram = 'upload_to_telegram' in request.form

    # التحقق من وجود مجلد الإخراج
    if not output_folder:
        return """
            <div style='direction: rtl; text-align: right; color: red;'>
                يجب تحديد مجلد الإخراج
            </div>
        """

    # تنظيف وتوحيد مسار المجلد
    output_folder = os.path.abspath(output_folder)

    # إنشاء المجلد إذا لم يكن موجوداً
    try:
        os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        return f"""
            <div style='direction: rtl; text-align: right; color: red;'>
                خطأ في إنشاء مجلد الإخراج:<br>
                {str(e)}
            </div>
        """

    if source == 'youtube':
        youtube_url = request.form.get('youtube_url', '').strip()
        if not youtube_url:
            return """
                <div style='direction: rtl; text-align: right; color: red;'>
                    يرجى إدخال رابط يوتيوب صحيح
                </div>
            """
        
        try:
            # التأكد من وجود المجلدات المطلوبة
            os.makedirs('input', exist_ok=True)
            os.makedirs('final', exist_ok=True)
            
            # محاولة تنزيل الفيديو
            start(youtube_url, is_playlist, output_folder, upload_to_telegram)
            return f"""
                <div style='direction: rtl; text-align: right;'>
                    تمت معالجة الطلب بنجاح:<br>
                    - رابط اليوتيوب: {youtube_url}<br>
                    - مجلد الحفظ: {output_folder}<br>
                    - تنزيل كقائمة تشغيل: {'نعم' if is_playlist else 'لا'}<br>
                    - رفع إلى تيليجرام: {'نعم' if upload_to_telegram else 'لا'}
                </div>
            """
        except Exception as e:
            error_msg = str(e)
            if "Requested format is not available" in error_msg:
                return """
                    <div style='direction: rtl; text-align: right; color: red;'>
                        عذراً، الفيديو غير متاح للتنزيل بالصيغة المطلوبة.<br>
                        الأسباب المحتملة:<br>
                        - الفيديو محمي من التنزيل<br>
                        - الفيديو تم حذفه أو جعله خاص<br>
                        - رابط الفيديو غير صحيح<br>
                        - قد تحتاج إلى تحديث أداة youtube-dl<br>
                        يرجى التأكد من الرابط والمحاولة مرة أخرى.
                    </div>
                """
            elif "Video unavailable" in error_msg:
                return """
                    <div style='direction: rtl; text-align: right; color: red;'>
                        عذراً، الفيديو غير متاح.<br>
                        قد يكون الفيديو:<br>
                        - تم حذفه<br>
                        - خاص<br>
                        - محظور في منطقتك<br>
                    </div>
                """
            return f"""
                <div style='direction: rtl; text-align: right; color: red;'>
                    حدث خطأ أثناء معالجة رابط اليوتيوب:<br>
                    {error_msg}
                </div>
            """
    else:
        if 'video_file' not in request.files:
            return "لم يتم اختيار ملف فيديو"
            
        video_file = request.files['video_file']
        if not video_file or video_file.filename == '':
            return "لم يتم اختيار ملف فيديو"

        try:
            # التأكد من وجود مجلد المدخلات
            input_dir = 'input'
            os.makedirs(input_dir, exist_ok=True)
            
            # حفظ الملف المرفوع
            file_path = os.path.join(input_dir, video_file.filename)
            video_file.save(file_path)
            
            # بدء المعالجة في خيط منفصل
            threading.Thread(target=start_file, args=(file_path, upload_to_telegram)).start()
            return f"جاري معالجة الملف: {video_file.filename}<br>المجلد: {output_folder}<br>رفع: {upload_to_telegram}"
        except Exception as e:
            return f"حدث خطأ أثناء معالجة الملف: {str(e)}"

def start_file(video_path, send_to_telegram):
    try:
        # التأكد من أن الملف موجود
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"الملف غير موجود: {video_path}")
            
        # التأكد من أن الملف هو فيديو
        valid_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.webm')
        if not video_path.lower().endswith(valid_extensions):
            raise ValueError(f"صيغة الملف غير مدعومة. الصيغ المدعومة هي: {', '.join(valid_extensions)}")
            
        # إنشاء مجلد المعالجة
        processing_input_folder = video_path.rsplit('.', 1)[0]  # حذف الامتداد بشكل آمن
        os.makedirs(processing_input_folder, exist_ok=True)
        
        # إنشاء كائن الفيديو ومعالجته
        video = Video(
            processing_input_folder=processing_input_folder,
            input_video_path=video_path,
            send_to_telegram=send_to_telegram
        )
        handle(video)
        
    except Exception as e:
        print(f"خطأ في معالجة الفيديو: {str(e)}")
        # يمكن إضافة تنظيف الملفات المؤقتة هنا إذا لزم الأمر
        raise

if __name__ == '__main__':

    import socket
    def get_local_ip():
        try:
            # Create a socket to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google's DNS
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"  # Fallback to localhost if unable to get IP
            
    app.run(host=get_local_ip(), port=80, debug=True)
