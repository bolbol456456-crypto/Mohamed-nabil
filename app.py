import os
from flask import Flask, render_template_string, request, redirect, url_for, session, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'captain_mohamed_1993_secure_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# جدول العملاء والاشتراكات والمرفقات والبيانات الكاملة
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    goal = db.Column(db.String(100), nullable=True)
    injuries = db.Column(db.Text, nullable=True)
    disliked_foods = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    
    receipt_path = db.Column(db.String(200), nullable=True)
    posture_image = db.Column(db.String(200), nullable=True)
    workout_video = db.Column(db.String(200), nullable=True)
    
    is_approved = db.Column(db.Boolean, default=False)
    access_code = db.Column(db.String(20), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- قوالب HTML والواجهات ---

INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>كابتن محمد نبيل | منصة التدريب الاحترافية</title>
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
        .price-box { background: var(--bg-card); border: 2px solid var(--primary); border-radius: 20px; padding: 50px; max-width: 550px; margin: 0 auto; text-align: right; }
        .price-box h3 { font-size: 28px; margin-bottom: 15px; text-align: center; }
        .price { font-size: 42px; font-weight: 900; color: var(--primary); margin-bottom: 25px; text-align: center; }
        .instapay-info { background: #1f1f1f; padding: 20px; border-radius: 12px; margin: 20px 0; border: 1px dashed var(--primary); text-align: center; }
        .instapay-info strong { color: var(--primary); font-size: 22px; display: block; margin-top: 5px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0 15px 0; background: #0a0a0a; border: 1px solid #333; color: #fff; border-radius: 8px; font-family: 'Cairo'; }
        label { color: var(--text-muted); font-size: 14px; }
        footer { text-align: center; padding: 40px; background: #050505; color: var(--text-muted); border-top: 1px solid #262626; }
    </style>
</head>
<body>
    <header>
        <div class="logo"><i class="fa-solid fa-dumbbell"></i> كابتن محمد نبيل</div>
        <nav>
            <a href="#features">مميزات البرامج</a>
            <a href="#pricing">الاشتراك والدفع</a>
            <a href="/client/login" class="btn" style="padding: 8px 20px; color: #000;">دخول المشتركين</a>
        </nav>
    </header>

    <section class="hero">
        <div>
            <h1>اصنع نسخت الأفضل مع <span>كابتن محمد نبيل</span></h1>
            <p>متابعة احترافية شخصية، برامج تدريب وتغذية مخصصة، وتقييم شامل للقوام لتصل لهدفك بقوة.</p>
            <a href="#pricing" class="btn" style="padding: 15px 40px; font-size: 18px;">ابدأ رحلتك الآن</a>
        </div>
    </section>

    <section class="features" id="features">
        <h2 class="section-title">لماذا تختار <span>منصتنا الاحترافية؟</span></h2>
        <div class="grid">
            <div class="card"><i class="fa-solid fa-bullseye"></i><h3>تحديد الأهداف بدقة</h3><p>سواء كان هدفك خسارة الدهون أو بناء الكتلة العضلية الصافية، نصمم لك النظام المناسب.</p></div>
            <div class="card"><i class="fa-solid fa-child-reaching"></i><h3>تقييم انحراف القوام</h3><p>معالجة القوام وتصحيح وضعيات الجسم عبر إرشادات تصوير واضحة ومراجعة مباشرة.</p></div>
            <div class="card"><i class="fa-solid fa-headset"></i><h3>متابعة مستمرة وشات خاص</h3><p>تواصل مباشر مع الكابتن، تعديل التمارين وفيديوهات تصحيح الأداء أول بأول.</p></div>
        </div>
    </section>

    <section class="pricing" id="pricing">
        <h2 class="section-title">الاشتراك ورفع إيصال الدفع</h2>
        <div class="price-box">
            <h3>الباقة التدريبية الشاملة</h3>
            <div class="price">1500 ج.م / شهرياً</div>
            <p style="text-align: center; color: var(--text-muted); margin-bottom: 20px;">يشمل التغذية، جدول التمارين، وتقييم القوام.</p>
            
            <div class="instapay-info">
                <span>التحويل الفوري عبر InstaPay على رقم:</span>
                <strong>01221078181</strong>
            </div>

            <form action="/register" method="POST" enctype="multipart/form-data">
                <label>الاسم الكامل:</label>
                <input type="text" name="name" required placeholder="اكتب اسمك الثلاثي">
                
                <label>رقم الواتساب (لاستلام الكود السري عليه):</label>
                <input type="text" name="phone" required placeholder="012xxxxxxxx">
                
                <label>صورة إيصال التحويل (إنستا باي):</label>
                <input type="file" name="receipt" accept="image/*" required>
                
                <button type="submit" class="btn" style="width: 100%; margin-top: 15px; padding: 14px; font-size: 16px;">إرسال طلب الاشتراكوإيصال الدفع</button>
            </form>
        </div>
    </section>

    <footer><p>جميع الحقوق محفوظة © 2026 - كابتن محمد نبيل.</p></footer>
</body>
</html>
'''

# صفحة دخول العميل بالكود السري
CLIENT_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>تسجيل دخول المشتركين | كابتن محمد نبيل</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Cairo', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login-card { background: #171717; padding: 40px; border-radius: 16px; border: 1px solid #262626; width: 100%; max-width: 400px; text-align: center; }
        h2 { color: #f59e0b; margin-bottom: 25px; }
        input { width: 100%; padding: 15px; margin-bottom: 20px; background: #0a0a0a; border: 1px solid #333; color: #fff; border-radius: 8px; text-align: center; font-size: 18px; }
        button { width: 100%; padding: 15px; background: #f59e0b; color: #000; border: none; font-weight: bold; border-radius: 8px; font-size: 16px; cursor: pointer; }
        .error { color: #ef4444; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>منصة المشتركين</h2>
        <p style="color:#9ca3af; margin-bottom: 20px;">أدخل الكود السري الخاص بك المرسل على الواتساب</p>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <input type="text" name="access_code" placeholder="أدخل كود الدخول" required autofocus>
            <button type="submit">دخول لوحتي الشخصية</button>
        </form>
        <a href="/" style="display:block; margin-top:20px; color:#9ca3af; text-decoration:none;">العودة للرئيسية</a>
    </div>
</body>
</html>
'''

# لوحة تحكم العميل الاحترافية والشاملة
CLIENT_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>لوحتي الشخصية | كابتن محمد نبيل</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #f59e0b; --bg-dark: #0a0a0a; --bg-card: #171717; --text-main: #f3f4f6; --text-muted: #9ca3af; }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); padding: 30px 5%; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #262626; padding-bottom: 20px; margin-bottom: 30px; }
        .welcome-msg { background: linear-gradient(135deg, #1f1f1f, #121212); padding: 20px; border-radius: 12px; border-left: 5px solid var(--primary); margin-bottom: 30px; font-size: 18px; font-weight: bold; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; }
        .card { background: var(--bg-card); padding: 25px; border-radius: 16px; border: 1px solid #262626; }
        .card h3 { color: var(--primary); margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-size: 20px; }
        input, select, textarea { width: 100%; padding: 10px; margin-top: 8px; margin-bottom: 12px; background: var(--bg-dark); border: 1px solid #333; color: #fff; border-radius: 8px; }
        label { color: var(--text-muted); font-size: 13px; display: block; }
        .btn { background: var(--primary); color: #000; padding: 12px; border-radius: 8px; font-weight: bold; border: none; cursor: pointer; width: 100%; margin-top: 10px; }
        .btn:hover { background: #d97706; }
        .guide-box { background: #121212; padding: 15px; border-radius: 10px; border: 1px dashed #333; margin-bottom: 15px; font-size: 13px; color: var(--text-muted); }
        .sample-img-container { display: flex; gap: 10px; margin-top: 10px; }
        .sample-img-container img { width: 48%; height: 120px; object-fit: cover; border-radius: 8px; border: 1px solid var(--primary); }
    </style>
</head>
<body>
    <div class="header">
        <h1>مرحباً بك، <span style="color: var(--primary);">{{ client.name }}</span></h1>
        <a href="/" style="color: var(--primary); text-decoration: none;"><i class="fa-solid fa-arrow-right"></i> تسجيل الخروج</a>
    </div>

    <div class="welcome-msg">
        🔥 "البطل الحقيقي ليس من لا يسقط أبداً، بل من ينهض في كل مرة أقوى من ذي قبل! استمر يا بطل، أنا معك خطوة بخطوة لنحقق هدفك." - كابتن محمد نبيل
    </div>

    <form method="POST" enctype="multipart/form-data" class="grid">
        <!-- البيانات الشخصية والتارجت -->
        <div class="card">
            <h3><i class="fa-solid id-card"></i> بيانات الجسم والأهداف</h3>
            <label>السن (بالسنوات):</label>
            <input type="number" name="age" value="{{ client.age or '' }}" placeholder="مثال: 25">
            
            <label>الوزن الحالي (كجم):</label>
            <input type="number" step="0.5" name="weight" value="{{ client.weight or '' }}" placeholder="مثال: 75">
            
            <label>الطول (سم):</label>
            <input type="number" name="height" value="{{ client.height or '' }}" placeholder="مثال: 178">
            
            <label>الهدف الأساسي:</label>
            <select name="goal">
                <option value="خسارة دهون وتنشيط" {% if client.goal == 'خسارة دهون وتنشيط' %}selected{% endif %}>خسارة دهون وزيادة التنشيط</option>
                <option value="زيادة الكتلة العضلية (تضخيم)" {% if client.goal == 'زيادة الكتلة العضلية (تضخيم)' %}selected{% endif %}>زيادة الكتلة العضلية (تضخيم)</option>
                <option value="إعادة تأهيل وقوام" {% if client.goal == 'إعادة تأهيل وقوام' %}selected{% endif %}>تحسين القوام وعلاج انحرافات العمود الفقري</option>
            </select>
            <button type="submit" class="btn">حفظ وتحديث البيانات</button>
        </div>

        <!-- الإصابات والحساسية والأكل -->
        <div class="card">
            <h3><i class="fa-solid fa-notes-medical"></i> الإصابات والتغذية</h3>
            <label>هل تعاني من أي إصابات قديمة أو آلام مفاصل؟</label>
            <textarea name="injuries" rows="2" placeholder="اكتب أماكن الإصابات إن وجدت...">{{ client.injuries or '' }}</textarea>
            
            <label>أكلات لا تحبها أو تسبب لك حساسية:</label>
            <textarea name="allergies" rows="2" placeholder="مثال: حساسية لكتوز، لا أحب السمك...">{{ client.allergies or '' }}</textarea>
            
            <label>ملاحظات إضافية للكابتن:</label>
            <textarea name="disliked_foods" rows="2" placeholder="أي تفاصيل تخص جدولك اليومي...">{{ client.disliked_foods or '' }}</textarea>
            <button type="submit" class="btn">تحديث الملف الصحي</button>
        </div>

        <!-- تقييم انحراف القوام وكيفية التصوير -->
        <div class="card">
            <h3><i class="fa-solid fa-child-reaching"></i> تقييم القوام (صور الوضعيات)</h3>
            <div class="guide-box">
                <b>تعليمات التصوير الصحيح:</b>
                <br>1. قف بشكل مستقيم ومطابق للصور الاسترشادية أدناه.
                <br>2. التقط صورتين (صورة من الأمام وصورة من الخلف) بملابس رياضية واضحة لتحديد الانحرافات.
            </div>
            
            <div class="sample-img-container">
                <div>
                    <span style="font-size:11px; color:#f59e0b;">وضعيات الأمام والجانب</span>
                    <img src="{{ url_for('static', filename='uploads/IMG_0197_b2c25a.jpeg') }}" alt="وضعيف تصوير استرشادية">
                </div>
                <div>
                    <span style="font-size:11px; color:#f59e0b;">وضعيات الظهر والخلف</span>
                    <img src="{{ url_for('static', filename='uploads/IMG_0196_b2c25a.jpeg') }}" alt="وضعيات تصوير الظهر">
                </div>
            </div>

            <label style="margin-top: 15px;">رفع صور القوام الجديدة:</label>
            <input type="file" name="posture_image" accept="image/*">
            {% if client.posture_image %}
            <span style="color: #10b981; font-size: 12px;"><i class="fa-solid fa-check"></i> تم رفع صورة القوام بنجاح</span>
            {% endif %}
            <button type="submit" class="btn">رفع وربط صور القوام</button>
        </div>

        <!-- رفع فيديو التمرين (Form Check) والشات -->
        <div class="card">
            <h3><i class="fa-solid fa-video"></i> تعديل الأداء والشات مع الكابتن</h3>
            <label>رفع فيديو أداء التمرين (Form Check):</label>
            <input type="file" name="workout_video" accept="video/*">
            {% if client.workout_video %}
            <span style="color: #10b981; font-size: 12px;"><i class="fa-solid fa-check"></i> تم رفع الفيديو للتعديل</span>
            {% endif %}
            
            <label style="margin-top: 15px;">استفسارك المباشر للكابتن:</label>
            <textarea rows="2" placeholder="اكتب سؤالك وسيرد عليك الكابتن قريباً..."></textarea>
            
            <button type="submit" class="btn">إرسال الفيديو والرسالة</button>
        </div>
    </form>
</body>
</html>
'''

# لوحة تحكم الأدمن السرية (تتطلب PIN: 1993 بدون ظهور رابط لها بالواجهة الرئيسية)
ADMIN_LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>تسجيل دخول الأدمن السرية</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Cairo', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .box { background: #171717; padding: 40px; border-radius: 12px; border: 1px solid #333; text-align: center; width: 350px; }
        input { width: 100%; padding: 12px; margin: 15px 0; background: #000; border: 1px solid #444; color: #fff; text-align: center; font-size: 20px; letter-spacing: 5px; border-radius: 6px; }
        button { width: 100%; padding: 12px; background: #f59e0b; color: #000; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="box">
        <h3>لوحة تحكم الكابتن</h3>
        {% if error %}<p style="color:red; font-size:12px;">{{ error }}</p>{% endif %}
        <form method="POST">
            <input type="password" name="pin" placeholder="••••" maxlength="4" required autofocus>
            <button type="submit">دخول سري</button>
        </form>
    </div>
</body>
</html>
'''

ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><title>لوحة التحكم الرئيسية | كابتن محمد نبيل</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0a0a0a; color: #fff; font-family: 'Cairo', sans-serif; padding: 30px; }
        table { width: 100%; border-collapse: collapse; background: #171717; margin-top: 20px; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px 15px; text-align: right; border-bottom: 1px solid #262626; font-size: 14px; }
        th { background: #1f1f1f; color: #f59e0b; }
        .btn-action { background: #10b981; color: #fff; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 12px; display: inline-block; }
        .btn-app { background: #f59e0b; color: #000; padding: 5px 10px; border-radius: 4px; text-decoration: none; font-size: 12px; }
    </style>
</head>
<body>
    <h1>لوحة إدارة المشتركين والمدفوعات (إنستا باي)</h1>
    <p style="color: #9ca3af;">قم بمراجعة إيصالات التحويل، ثم تفعيل الكود السري للعميل ليتم إرساله له على الواتساب.</p>
    <table>
        <tr>
            <th>الاسم</th>
            <th>رقم الواتساب</th>
            <th>إيصال الدفع</th>
            <th>الحالة</th>
            <th>الكود السري</th>
            <th>الإجراء (التفعيل وتوليد الكود)</th>
        </tr>
        {% for c in clients %}
        <tr>
            <td>{{ c.name }}</td>
            <td>{{ c.phone }}</td>
            <td>{% if c.receipt_path %}<a href="{{ url_for('download_file', filename=c.receipt_path) }}" target="_blank" style="color:#38bdf8;">عرض الإيصال</a>{% else %}لا يوجد{% endif %}</td>
            <td>{% if c.is_approved %}<span style="color:#10b981;">مفعل ونشط</span>{% else %}<span style="color:#ef4444;">بانتظار المراجعة</span>{% endif %}</td>
            <td><strong>{{ c.access_code or 'لم يُولد بعد' }}</strong></td>
            <td>
                <form action="/admin/approve/{{ c.id }}" method="POST" style="display:inline;">
                    <button type="submit" class="btn-app">تفعيل وتوليد كود</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    <a href="/" style="display:block; margin-top:30px; color:#f59e0b; text-decoration:none;">العودة للموقع الرئيسي</a>
</body>
</html>
'''

# --- المسارات والتحكم (Routes) ---

@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    phone = request.form.get('phone')
    
    receipt_filename = None
    receipt_file = request.files.get('receipt')
    if receipt_file and allowed_file(receipt_file.filename):
        receipt_filename = secure_filename(receipt_file.filename)
        receipt_file.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_filename))
        
    new_client = Client(name=name, phone=phone, receipt_path=receipt_filename)
    db.session.add(new_client)
    db.session.commit()
    
    return "<h2 style='text-align:center; color:#f59e0b; font-family:Cairo; margin-top:100px;'>تم استلام طلبك وإيصال الدفع بنجاح!<br>سيقوم الكابتن محمد نبيل بمراجعة الإيصال وإرسال كود الدخول الخاص بك عبر الواتساب قريباً.<br><a href='/' style='color:#fff; font-size:16px;'>العودة للرئيسية</a></h2>"

@app.route('/client/login', methods=['GET', 'POST'])
def client_login():
    if request.method == 'POST':
        code = request.form.get('access_code')
        client = Client.query.filter_by(access_code=code, is_approved=True).first()
        if client:
            session['client_id'] = client.id
            return redirect(url_for('client_dashboard'))
        else:
            return render_template_string(CLIENT_LOGIN_TEMPLATE, error='الكود السري غير صحيح أو الحساب بانتظار التفعيل')
    return render_template_string(CLIENT_LOGIN_TEMPLATE)

@app.route('/client/dashboard', methods=['GET', 'POST'])
def client_dashboard():
    client_id = session.get('client_id')
    if not client_id:
        return redirect(url_for('client_login'))
        
    client = Client.query.get(client_id)
    
    if request.method == 'POST':
        client.age = request.form.get('age', type=int)
        client.weight = request.form.get('weight', type=float)
        client.height = request.form.get('height', type=float)
        client.goal = request.form.get('goal')
        client.injuries = request.form.get('injuries')
        client.allergies = request.form.get('allergies')
        client.disliked_foods = request.form.get('disliked_foods')
        
        # حفظ صورة القوام إن وجدت
        posture_file = request.files.get('posture_image')
        if posture_file and allowed_file(posture_file.filename):
            client.posture_image = secure_filename(posture_file.filename)
            posture_file.save(os.path.join(app.config['UPLOAD_FOLDER'], client.posture_image))
            
        # حفظ فيديو التمرين إن وجد
        video_file = request.files.get('workout_video')
        if video_file and allowed_file(video_file.filename):
            client.workout_video = secure_filename(video_file.filename)
            video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], client.workout_video))
            
        db.session.commit()
        return redirect(url_for('client_dashboard'))
        
    return render_template_string(CLIENT_DASHBOARD_TEMPLATE, client=client)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('pin') == '1993':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template_string(ADMIN_LOGIN_TEMPLATE, error='الرقم السري خاطئ')
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    clients = Client.query.all()
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, clients=clients)

@app.route('/admin/approve/<int:client_id>', methods=['POST'])
def admin_approve(client_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    client = Client.query.get(client_id)
    if client:
        client.is_approved = True
        # توليد كود سري خاص فريد للعميل
        import random
        client.access_code = f"MN-{client.id}-{random.randint(1000, 9999)}"
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    with app.app_context():
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        db.create_all()
    app.run(debug=True, port=5000)
