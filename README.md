# 光影识慧 (PhotoInsight) v0.2

![Project Banner](https://placehold.co/800x200/6366f1/white?text=PhotoInsight&font=raleway)

**一个由AI驱动的本地照片智能管理与检索工具。利用视觉语言模型（VLM）深度理解您的每一张照片。**

---

## 📖 项目简介

`光影识慧 (PhotoInsight)` 是一个旨在彻底改变您管理和浏览本地照片库方式的桌面应用项目。传统的照片管理依赖于手动的文件夹整理和标签添加，费时费力。本项目通过引入先进的AI模型，实现对照片内容的自动化分析、分类，并提供强大的语义搜索功能。

**当前版本 (v0.2)** 在核心索引引擎的基础上，新增了AI驱动的 **季节分类** 功能，能够自动识别照片的季节属性，并允许用户按季节进行筛选和浏览。

## ✨ v0.2 核心功能

*   **🗂️ 实时文件索引:** 通过 Websocket 与前端连接，实时扫描指定目录，为所有图片（支持 `.jpg`, `.jpeg`, `.png`, `.webp`）创建元数据索引。
*   **🧠 核心AI能力 (特征提取):** 集成 **CLIP** 模型，为每张图片生成高质量的特征向量（Embeddings），这是实现语义搜索和以图搜图的关键。
*   **🍂 AI赋能 (��节分类):** **(新)** 利用外部大型视觉语言模型 (VLM)，对图片内容进行分析，自动识别并将其归类到 **春、夏、秋、冬** 四个季节。
*   **🗄️ 双数据库存储:**
    *   **元数据存储 (SQLite):** 高效存储图片路径、大小等基本信息，并通过独立的关联表存储季节分类结果。
    *   **向量存储 (ChromaDB):** 持久化存储图片特征向量，用于未来的相似性搜索。
*   **📡 API & Websocket 服务:** 基于 **FastAPI** 和 **Socket.IO** 搭建后端服务，提供稳定的接口和实时的进度反馈。

## 🛠️ 技术栈 (Tech Stack)

*   **后端 (Backend):**
    *   **语言:** Python 3.9+
    *   **框架:** FastAPI, Uvicorn
    *   **实时通信:** Python-SocketIO
    *   **数据库:**
        *   **元数据/关系:** SQLite (通过 SQLAlchemy)
        *   **向量数据:** ChromaDB
    *   **AI / ML:**
        *   **特征提取:** CLIP (通过 `transformers`)
        *   **内容分类:** 外部 VLM (需兼容 OpenAI API)
*   **前端 (Frontend):**
    *   **框架:** Vue 3
    *   **构建工具:** Vite
    *   **实时通信:** Socket.io-client

## 🗺️ 项目路线图 (Roadmap)

-   **[v0.1 - 核心引擎]**
    -   [x] 实现文件扫描与基础元数据索引功能 (SQLite)。
    -   [x] 完成核心的后端API��Websocket框架搭建 (FastAPI, Socket.IO)。
    -   [x] 集成图片特征提取模型 (CLIP)，生成图片向量并存入向量数据库 (ChromaDB)。

-   **[v0.2 - AI赋能与分类]**
    -   [x] **实现AI驱动的季节自动分类功能。**
    -   [x] **前端增加触发分类和按季节浏览的交互界面。**
    -   [ ] 实现基于文本的语义搜索API（例如输入“海滩上的日落”）。
    -   [ ] 集成多模态VLM (如Gemma, LLaVA)，实现对图片的自动文本描述/打标。

-   **[v0.3 - 可视化与搜索]**
    -   [ ] 搭建前端图片瀑布流预览界面。
    -   [ ] 对接后端API，在前端实现文本搜索功能。
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

# 2. (建议) 创建并激活Python虚拟环境
# python -m venv venv
# source venv/bin/activate  (Linux/macOS)
# venv\Scripts\activate  (Windows)

# 3. 安装Python依赖
pip install -r requirements.txt

# 4. 启动FastAPI服务
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

### 4. 使用季节分类功能 (重要)

-   季节分类功能依赖一个在本地运行的、兼容 OpenAI API 格式的大语言模型服务。
-   您可以使用 **LM Studio**, **Ollama** 或其他类似工具来加载您选择的VLM模型（例如 `LLaVA`）。
-   启动模型服务后，请确保其API端点为 `http://localhost:1234/v1/chat/completions`。这是后端代码中硬编码的地址。如果您的服务地址不同，请修改 `backend/classify_seasons.py` 文件中的 `openai.api_base` 地址。

现在，您可以打开浏览器访问 `http://localhost:5173` 来使用应用���。

## 🤝 如何贡献 (Contributing)

欢迎任何形式的贡献！您可以：
* 提交Bug报告或功能建议到 `Issues`。
* Fork本仓库，创建您的功能分支，然后提交 Pull Request。

在提交代码前，请确保您的代码遵循项目现有的编码风格。

## 📄 许可证 (License)

本项目采用 [MIT License](LICENSE) 开源许可证。
