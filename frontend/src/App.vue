<template>
  <div id="main-container">
    <h1>光影识慧 v0.2</h1>
    
    <!-- 功能说明 -->
    <div class="info-panel">
      <p><strong>版本更新 (v0.2):</strong> 新增了基于 VLM 模型的智能季节分类功能。您可以启动分类任务，然后按季节浏览照片。</p>
      <p><strong>注意:</strong> 季节分类需要您在本地运行一个兼容 OpenAI API 的 VLM 服务 (如 LM Studio)，并确保模型已正确加载。</p>
    </div>

    <!-- 索引控制 -->
    <div class="control-section">
      <h2>1. 扫描与索引</h2>
      <div class="control-panel">
        <input type="text" v-model="directory" placeholder="请输入要扫描的绝对路径" />
        <button @click="startIndexing" :disabled="isProcessing">{{ isIndexing ? '正在索引...' : '开始索引' }}</button>
        <button @click="loadAllImages" :disabled="isProcessing">加载全部</button>
      </div>
    </div>

    <!-- 季节分类控制 -->
    <div class="control-section">
      <h2>2. 智能分类</h2>
      <div class="control-panel">
        <button @click="startSeasonClassification" :disabled="isProcessing">{{ isClassifying ? '正在分类...' : '按季节分类' }}</button>
      </div>
    </div>

    <!-- 季节浏览 -->
    <div class="control-section">
      <h2>3. 按季节浏览</h2>
      <div class="control-panel season-buttons">
        <button @click="loadSeasonImages('Spring')" :disabled="isProcessing">春</button>
        <button @click="loadSeasonImages('Summer')" :disabled="isProcessing">夏</button>
        <button @click="loadSeasonImages('Autumn')" :disabled="isProcessing">秋</button>
        <button @click="loadSeasonImages('Winter')" :disabled="isProcessing">冬</button>
      </div>
    </div>

    <!-- 状态与日志 -->
    <div class="status-panel">
      <h2>状态: {{ status }}</h2>
      <div v-if="error" class="error-message">错误: {{ error }}</div>
    </div>
    <div class="output-log">
      <h3>{{ logTitle }} ({{ foundImages.length }}):</h3>
      <ul>
        <li v-for="image in foundImages" :key="image">{{ image }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { io } from 'socket.io-client';

const directory = ref('');
const isIndexing = ref(false);
const isClassifying = ref(false);
const status = ref('待命');
const error = ref('');
const foundImages = ref([]);
const logTitle = ref('控制台输出');
let socket = null;

// 计算属性，判断是否有任何处理正在进行中
const isProcessing = computed(() => isIndexing.value || isClassifying.value);

onMounted(() => {
  socket = io('http://localhost:8000');

  socket.on('connect', () => { status.value = '已连接到后端服务'; });
  socket.on('disconnect', () => {
    status.value = '与后端服务断开连接';
    isIndexing.value = false;
    isClassifying.value = false;
  });

  socket.on('message', (data) => { console.log('Message from server:', data); });
  socket.on('error', (data) => {
    error.value = data.data;
    status.value = '出现错误';
    isIndexing.value = false;
    isClassifying.value = false;
  });

  // --- 索引事件 ---
  socket.on('indexing_status', (data) => {
    status.value = data.data;
    isIndexing.value = true;
    error.value = '';
    foundImages.value = [];
    logTitle.value = '实时发现的新图片';
  });
  socket.on('new_image_found', (data) => { foundImages.value.unshift(data.path); });
  socket.on('indexing_complete', (data) => {
    status.value = data.data;
    isIndexing.value = false;
  });
  socket.on('all_images_loaded', (data) => {
    foundImages.value = data.images.map(img => img.path);
    logTitle.value = '所有已索引的图片';
    status.value = `加载了 ${data.images.length} 张图片`;
    error.value = '';
  });

  // --- 季节分类事件 ---
  socket.on('classification_status', (data) => {
    status.value = data.data;
    isClassifying.value = true;
    error.value = '';
    logTitle.value = '分类日志';
    foundImages.value = []; // 清空旧列表
  });
  socket.on('classification_complete', (data) => {
    status.value = data.data;
    isClassifying.value = false;
  });
  socket.on('season_images_loaded', (data) => {
    foundImages.value = data.images.map(img => img.path);
    logTitle.value = `${data.season}季的图片`;
    status.value = `加载了 ${data.images.length} 张${data.season}季的图片`;
    error.value = '';
  });
});

const startIndexing = () => {
  if (!directory.value.trim()) {
    error.value = '目录不能为空';
    return;
  }
  if (socket) socket.emit('start_indexing', { directory: directory.value });
};

const loadAllImages = () => {
  if (socket) {
    status.value = '正在从数据库加载...';
    foundImages.value = [];
    error.value = '';
    socket.emit('load_all_images', {});
  }
};

const startSeasonClassification = () => {
  if (socket) {
    status.value = '正在准备分类...';
    error.value = '';
    socket.emit('start_season_classification', {});
  }
};

const loadSeasonImages = (season) => {
  if (socket) {
    status.value = `正在加载${season}季图片...`;
    foundImages.value = [];
    error.value = '';
    socket.emit('load_season_images', { season: season });
  }
};
</script>

<style>
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: #f4f4f9;
  color: #333;
  margin: 0;
  padding: 2rem;
}

#main-container {
  max-width: 800px;
  margin: 0 auto;
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px_10px rgba(0,0,0,0.1);
}

h1 {
  color: #4a4a4a;
  text-align: center;
  margin-bottom: 1rem;
}

h2 {
  color: #4a4a4a;
  border-bottom: 2px solid #eef2ff;
  padding-bottom: 0.5rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.info-panel {
  background-color: #eef2ff;
  border-radius: 4px;
  padding: 1rem;
  margin-bottom: 2rem;
  color: #4338ca;
  font-size: 0.9rem;
}
.info-panel p {
  margin: 0.5rem 0;
}

.control-section {
  margin-bottom: 1.5rem;
}

.control-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.control-panel input {
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  min-width: 200px;
}

.control-panel button {
  padding: 0.75rem 1.5rem;
  border: none;
  background-color: #6366f1;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
  white-space: nowrap;
}

.control-panel button:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
}

.control-panel button:hover:not(:disabled) {
  background-color: #4f46e5;
}

.season-buttons button {
  background-color: #38bdf8;
}
.season-buttons button:hover:not(:disabled) {
  background-color: #0ea5e9;
}

.status-panel {
  margin-top: 2rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-left: 4px solid #6366f1;
}

.status-panel h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #4338ca;
  border: none;
}

.error-message {
  color: #ef4444;
  margin-top: 0.5rem;
  font-weight: bold;
}

.output-log {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  max-height: 400px;
  overflow-y: auto;
}

.output-log h3 {
  margin-top: 0;
  color: #111827;
}

.output-log ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.output-log li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
  font-family: "Courier New", Courier, monospace;
  font-size: 0.9rem;
  color: #374151;
  word-break: break-all;
}

.output-log li:last-child {
  border-bottom: none;
}
</style>
