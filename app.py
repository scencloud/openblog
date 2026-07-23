#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用开源博客系统 - 单文件Flask应用
端口: 31258
"""

import os
import sys
import uuid
import time
import secrets
import hashlib
import functools
from datetime import datetime, timedelta
from io import BytesIO

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, abort, send_from_directory, jsonify, g
)
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
import bleach

# ============================================================
# 配置
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
QUILL_UPLOAD_DIR = os.path.join(UPLOAD_DIR, 'quill')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(QUILL_UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('BLOG_SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATA_DIR, "blog.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

db = SQLAlchemy(app)

# ============================================================
# 数据模型
# ============================================================

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    blog_name = db.Column(db.String(100), default='xxx的博客')
    subtitle = db.Column(db.String(50), default='记录生活，分享思考')
    logo = db.Column(db.String(200), default='')
    password_hash = db.Column(db.String(200), default='')
    about_text = db.Column(db.Text, default='')
    first_run = db.Column(db.Boolean, default=True)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.String(200), default='')
    content = db.Column(db.Text, default='')
    cover = db.Column(db.String(200), default='')
    is_pinned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================
# 工具函数
# ============================================================

def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f'{salt}${h.hex()}'

def verify_password(password, password_hash):
    if not password_hash or '$' not in password_hash:
        return False
    salt, h = password_hash.split('$', 1)
    check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return secrets.compare_digest(check.hex(), h)

def get_settings():
    s = Setting.query.first()
    if not s:
        default_pw_hash = hash_password(os.environ.get('BLOG_DEFAULT_PASSWORD', 'blogadmin666'))
        default_about = """<h2>ScenCloud</h2>
<p>官方网站：<a href="https://www.scencloud.com" target="_blank">www.scencloud.com</a></p>
<p>联系方式：<a href="mailto:contact@scencloud.com">contact@scencloud.com</a></p>

<h3>使用授权</h3>
<ul>
<li>个人非商用：✅ 允许</li>
<li>商业用途：❌ 禁止</li>
<li>再分发：❌ 禁止</li>
<li>修改后声称原创：❌ 禁止</li>
<li>用于竞赛/评比：❌ 禁止</li>
<li>转售/打包售卖：❌ 禁止</li>
</ul>

<h3>免责声明</h3>
<ol>
<li><strong>内容准确性：</strong>本站所有文章、教程、技术分享等内容均基于作者个人经验与理解，可能存在疏漏或过时信息。内容仅供参考和学习交流之用，不构成任何形式的专业建议（包括但不限于技术、法律、财务、医疗建议）。因参考本站内容而产生的任何直接或间接损失，本站及作者不承担任何责任。</li>
<li><strong>外部链接：</strong>本站包含的外部链接仅为方便用户获取更多信息，不代表对链接指向的第三方网站、产品或服务的认可、推荐或担保。访问外部链接的风险由用户自行承担。</li>
<li><strong>技术风险：</strong>本站提供的代码示例、开源项目、技术方案等仅供学习参考。在生产环境中使用前，请务必自行测试验证。因使用本站技术内容导致的系统故障、数据丢失、安全漏洞等问题，本站概不负责。</li>
<li><strong>软件与工具：</strong>本站推荐或介绍的第三方软件、工具、插件等，其稳定性、安全性、兼容性由相应开发商负责。本站不对第三方产品的质量、性能或安全性做任何保证。</li>
<li><strong>用户生成内容：</strong>本站的评论区、留言板等用户互动区域中，用户发布的言论不代表本站立场。用户需对自己发布的内容承担全部法律责任。</li>
<li><strong>知识产权：</strong>本站发布的原创内容版权归 ScenCloud 所有。未经授权，禁止以任何形式复制、转载、改编或用于商业目的。如需转载，请联系作者获取书面授权。</li>
<li><strong>隐私保护：</strong>本站尊重并保护用户隐私。我们不会主动收集、出售或向第三方共享用户的个人信息，法律法规要求的情况除外。</li>
<li><strong>服务可用性：</strong>本站不保证服务的持续可用性。因服务器维护、网络故障、不可抗力等原因导致的服务中断，本站不承担责任。</li>
<li><strong>内容变更：</strong>本站保留随时修改、更新或删除任何内容的权利，恕不另行通知。</li>
<li><strong>未成年人保护：</strong>本站内容面向具备完全民事行为能力的成年人。未成年人使用本站内容应在监护人指导下进行。</li>
<li><strong>法律适用：</strong>本站内容受中华人民共和国法律管辖。因本站内容产生的任何争议，应友好协商解决；协商不成的，提交有管辖权的人民法院处理。</li>
<li><strong>最终解释权：</strong>本声明的最终解释权归 ScenCloud 所有。如有疑问，请通过 contact@scencloud.com 联系我们。</li>
</ol>

<h3>更新记录</h3>
<p>本声明最后更新于 2025 年。ScenCloud 保留随时修改本声明的权利。</p>"""
        s = Setting(
            blog_name='xxx的博客',
            subtitle='记录生活，分享思考',
            logo='',
            password_hash=default_pw_hash,
            about_text=default_about,
            first_run=True
        )
        db.session.add(s)
        db.session.commit()
    return s

def clean_html(text):
    if not text:
        return ''
    allowed_tags = list(bleach.ALLOWED_TAGS) + [
        'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'pre', 'code', 'blockquote',
        'img', 'video', 'source', 'iframe', 'span', 'div',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'strong', 'em', 'u', 's', 'a', 'sup', 'sub'
    ]
    allowed_attrs = {
        '*': ['class', 'style', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'width', 'height'],
        'video': ['src', 'controls', 'width', 'height'],
        'source': ['src', 'type'],
        'iframe': ['src', 'width', 'height', 'frameborder', 'allowfullscreen'],
    }
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attrs, strip=True)

def sanitize_filename(filename):
    ext = os.path.splitext(filename)[1].lower()
    return f'{uuid.uuid4().hex}{ext}'

def allowed_file(filename, allowed_exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

def check_upload_security(file):
    IMAGE_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    VIDEO_EXTS = {'mp4', 'webm', 'ogg', 'mov'}
    filename = file.filename or ''
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    if ext in IMAGE_EXTS:
        try:
            img = Image.open(file)
            img.verify()
            file.seek(0)
        except Exception:
            return False, '图片文件无效'
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 5 * 1024 * 1024:
            return False, '图片不能超过5MB'
        return True, 'image'
    elif ext in VIDEO_EXTS:
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 50 * 1024 * 1024:
            return False, '视频不能超过50MB'
        return True, 'video'
    else:
        return False, '不支持的文件类型'

def crop_cover(file):
    img = Image.open(file)
    w, h = img.size
    target_ratio = 3 / 2
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    buf = BytesIO()
    fmt = img.format or 'JPEG'
    if fmt.upper() == 'JPG':
        fmt = 'JPEG'
    img.save(buf, format=fmt, quality=85)
    buf.seek(0)
    return buf

# ============================================================
# 登录保护 & 暴力破解
# ============================================================

def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

failed_attempts = {}

def is_locked(ip):
    info = failed_attempts.get(ip)
    if not info:
        return False
    if info.get('locked_until') and datetime.utcnow() < info['locked_until']:
        return True
    if info.get('locked_until') and datetime.utcnow() >= info['locked_until']:
        failed_attempts.pop(ip, None)
        return False
    return False

def record_failed(ip):
    info = failed_attempts.setdefault(ip, {'count': 0})
    info['count'] += 1
    if info['count'] >= 5:
        info['locked_until'] = datetime.utcnow() + timedelta(minutes=15)
        info['count'] = 0

def clear_failed(ip):
    failed_attempts.pop(ip, None)

# ============================================================
# 安全响应头 & 错误页面
# ============================================================

@app.after_request
def set_security_headers(response):
    # 静态文件（图片/视频）不加限制头，否则会被浏览器拦截
    req_path = request.path or ''
    if req_path.startswith('/static/') or req_path.startswith('/uploads/'):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404, message='页面未找到'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('error.html', code=500, message='服务器内部错误'), 500

# ============================================================
# 前台路由
# ============================================================

@app.route('/')
def home():
    s = get_settings()
    sort_mode = session.get('sort_mode', 'time')
    if sort_mode == 'random':
        articles = Article.query.order_by(Article.is_pinned.desc(), db.func.random()).all()
    else:
        articles = Article.query.order_by(Article.is_pinned.desc(), Article.created_at.desc()).all()
    return render_template('home.html', settings=s, articles=articles)

@app.route('/post/<int:article_id>')
def article_detail(article_id):
    s = get_settings()
    article = Article.query.get_or_404(article_id)
    return render_template('article.html', settings=s, article=article)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# ============================================================
# 后台 - 登录
# ============================================================

@app.route('/blogadmin', methods=['GET', 'POST'])
def admin_login():
    s = get_settings()
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    ip = request.remote_addr
    if is_locked(ip):
        flash('登录失败次数过多，请15分钟后再试', 'error')
        return render_template('admin/login.html', settings=s)
    if request.method == 'POST':
        password = request.form.get('password', '')
        if verify_password(password, s.password_hash):
            session['admin_logged_in'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=24)
            clear_failed(ip)
            if s.first_run:
                return redirect(url_for('admin_change_password'))
            return redirect(url_for('admin_dashboard'))
        else:
            record_failed(ip)
            flash('密码错误', 'error')
    return render_template('admin/login.html', settings=s)

@app.route('/blogadmin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('home'))

# ============================================================
# 后台 - 主页
# ============================================================

@app.route('/blogadmin/dashboard')
@login_required
def admin_dashboard():
    s = get_settings()
    return render_template('admin/dashboard.html', settings=s)

# ============================================================
# 后台 - 文章管理
# ============================================================

@app.route('/blogadmin/articles')
@login_required
def admin_articles():
    s = get_settings()
    sort_mode = session.get('sort_mode', 'time')
    if sort_mode == 'random':
        articles = Article.query.order_by(Article.is_pinned.desc(), db.func.random()).all()
    else:
        articles = Article.query.order_by(Article.is_pinned.desc(), Article.created_at.desc()).all()
    return render_template('admin/articles.html', settings=s, articles=articles, sort_mode=sort_mode)

@app.route('/blogadmin/sort', methods=['POST'])
@login_required
def admin_sort():
    current = session.get('sort_mode', 'time')
    session['sort_mode'] = 'random' if current == 'time' else 'time'
    return redirect(url_for('admin_articles'))

@app.route('/blogadmin/article/new', methods=['GET', 'POST'])
@login_required
def admin_article_new():
    s = get_settings()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '')
        is_pinned = request.form.get('is_pinned') == 'on'
        errors = []
        if not title or len(title) > 100:
            errors.append('标题必须1-100字符')
        if len(summary) > 200:
            errors.append('简介不能超过200字符')
        if is_pinned:
            pinned_count = Article.query.filter_by(is_pinned=True).count()
            if pinned_count >= 5:
                errors.append('置顶文章最多5篇，请先取消其他文章的置顶')
        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('admin/article_form.html', settings=s, article=None, title=title, summary=summary, content=content, is_pinned=is_pinned)
        cover_path = ''
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            ok, result = check_upload_security(cover_file)
            if not ok:
                flash(result, 'error')
                return render_template('admin/article_form.html', settings=s, article=None, title=title, summary=summary, content=content, is_pinned=is_pinned)
            if result == 'image':
                cropped = crop_cover(cover_file)
                fname = sanitize_filename(cover_file.filename)
                month_dir = os.path.join(QUILL_UPLOAD_DIR, datetime.now().strftime('%Y/%m'))
                os.makedirs(month_dir, exist_ok=True)
                filepath = os.path.join(month_dir, fname)
                with open(filepath, 'wb') as f:
                    f.write(cropped.read())
                cover_path = os.path.relpath(filepath, BASE_DIR)
        article = Article(title=title, summary=summary, content=clean_html(content), cover=cover_path, is_pinned=is_pinned)
        db.session.add(article)
        db.session.commit()
        flash('文章创建成功', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin/article_form.html', settings=s, article=None, title='', summary='', content='', is_pinned=False)

@app.route('/blogadmin/article/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def admin_article_edit(article_id):
    s = get_settings()
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        summary = request.form.get('summary', '').strip()
        content = request.form.get('content', '')
        is_pinned = request.form.get('is_pinned') == 'on'
        errors = []
        if not title or len(title) > 100:
            errors.append('标题必须1-100字符')
        if len(summary) > 200:
            errors.append('简介不能超过200字符')
        if is_pinned:
            pinned_count = Article.query.filter_by(is_pinned=True).filter(Article.id != article_id).count()
            if pinned_count >= 5:
                errors.append('置顶文章最多5篇，请先取消其他文章的置顶')
        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('admin/article_form.html', settings=s, article=article, title=title, summary=summary, content=content, is_pinned=is_pinned)
        cover_file = request.files.get('cover')
        if cover_file and cover_file.filename:
            ok, result = check_upload_security(cover_file)
            if not ok:
                flash(result, 'error')
                return render_template('admin/article_form.html', settings=s, article=article, title=title, summary=summary, content=content, is_pinned=is_pinned)
            if result == 'image':
                if article.cover and os.path.exists(os.path.join(BASE_DIR, article.cover)):
                    os.remove(os.path.join(BASE_DIR, article.cover))
                cropped = crop_cover(cover_file)
                fname = sanitize_filename(cover_file.filename)
                month_dir = os.path.join(QUILL_UPLOAD_DIR, datetime.now().strftime('%Y/%m'))
                os.makedirs(month_dir, exist_ok=True)
                filepath = os.path.join(month_dir, fname)
                with open(filepath, 'wb') as f:
                    f.write(cropped.read())
                article.cover = os.path.relpath(filepath, BASE_DIR)
        article.title = title
        article.summary = summary
        article.content = clean_html(content)
        article.is_pinned = is_pinned
        article.updated_at = datetime.utcnow()
        db.session.commit()
        flash('文章更新成功', 'success')
        return redirect(url_for('admin_articles'))
    return render_template('admin/article_form.html', settings=s, article=article, title=article.title, summary=article.summary, content=article.content, is_pinned=article.is_pinned)

@app.route('/blogadmin/article/delete/<int:article_id>', methods=['POST'])
@login_required
def admin_article_delete(article_id):
    referer = request.headers.get('Referer', '')
    if '/blogadmin' not in referer:
        abort(403)
    article = Article.query.get_or_404(article_id)
    if article.cover and os.path.exists(os.path.join(BASE_DIR, article.cover)):
        os.remove(os.path.join(BASE_DIR, article.cover))
    db.session.delete(article)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('admin_articles'))

@app.route('/blogadmin/article/toggle_pin/<int:article_id>', methods=['POST'])
@login_required
def admin_toggle_pin(article_id):
    article = Article.query.get_or_404(article_id)
    if not article.is_pinned:
        pinned_count = Article.query.filter_by(is_pinned=True).count()
        if pinned_count >= 5:
            flash('置顶文章最多5篇，请先取消其他文章的置顶', 'error')
            return redirect(url_for('admin_articles'))
    article.is_pinned = not article.is_pinned
    db.session.commit()
    flash('置顶状态已更新', 'success')
    return redirect(url_for('admin_articles'))

# ============================================================
# 后台 - 站点设置
# ============================================================

@app.route('/blogadmin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    s = get_settings()
    if request.method == 'POST':
        blog_name = request.form.get('blog_name', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        errors = []
        if not blog_name or len(blog_name) > 100:
            errors.append('博客名称必须1-100字符')
        if len(subtitle) > 50:
            errors.append('署名不能超过50字符')
        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('admin/settings.html', settings=s)
        s.blog_name = blog_name
        s.subtitle = subtitle
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            if not allowed_file(logo_file.filename, {'jpg', 'jpeg', 'png'}):
                flash('Logo只能是jpg/jpeg/png格式', 'error')
                return render_template('admin/settings.html', settings=s)
            if s.logo and os.path.exists(os.path.join(BASE_DIR, s.logo)):
                os.remove(os.path.join(BASE_DIR, s.logo))
            fname = sanitize_filename(logo_file.filename)
            logo_dir = os.path.join(UPLOAD_DIR, 'logo')
            os.makedirs(logo_dir, exist_ok=True)
            filepath = os.path.join(logo_dir, fname)
            logo_file.save(filepath)
            s.logo = os.path.relpath(filepath, BASE_DIR)
        s.first_run = False
        db.session.commit()
        flash('设置已保存', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin/settings.html', settings=s)

# ============================================================
# 后台 - 修改密码
# ============================================================

@app.route('/blogadmin/change_password', methods=['GET', 'POST'])
@login_required
def admin_change_password():
    s = get_settings()
    is_first = s.first_run
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not verify_password(current_password, s.password_hash):
            flash('当前密码错误', 'error')
            return render_template('admin/change_password.html', settings=s, is_first=is_first)
        if len(new_password) < 6:
            flash('新密码至少6位', 'error')
            return render_template('admin/change_password.html', settings=s, is_first=is_first)
        if new_password != confirm_password:
            flash('两次输入的密码不一致', 'error')
            return render_template('admin/change_password.html', settings=s, is_first=is_first)
        s.password_hash = hash_password(new_password)
        s.first_run = False
        db.session.commit()
        flash('密码修改成功', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/change_password.html', settings=s, is_first=is_first)

# ============================================================
# 后台 - 关于（纯展示，只读）
# ============================================================

@app.route('/blogadmin/about')
@login_required
def admin_about():
    s = get_settings()
    return render_template('admin/about.html', settings=s)

# ============================================================
# Quill上传接口
# ============================================================

@app.route('/upload/quill', methods=['POST'])
@login_required
def upload_quill():
    if 'upload' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    file = request.files['upload']
    if not file or not file.filename:
        return jsonify({'error': '未选择文件'}), 400
    ok, result = check_upload_security(file)
    if not ok:
        return jsonify({'error': result}), 400
    fname = sanitize_filename(file.filename)
    month_dir = os.path.join(QUILL_UPLOAD_DIR, datetime.now().strftime('%Y/%m'))
    os.makedirs(month_dir, exist_ok=True)
    filepath = os.path.join(month_dir, fname)
    file.save(filepath)
    url = '/' + os.path.relpath(filepath, BASE_DIR)
    return jsonify({'url': url})

@app.route('/static/quill/<path:filename>')
def quill_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'static', 'quill'), filename)

# ============================================================
# 启动
# ============================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        get_settings()
    app.run(host='0.0.0.0', port=31258, debug=False)
