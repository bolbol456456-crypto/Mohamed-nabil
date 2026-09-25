import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'captain_mohamed_1993_secret_key'

# إعداد قاعدة البيانات وتخزين الملفات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# جدول حفظ مرفقات العملاء في قاعدة البيانات
class ClientUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200), nullable=True)
    video_path = db.Column(db.String(200), nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# قاعدة بيانات تجريبية للإحصائيات والاشتراكات
clients_db = [
    {"id": 1, "name": "أحمد محمود", "email": "ahmed@example.com", "goal": "تضخيم عضلات", "status": "نشط", "progress": "+4.5 كجم", "instapay_ref": "IP-982341", "paid": True},
    {"id": 2, "name": "محمود حسن", "email": "mahmoud@example.com", "goal": "تنشيط وخسارة دهون", "status": "نشط", "progress": "-6 كجم", "instapay_ref": "IP-982342", "paid": True}
]

# --- القوالب (Templates) ---

INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كابتن محمد نبيل | منصة التدريب الذكية</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #f59e0b; --primary-dark: #d97706; --bg-dark: #0a0a0a; --bg-card: #171717; --text-main: #f3f4f6; --text-muted: #9ca3af; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); line-height: 1.6; }
        header { display: flex; justify-content: space-between; align-items: center; padding: 20px 8%; background: rgba(10,10,10,0.95); position: fixed; width: 100%; top: 0; z-index: 1000; border-bottom: 1px solid #262626; }
        .logo { font-size: 24px; font-weight: 900; color: var(--primary); display: flex; align-items: center; gap: 10px; }
        nav a { color: var(--text-main); text-decoration: none; margin-left: 25px; font-weight: 600; transition: 0.3s; }
        nav a:hover { color: var(--primary); }
        .btn { background: var(--primary); color: #000; padding: 10px 25px; border-radius: 8px; font-weight: 700; text-decoration: none; transition: 0.3s; display: inline-block; }
        .btn:hover { background: var(--primary-dark); transform: translateY(-2px); }
        .hero { height: 100vh; background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.85)), center/cover; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 20px; }
        .hero h1 { font-size: 52px; font-weight: 900; margin-bottom: 20px; color: #fff; }
        .hero h1 span { color: var(--primary); }
        .hero p { font-size: 20px; color: var(--text-muted); margin-bottom: 30px; }
        .features { padding: 100px 8%; background: #121212; }
        .section-title { text-align: center; font-size: 38px; font-weight: 900; margin-bottom: 60px; color: #fff; }
        .section-title span { color: var(--primary); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }
        .card { background: var(--bg-card); padding: 35px; border-radius: 16px; border: 1px solid #262626; transition: 0.3s; }
        .card:hover { transform: translateY(-8px); border-color: var(--primary); }
        .card i { font-size: 40px; color: var(--primary); margin-bottom: 20px; }
        .card h3 { font-size: 22px; margin-bottom: 15px; color: #fff; }
        .card p { color: var(--text-muted); font-size: 15px; }
        .pricing { padding: 100px 8%; text-align: center; }
        .price-box { background: var(--bg-card); border: 2px solid var(--primary); border-radius: 20px; padding: 50px; max-width: 500px; margin: 0 auto; }
        .price-box h3 { font-size: 30px; margin-bottom: 15px; }
        .price { font-size: 48px; font-weight: 900; color: var(--primary); margin-bottom: 25px; }
        .instapay-info { background: #1f1f1f; padding: 20px; border-radius: 12px; margin: 20px 0; border: 1px dashed var(--primary); }
        .instapay-info strong { color: var(--primary); font-size: 20px; display: block; margin-top: 5px; }
        footer { text-align: center; padding: 40px; background: #050505; color: var(--text-muted); border-top: 1px solid #262626; }
    </style>
</head>
<body>
    <header>
        <div class="logo"><i class="fa-solid fa-dumbbell"></i> كابتن محمد نبيل</div>
        <nav>
            <a href="#features">مميزات المنصة</a>
            <a href="#pricing">الاشتراك</a>
            <a href="/admin/login" style="color: var(--primary);"><i class="fa-solid fa-lock"></i> لوحة التحكم</a>
        </nav>
        <a href="#pricing" class="btn">اشترك الآن</a>
    </header>

    <section class="hero">
        <div>
            <h1>منصة <span>كابتن محمد نبيل</span> للتدريب بالذكاء الاصطناعي</h1>
            <p>تحليل قوام متقدم، تصحيح التمارين بالفيديو والصوت، ومتابعة فورية 24/7.</p>
            <a href="#pricing" class="btn" style="padding: 15px 40px; font-size: 18px;">ابدأ الآن</a>
        </div>
    </section>

    <section class="features" id="features">
        <h2 class="section-title">أدوات الذكاء الاصطناعي في المنصة</h2>
        <div class="grid">
            <div class="card"><i class="fa-solid fa-child-reaching"></i><h3>تحديد انحراف القوام</h3><p>فحص صور العميل واكتشاف ميل الكتفين أو العمود الفقري لتحديد التمرين العلاجي.</p></div>
            <div class="card"><i class="fa-solid fa-video"></i><h3>تصحيح التمرين بالفيديو</h3><p>تحليل زوايا الأداء وتوفير تعليق صوتي وتجميد فوري للقطات الخطأ.</p></div>
            <div class="card"><i class="fa-solid fa-comments"></i><h3>شات ومساعد ذكي 24/7</h3><p>ردود ذكية على الأسئلة الغذائية مع مراجعة وإشراف مباشر من الكابتن.</p></div>
        </div>
    </section>

    <section class="pricing" id="pricing">
        <h2 class="section-title">الاشتراك والدفع</h2>
        <div class="price-box">
            <h3>الباقة الاحترافية الشاملة</h3>
            <div class="price">1500 ج.م / شهرياً</div>
            <p>تحليل قوام، برنامج غذائي، وتدريب ذكي شخصي.</p>
            <div class="instapay-info">
                <span>التحويل عبر InstaPay:</span>
                <strong>01221078181</strong>
            </div>
            <a href="/client/dashboard" class="btn" style="display: block; margin-top: 20px;">دخول منصة العميل</a>
        </div>
    </section>

    <footer><p>جميع الحقوق محفوظة © 2026 - كابتن محمد نبيل.</p></footer>
</body>
</html>
'''

ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>تسجيل الدخول | لوحة التحكم</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Cairo', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login-card { background: #171717; padding: 40px; border-radius: 16px; border: 1px solid #262626; width: 100%; max-width: 400px; text-align: center; }
        h2 { color: #f59e0b; margin-bottom: 25px; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; background: #0a0a0a; border: 1px solid #333; color: #fff; border-radius: 8px; text-align: center; font-size: 20px; letter-spacing: 5px; }
        button { width: 100%; padding: 15px; background: #f59e0b; color: #000; border: none; font-weight: bold; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .error { color: #ef4444; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>لوحة التحكم</h2>
        <p style="color:#9ca3af; margin-bottom: 20px;">أدخل الرقم السري (1993)</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="password" name="pin" placeholder="••••" maxlength="4" required autofocus>
            <button type="submit">دخول</button>
        </form>
        <a href="/" style="display:block; margin-top:20px; color:#9ca3af; text-decoration:none;">العودة للموقع</a>
    </div>
</body>
</html>
'''

ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>لوحة التحكم | كابتن محمد نبيل</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Cairo', sans-serif; display: flex; }
        .sidebar { width: 280px; background: #121212; height: 100vh; padding: 30px; border-left: 1px solid #262626; position: fixed; }
        .sidebar h2 { color: #f59e0b; font-size: 20px; margin-bottom: 40px; }
        .sidebar a { display: block; color: #9ca3af; text-decoration: none; padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; font-weight: 600; }
        .sidebar a:hover, .sidebar a.active { background: #f59e0b; color: #000; }
        .main-content { margin-right: 280px; padding: 40px; width: calc(100% - 280px); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .stat-card { background: #171717; padding: 25px; border-radius: 12px; border: 1px solid #262626; }
        .stat-card h4 { color: #9ca3af; font-size: 14px; margin-bottom: 10px; }
        .stat-card .value { font-size: 32px; font-weight: 900; color: #f59e0b; }
        table { width: 100%; border-collapse: collapse; background: #171717; border-radius: 12px; overflow: hidden; margin-top: 20px; }
        th, td { padding: 15px 20px; text-align: right; border-bottom: 1px solid #262626; }
        th { background: #1f1f1f; color: #f59e0b; }
        .media-link { color: #38bdf8; text-decoration: none; margin-left: 10px; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2><i class="fa-solid fa-crown"></i> كابتن محمد نبيل</h2>
        <a href="#" class="active"><i class="fa-solid fa-chart-line"></i> لوحة الأداء</a>
        <a href="/"><i class="fa-solid fa-globe"></i> زيارة الموقع</a>
    </div>
    <div class="main-content">
        <h1 style="margin-bottom: 30px;">لوحة تحكم الكابتن (PIN: 1993)</h1>
        <div class="stats-grid">
            <div class="stat-card"><h4>العملاء النشطين</h4><div class="value">{{ active_count }}</div></div>
            <div class="stat-card"><h4>إجمالي الأرباح</h4><div class="value">{{ revenue }} ج.م</div></div>
            <div class="stat-card"><h4>حساب InstaPay</h4><div class="value" style="font-size: 20px;">01221078181</div></div>
        </div>
        
        <h2>سجل مرفقات العملاء (قاعدة البيانات)</h2>
        <table>
            <thead><tr><th>معرف الطلب</th><th>اسم العميل</th><th>صورة القوام</th><th>فيديو التمرين</th><th>تاريخ الرفع</th></tr></thead>
            <tbody>
                {% for upload in uploads %}
                <tr>
                    <td>{{ upload.id }}</td>
                    <td>{{ upload.client_name }}</td>
                    <td>{% if upload.image_path %}<a class="media-link" href="{{ url_for('download_file', filename=upload.image_path) }}" target="_blank">عرض الصورة</a>{% else %}لا توجد{% endif %}</td>
                    <td>{% if upload.video_path %}<a class="media-link" href="{{ url_for('download_file', filename=upload.video_path) }}" target="_blank">عرض الفيديو</a>{% else %}لا يوجد{% endif %}</td>
                    <td>{{ upload.upload_date.strftime('%Y-%m-%d %H:%M') }}</td>
                </tr>
                {% else %}
                <tr><td colspan="5" style="text-align: center; color: #9ca3af;">لا توجد مرفقات مرفوعة حالياً.</td></tr>
                {% endfor %}
            </tbody>
        </table>

        <h2 style="margin-top: 40px;">سجل العملاء النشطين (التجريبي)</h2>
        <table>
            <thead><tr><th>الاسم</th><th>البريد</th><th>الهدف</th><th>التطور</th><th>الحالة</th></tr></thead>
            <tbody>
                {% for client in clients %}
                <tr><td>{{ client.name }}</td><td>{{ client.email }}</td><td>{{ client.goal }}</td><td style="color: #10b981;">{{ client.progress }}</td><td>{{ client.status }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
'''

CLIENT_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>لوحة العميل الذكية | كابتن محمد نبيل</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Cairo', sans-serif; padding: 40px 8%; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #262626; padding-bottom: 20px; margin-bottom: 40px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
        .card { background: #171717; padding: 30px; border-radius: 16px; border: 1px solid #262626; }
        .card h3 { color: #f59e0b; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        .btn { background: #f59e0b; color: #000; padding: 10px 20px; border-radius: 8px; font-weight: bold; border: none; cursor: pointer; margin-top: 15px; width: 100%; }
        textarea, input { width: 100%; padding: 12px; margin-top: 10px; background: #0a0a0a; border: 1px solid #333; color: #fff; border-radius: 6px; }
        label { color: #9ca3af; font-size: 14px; display: block; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>منصة العميل الذكية | كابتن محمد نبيل</h1>
        <a href="/" style="color: #f59e0b; text-decoration: none;"><i class="fa-solid fa-arrow-right"></i> الرئيسية</a>
    </div>
    
    <form action="/client/upload" method="POST" enctype="multipart/form-data" class="grid">
        <!-- قسم تحليل القوام ورفع الملفات للقاعدة -->
        <div class="card">
            <h3><i class="fa-solid fa-child-reaching"></i> رفع صور القوام وفيديوهات التمارين</h3>
            <label>اسم العميل الثنائي:</label>
            <input type="text" name="client_name" placeholder="اكتب اسمك هنا..." required>
            
            <label>صورة القوام (صور الأمام/الخلف):</label>
            <input type="file" name="posture_image" accept="image/*">
            
            <label>فيديو التمرين (Form Check):</label>
            <input type="file" name="workout_video" accept="video/*">
            
            <button type="submit" class="btn">إرسال للكابتن والتحليل (AI)</button>
        </div>

        <div class="card">
            <h3><i class="fa-solid fa-utensils"></i> البيانات الصحية ونوت الأكل</h3>
            <p style="color: #9ca3af; font-size: 14px;">سجل الإصابات، الأمراض، وحساسية الأكل لتصميم نظامك.</p>
            <textarea rows="5" placeholder="اكتب ملاحظات الأكل، الإصابات، أو الحساسية هنا..."></textarea>
            <button type="button" class="btn" onclick="alert('تم حفظ البيانات بنجاح!')">حفظ وتحديث البيانات</button>
        </div>
        
        <div class="card">
            <h3><i class="fa-solid fa-robot"></i> حالة الذكاء الاصطناعي</h3>
            <p style="color: #9ca3af; font-size: 14px;">مساعدك الآلي جاهز للرد على استفساراتك التدريبية والغذائية طوال اليوم.</p>
            <div style="background: #121212; padding: 15px; border-radius: 8px; margin-top: 15px; border: 1px dashed #333;">
                <span style="color: #10b981;"><i class="fa-solid fa-circle" style="font-size: 10px;"></i> النظام يعمل بكفاءة 24/7</span>
            </div>
            <a href="/" class="btn" style="text-align: center; text-decoration: none; display: block; margin-top: 38px; background: #333; color: #fff;">العودة للرئيسية</a>
        </div>
    </form>
</body>
</html>
'''

# --- المسارات (Routes) ---

@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/client/dashboard')
def client_dashboard():
    return render_template_string(CLIENT_DASHBOARD_TEMPLATE)

# مسار استقبال مرفقات العميل وحفظها في قاعدة البيانات والملفات[cite: 1]
@app.route('/client/upload', methods=['POST'])
def client_upload():
    client_name = request.form.get('client_name')
    
    # استقبال صورة القوام
    image_file = request.files.get('posture_image')
    image_filename = None
    if image_file and allowed_file(image_file.filename):
        image_filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
    # استقبال فيديو التمرين
    video_file = request.files.get('workout_video')
    video_filename = None
    if video_file and allowed_file(video_file.filename):
        video_filename = secure_filename(video_file.filename)
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_filename))
        
    # حفظ البيانات في قاعدة البيانات[cite: 1]
    new_upload = ClientUpload(client_name=client_name, image_path=image_filename, video_path=video_filename)
    db.session.add(new_upload)
    db.session.commit()
    
    return redirect(url_for('client_dashboard'))

# مسار استعراض الملفات المرفوعة للأدمن
@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('pin') == '1993':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string(ADMIN_LOGIN_TEMPLATE, error='الرقم السري غير صحيح')
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # استدعاء جميع الملفات المرفوعة للعملاء من قاعدة البيانات[cite: 1]
    uploads = ClientUpload.query.all()
    return render_template_string(
        ADMIN_DASHBOARD_TEMPLATE, 
        clients=clients_db, 
        uploads=uploads, 
        active_count=len(clients_db), 
        revenue=len(clients_db)*1500
    )

# إنشاء الجداول تلقائياً وتشغيل التطبيق[cite: 1]
if __name__ == '__main__':
    with app.app_context():
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        db.create_all()
    app.run(debug=True, port=5000)
