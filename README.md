# 光影识慧 (PhotoInsight) v0.1

![Project Banner](https://placehold.co/800x200/6366f1/white?text=PhotoInsight&font=raleway)

**一个由AI驱动的本地照片智能管理与检索工具。利用视觉语言模型（VLM）深度理解您的每一张照片。**

---

## 📖 项目简介

`光影识慧 (PhotoInsight)` 是一个旨在彻底改变您管理和浏览本地照片库方式的桌面应用项目。传统的照片管理依赖于手动的文件夹整理和标签添加，费时费力。本项目通过引入先进的AI模型，实现对照片内容的自动化分析，并提供强大的语义搜索功能。

**当前版本 (v0.1)** 已完成核心后端引擎的开发，能够稳定地扫描本地图片、提取视觉特征并建立索引，为后续的智能搜索和管理功能奠定了坚实的基础。

## ✨ v0.1 核心功能

* **🗂️ 实时文件索引:** 通过Websocket与前端连接，实时扫描指定目录，为所有图片（支持`.jpg`, `.jpeg`, `.png`, `.webp`）创建元数据索引。
* **🧠 核心AI能力:** 集成 **CLIP** 模型，为每张图片生成高质量的特征向量（Embeddings），这是实现语义搜索和以图搜图的关键。
* **🗄️ 双数据库存储:**
    * **元数���存储 (SQLite):** 高效存储图片的路径、大小等基本信息。
    * **向量存储 (ChromaDB):** 持久化存储图片特征向量，用于未来的相似性搜索。
* **📡 API & Websocket 服务:** 基于 **FastAPI** 和 **Socket.IO** 搭建后端服务，提供稳定的接口和实时的进度反馈。

## 🛠️ 技术栈 (Tech Stack)

* **后端 (Backend):**
    * **语言:** Python 3.9+
    * **框架:** FastAPI, Uvicorn
    * **实时通信:** Python-SocketIO
    * **数据库:**
        * **元数据存储:** SQLite (通过 SQLAlchemy)
        * **向量存储:** ChromaDB
    * **AI / 特征提取:** CLIP (通过 `sentence-transformers` 库)
* **前端 (Frontend):**
    * **框架:** Vue 3
    * **构建工具:** Vite
    * **UI库:** (待定)

## 🗺️ 项目路线图 (Roadmap)

-   **[v0.1 - 核心引擎]**
    -   [x] 实现文件扫描与基础元数据索引功能 (SQLite)。
    -   [x] 完成核心的后端API与Websocket框架搭建 (FastAPI, Socket.IO)。
    -   [x] 集成图片特征提取模型 (CLIP)，生成图片向量并存入向量数据库 (ChromaDB)。

-   **[v0.2 - AI赋能与搜索]**
    -   [ ] 实现基于文本的语义搜索API（例如输入“海滩上的日落”）。
    -   [ ] 集成多模态VLM (如Gemma, LLaVA)，实现对图片的自动文本描述/打标。
    -   [ ] 将AI生成的标签更新到元数据索引中。

-   **[v0.3 - 可视化界面]**
    -   [ ] 搭建前端项目框架，实现图片瀑布流预览界面。
    -   [ ] 对接后端API，展示图片和分类，并实现搜索功能。
    -   [ ] 实现图片上传或指定目录的功能界面。

-   **[v0.4 - 高级功能]**
    -   [ ] 实现以图搜图功能的前后端逻辑。
    -   [ ] 提供文件复制/移动等管理操作。

-   **[v1.0 - 正式版]**
    -   [ ] 性能优化和Bug修复。
    -   [ ] 使用Tauri或Electron打包成桌面应用。
    -   [ ] 撰写完整的用户文档。

## 🚀 安装与使用 (Installation & Usage)

### 1. 环境准备

-   确保你已安装 Python 3.9+ 和 Node.js (v16+)。
-   克隆本仓库:
    ```bash
    git clone https://github.com/your-username/photo-insight-buct.git
    cd photo-insight-buct
    ```

### 2. 启动后端服务

```bash
# 1. 进入后端目录
cd backend

# 2. 安装Python依赖
# 建议在虚拟环境中使用
pip install -r requirements.txt

# 3. 启动FastAPI服务
# 服务将运行在 http://127.0.0.1:8000
uvicorn main:socket_app --host 127.0.0.1 --port 8000
```
后端启动后，会自动创建 `backend/photo_insight.db` (SQLite数据库) 和 `chroma_db` 目录（向量数据库）。

### 3. 启动前端界面

```bash
# 1. (在另一个终端中) 进入前端目录
cd frontend

# 2. 安装Node.js依赖
npm install

# 3. 启动开发服务器
# 服务将运行在 http://localhost:5173
npm run dev
```
现在，你可以打开浏览器访问 `http://localhost:5173` 来使用应用。

## 🤝 如何贡献 (Contributing)

欢迎任何形式的贡献！您可以：
* 提交Bug报告或功能建议到 `Issues`。
* Fork本仓库，创建您的功能分支，然后提交 Pull Request。

在提交代码前，请确保您的代码遵循项目现有的编码风格。

## 📄 许可证 (License)

本项目采用 [MIT License](LICENSE) 开源许可证。