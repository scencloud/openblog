# OpenBlog - 通用开源博客系统

> 一个轻量、安全、完全离线的单文件博客系统，基于 Flask + SQLite，开箱即用。

---

## 📋 目录

- [功能概览](#功能概览)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [目录结构](#目录结构)
- [功能详解](#功能详解)
  - [前台功能](#前台功能)
  - [后台功能](#后台功能)
- [安全机制](#安全机制)
- [环境变量](#环境变量)
- [使用说明](#使用说明)
- [限制与注意事项](#限制与注意事项)
- [常见问题](#常见问题)
- [License](#license)

---

## ✨ 功能概览

| 类别 | 功能 | 状态 |
|------|------|------|
| 前台 | Logo + 博客名称 + 署名（均可后台修改） | ✅ |
| 前台 | 3:2 横向文章卡片列表 | ✅ |
| 前台 | 文章标题 + 简介 + 查看详情按钮 | ✅ |
| 前台 | 文章详情页（封面 + 标题 + 简介 + 正文） | ✅ |
| 前台 | 图片 / 视频内嵌显示 | ✅ |
| 前台 | 响应式布局（PC + 手机） | ✅ |
| 前台 | 置顶文章 📌 标签 | ✅ |
| 前台 | 底部版权信息（Powered by OpenBlog） | ✅ |
| 后台 | 登录系统 + 暴力破解保护（5次锁定15分钟） | ✅ |
| 后台 | 首次登录强制修改默认密码 | ✅ |
| 后台 | 修改密码 | ✅ |
| 后台 | 文章增删改查 | ✅ |
| 后台 | 封面图上传 + 自动 3:2 裁剪 | ✅ |
| 后台 | Quill 本地离线富文本编辑器 | ✅ |
| 后台 | 图片上传（≤5MB） | ✅ |
| 后台 | 视频上传（≤50MB） | ✅ |
| 后台 | 置顶控制（最多5篇） | ✅ |
| 后台 | 排序切换（按时间 / 随机） | ✅ |
| 后台 | 站点设置（改名称 / 署名 / Logo） | ✅ |
| 后台 | 关于模块（展示联系方式、使用授权、免责声明） | ✅ |
| 安全 | XSS 防护（bleach 清洗 + 模板转义） | ✅ |
| 安全 | SQL 注入防护（SQLAlchemy ORM） | ✅ |
| 安全 | CSRF 防护（Referer 校验 + POST 限制） | ✅ |
| 安全 | 文件上传白名单 + MIME 验证 + PIL 校验 + UUID 重命名 | ✅ |
| 安全 | 密码 PBKDF2 哈希 | ✅ |
| 安全 | Session 安全（HttpOnly + SameSite） | ✅ |
| 安全 | 安全响应头（X-Frame-Options / X-Content-Type-Options 等） | ✅ |
| 安全 | 自定义 404 / 500 错误页面 | ✅ |
| 部署 | 单文件架构，极简部署 | ✅ |
| 部署 | 默认端口 31258 | ✅ |
| 部署 | debug=False 生产模式 | ✅ |
| 部署 | Quill 完全离线引入，无需联网 | ✅ |

---

## 🛠 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Flask |
| 数据库 | SQLite（通过 Flask-SQLAlchemy） |
| 富文本编辑器 | Quill 1.3.7（本地离线） |
| 密码加密 | PBKDF2-SHA256（100,000 次迭代） |
| HTML 清洗 | bleach |
| 图片处理 | Pillow（自动 3:2 裁剪） |
| 运行环境 | Python 3.8+ |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask flask-sqlalchemy bleach pillow
```

### 2. 下载 Quill（离线编辑器）

```bash
mkdir -p static/quill
cd static/quill
wget https://cdn.quilljs.com/1.3.7/quill.snow.css
wget https://cdn.quilljs.com/1.3.7/quill.js
```

### 3. 启动服务

```bash
python app.py
```

### 4. 访问

| 页面 | 地址 |
|------|------|
| 前台首页 | http://你的IP:31258 |
| 后台管理 | http://你的IP:31258/blogadmin |
| 默认密码 | `blogadmin666` |

---

## 📁 目录结构

```
openblog/
├── app.py                          # 主程序（单文件）
├── README.md                       # 说明文档
├── data/
│   └── blog.db                     # SQLite 数据库（自动生成）
├── static/
│   ├── css/
│   │   └── style.css               # 极客暗色主题样式
│   ├── quill/
│   │   ├── quill.js                # Quill 编辑器核心
│   │   └── quill.snow.css          # Quill 主题样式
│   └── uploads/
│       ├── logo/                   # Logo 文件
│       └── quill/                  # Quill 上传的图片/视频
│           └── YYYY/MM/            # 按年/月分目录
└── templates/
    ├── base.html                   # 基础模板
    ├── home.html                   # 前台首页
    ├── article.html                # 文章详情页
    ├── error.html                  # 错误页面（404/500）
    └── admin/
        ├── login.html              # 后台登录
        ├── dashboard.html          # 后台仪表盘
        ├── articles.html           # 文章列表
        ├── article_form.html       # 新建/编辑文章
        ├── settings.html           # 站点设置
        ├── change_password.html    # 修改密码
        └── about.html              # 关于（只读展示）
```

---

## 📖 功能详解

### 前台功能

#### 首页

从上到下依次显示：
1. **顶部区域**：Logo 图片 + 博客名称 + 署名（一句话描述）
2. **文章列表**：一行一篇，3:2 横向卡片，包含封面图、标题、简介、"查看详情"按钮
3. **底部**：版权信息

- 置顶文章始终排在最前面
- 无分页，所有文章一页显示
- 首页无后台入口链接

#### 文章详情页

- 顶部大图封面（最大高度 400px）
- 文章标题
- 文章简介（左侧蓝色边框高亮）
- 正文内容（支持 Quill 富文本，含图片/视频）
- "← 返回首页"链接

#### 响应式适配

| 设备 | 表现 |
|------|------|
| PC 端 | 正常横向卡片布局 |
| 手机端（≤640px） | Logo 缩小、卡片纵向排列、字体调整 |

---

### 后台功能

#### 登录系统

| 特性 | 说明 |
|------|------|
| 入口 | `/blogadmin`（首页无入口） |
| 默认密码 | `blogadmin666` |
| 密码加密 | PBKDF2-SHA256（10万次迭代） |
| 暴力破解防护 | 5次失败锁定15分钟 |
| 首次登录 | 强制跳转修改密码 |
| 退出登录 | `/blogadmin/logout` |

#### 后台仪表盘

卡片式布局，包含四个模块：

| 模块 | 功能 |
|------|------|
| 📝 文章管理 | 增删改查、置顶控制 |
| ⚙️ 站点设置 | 修改博客名称、署名、Logo |
| ℹ️ 关于 | 展示联系方式、使用授权、免责声明 |
| 🔑 修改密码 | 更新管理员密码 |

#### 文章管理

**文章列表：**
- 显示标题、状态（置顶/普通）、创建时间、操作按钮
- 排序切换：⏰ 按时间 / 🎲 随机
- 置顶文章始终排最前

**新建文章：**

| 字段 | 限制 | 说明 |
|------|------|------|
| 封面图 | jpg/jpeg/png/gif/webp | 自动裁剪为 3:2 |
| 标题 | ≤100字符 | 前后端双重校验 |
| 简介 | ≤200字符 | 前后端双重校验 |
| 正文 | 无限制 | Quill 编辑器 |
| 置顶 | 最多5篇 | 超限时提示 |

**编辑文章：**
- 自动填充已有数据
- 更换封面时自动删除旧文件

**删除文章：**
- 二次确认弹窗
- 自动删除关联封面文件
- CSRF 防护（Referer 校验）

**置顶控制：**
- 每个文章独立控制
- 最多置顶5篇
- 达上限时提示用户手动取消

#### Quill 富文本编辑器

| 特性 | 说明 |
|------|------|
| 引入方式 | 本地引入，完全离线 |
| 图片上传 | jpg/jpeg/png/gif/webp，≤5MB |
| 视频上传 | mp4/webm/ogg/mov，≤50MB |
| 上传接口 | `/upload/quill` |
| 存储路径 | `static/uploads/quill/年/月/` |
| 工具栏 | 加粗、斜体、标题、列表、链接、图片、视频、代码块、引用、清除格式 |
| 安全 | 后端 bleach 清洗 HTML |

#### 站点设置

| 设置项 | 限制 | 默认值 |
|--------|------|--------|
| 博客名称 | ≤100字符 | xxx的博客 |
| 署名 | ≤50字符 | 记录生活，分享思考 |
| Logo | jpg/jpeg/png | 无 |

#### 关于模块

后台只读展示页面，包含：
- ScenCloud 品牌信息
- 官方网站、联系方式
- 使用授权说明
- 12条免责声明

---

## 🔒 安全机制

| 攻击类型 | 防护措施 |
|----------|----------|
| XSS | bleach 清洗 + 协议过滤 + 模板转义 |
| SQL 注入 | SQLAlchemy ORM 参数化查询 |
| CSRF | Referer 校验 + POST 限制 |
| 文件上传 | 白名单 + MIME 验证 + PIL 校验 + UUID 重命名 + 大小限制 |
| 密码泄露 | PBKDF2 哈希（不可逆） |
| Session 劫持 | HttpOnly + SameSite |
| 暴力破解 | 5次失败锁定15分钟 |
| 点击劫持 | X-Frame-Options: DENY |
| 信息泄露 | 自定义 404/500 页面，debug=False |

### 安全响应头

对 HTML 页面（非静态文件）自动添加以下响应头：

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

> ⚠️ 静态文件（图片/视频）不添加 `X-Frame-Options`，避免浏览器拦截资源加载。

---

## ⚙️ 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BLOG_SECRET_KEY` | 自动生成（随机） | Flask 会话密钥 |
| `BLOG_DEFAULT_PASSWORD` | `blogadmin666` | 默认管理员密码 |
| `FLASK_DEBUG` | `False` | 调试模式（生产环境勿开启） |

---

## 📖 使用说明

### 首次使用

1. 启动服务：`python app.py`
2. 打开浏览器访问 `http://你的IP:31258/blogadmin`
3. 输入默认密码 `blogadmin666` 登录
4. **首次登录会强制跳转到修改密码页面，请立即修改！**
5. 进入「站点设置」，修改博客名称、署名、上传 Logo
6. 进入「关于」查看联系方式和免责声明（默认为 ScenCloud 信息）
7. 开始写文章 → 进入「文章管理」→ 点击「新建文章」

### 日常使用

- **写文章**：后台 → 文章管理 → 新建文章 → 填写标题/简介/正文 → 上传封面 → 保存
- **置顶文章**：文章列表中点击「置顶」按钮（最多5篇）
- **修改站点信息**：后台 → 站点设置
- **修改密码**：后台 → 修改密码
- **查看文章**：前台首页点击「查看详情」

### 关于 Quill 编辑器

- 图片/视频通过编辑器工具栏上传，自动存储到 `static/uploads/quill/年/月/`
- 支持拖拽粘贴图片
- 视频格式支持：mp4、webm、ogg、mov
- 视频最大 50MB，图片最大 5MB

---

## ⚠️ 限制与注意事项

### 功能限制

| 项目 | 限制 |
|------|------|
| 置顶文章数量 | 最多 5 篇 |
| 文章标题长度 | 1-100 字符 |
| 文章简介长度 | 0-200 字符 |
| 图片上传大小 | ≤ 5MB |
| 视频上传大小 | ≤ 50MB |
| 支持的图片格式 | jpg, jpeg, png, gif, webp |
| 支持的视频格式 | mp4, webm, ogg, mov |
| Logo 格式 | jpg, jpeg, png |
| 新密码长度 | ≥ 6 位 |
| 博客名称长度 | 1-100 字符 |
| 署名长度 | 0-50 字符 |
| 文章分页 | 无（所有文章一页显示） |

### 架构限制

| 项目 | 说明 |
|------|------|
| 数据库 | SQLite，不适合高并发场景 |
| 并发能力 | Flask 开发服务器，仅适合小规模使用 |
| 多用户 | 仅支持单一管理员账户 |
| 评论系统 | 不支持 |
| 文章分类/标签 | 不支持 |
| 全文搜索 | 不支持 |
| 多语言 | 仅支持中文 |
| CDN/缓存 | 不支持（静态文件直接由 Flask 提供） |

### 部署限制

| 项目 | 说明 |
|------|------|
| 生产部署 | 建议使用 Gunicorn + Nginx |
| 数据库备份 | 需手动备份 `data/blog.db` |
| 文件备份 | 需手动备份 `static/uploads/` |
| HTTPS | 需通过 Nginx 反向代理配置 |
| 端口 | 默认 31258，可在代码中修改 |

### 安全限制

| 项目 | 说明 |
|------|------|
| 会话管理 | 基于 Flask session，24小时过期 |
| 密码策略 | 仅要求长度 ≥ 6 位，无复杂度要求 |
| 上传扫描 | 依赖 PIL 验证，不保证 100% 安全 |
| DDoS 防护 | 无，需外部防护 |

---

## ❓ 常见问题

### Q: 如何修改端口？

打开 `app.py`，找到最后一行：

```python
app.run(host='0.0.0.0', port=31258, debug=False)
```

将 `31258` 改为你要的端口号。

### Q: 如何备份数据？

备份以下两个位置：
1. `data/blog.db` — 数据库文件
2. `static/uploads/` — 上传的图片和视频

### Q: 如何重置管理员密码？

删除数据库文件后重启服务，会自动创建默认密码：

```bash
rm data/blog.db
python app.py
```

然后用默认密码 `blogadmin666` 重新登录。

### Q: 视频插入后显示 ERR_BLOCKED_BY_RESPONSE？

已修复。安全响应头现在不对静态文件添加 `X-Frame-Options: DENY`，视频/图片可正常加载。

### Q: 如何在生产环境部署？

推荐使用 Gunicorn + Nginx：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动（4个worker）
gunicorn -w 4 -b 127.0.0.1:31258 app:app
```

Nginx 反向代理配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:31258;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/openblog/static/;
        expires 7d;
    }
}
```

### Q: 关于模块的内容如何修改？

编辑 `app.py` 中 `get_settings()` 函数里的 `default_about` 变量，修改 HTML 内容后重启服务。

> ⚠️ 修改前需先删除数据库（`rm data/blog.db`），因为默认值只在首次创建时写入。

---

## 📄 License

MIT License - 自由使用，保留版权声明即可。

---

> ScenCloud · www.scencloud.com · contact@scencloud.com
