<template>
  <div id="main-container">
    <h1>光影识慧 - 索引过程</h1>
    <div class="control-panel">
      <input type="text" v-model="directory" placeholder="请输入要扫描的绝对路径" />
      <button @click="startIndexing" :disabled="isIndexing">{{ isIndexing ? '正在索引...' : '开始索引' }}</button>
      <button @click="loadAllImages" :disabled="isIndexing">加载已有索引</button>
    </div>
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
import { ref, onMounted } from 'vue';
import { io } from 'socket.io-client';

const directory = ref('');
const isIndexing = ref(false);
const status = ref('待命');
const error = ref('');
const foundImages = ref([]);
const logTitle = ref('控制台输出');
let socket = null;

onMounted(() => {
  socket = io('http://localhost:8000');

  socket.on('connect', () => {
    status.value = '已连接到后端服务';
  });

  socket.on('disconnect', () => {
    status.value = '与后端服务断开连接';
    isIndexing.value = false;
  });

  socket.on('message', (data) => {
    console.log('Message from server:', data);
  });

  socket.on('indexing_status', (data) => {
    status.value = data.data;
    isIndexing.value = true;
    error.value = '';
    foundImages.value = [];
    logTitle.value = '实时发现的新图片';
  });

  socket.on('new_image_found', (data) => {
    foundImages.value.unshift(data.path); // 将新图片添加到列表顶部
  });

  socket.on('indexing_complete', (data) => {
    status.value = data.data;
    isIndexing.value = false;
  });

  socket.on('all_images_loaded', (data) => {
    foundImages.value = data.images.map(img => img.path);
    logTitle.value = '已索引的图片';
    status.value = `加载了 ${data.images.length} 条已有索引`;
    error.value = '';
  });

  socket.on('error', (data) => {
    error.value = data.data;
    status.value = '出现错误';
    isIndexing.value = false;
  });
});

const startIndexing = () => {
  if (!directory.value.trim()) {
    error.value = '目录不能为空';
    return;
  }
  if (socket) {
    socket.emit('start_indexing', { directory: directory.value });
  }
};

const loadAllImages = () => {
  if (socket) {
    status.value = '正在从数据库加载...';
    foundImages.value = [];
    error.value = '';
    socket.emit('load_all_images', {});
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
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

h1 {
  color: #4a4a4a;
  text-align: center;
  margin-bottom: 2rem;
}

.control-panel {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.control-panel input {
  flex-grow: 1;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
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

.status-panel {
  margin-bottom: 2rem;
  padding: 1rem;
  background: #eef2ff;
  border-left: 4px solid #6366f1;
}

.status-panel h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #4338ca;
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
}

.output-log li:last-child {
  border-bottom: none;
}
</style>
