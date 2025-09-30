# تطبيق Flask للمستخدمين

تطبيق ويب مبني بـ Flask يتيح للمستخدمين التسجيل وتسجيل الدخول وإدارة الملفات الشخصية.

## الميزات

- ✅ تسجيل المستخدمين الجدد
- ✅ تسجيل الدخول
- ✅ إدارة الملف الشخصي
- ✅ تحديث صورة الملف الشخصي
- ✅ إعادة تعيين كلمة المرور عبر OTP
- ✅ نظام جلسات آمن
- ✅ قاعدة بيانات SQLite

## المتطلبات

- Python 3.7+
- pip

## التثبيت

1. انسخ المشروع:
```bash
git clone <repository-url>
cd flask
```

2. أنشئ بيئة افتراضية (اختياري):
```bash
python -m venv env
env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac
```

3. ثبت المكتبات المطلوبة:
```bash
pip install -r requirements.txt
```

## التشغيل

1. شغل التطبيق:
```bash
python app.py
```

2. افتح المتصفح على:
```
http://localhost:5000
```

## هيكل المشروع

```
flask/
├── app.py                 # الملف الرئيسي للتطبيق
├── requirements.txt       # المكتبات المطلوبة
├── users.db              # قاعدة البيانات
├── static/               # الملفات الثابتة
│   ├── style.css         # ملف CSS
│   └── profile_pics/     # صور الملفات الشخصية
└── templates/            # قوالب HTML
    ├── base.html         # القالب الأساسي
    ├── home.html         # الصفحة الرئيسية
    ├── login.html        # صفحة تسجيل الدخول
    ├── register.html     # صفحة التسجيل
    ├── profile.html      # صفحة الملف الشخصي
    └── edit_profile.html # صفحة تعديل الملف الشخصي
```

## إعدادات البريد الإلكتروني

لتشغيل ميزة إعادة تعيين كلمة المرور، قم بتحديث إعدادات البريد في `app.py`:

```python
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'
```

## قاعدة البيانات

يتم إنشاء قاعدة البيانات تلقائياً عند تشغيل التطبيق لأول مرة.

## الأمان

- كلمات المرور مشفرة بـ bcrypt
- حماية CSRF
- جلسات آمنة
- تحقق من صحة المدخلات

## المساهمة

نرحب بالمساهمات! يرجى إنشاء issue أو pull request.

## الترخيص

هذا المشروع مرخص تحت رخصة MIT.
