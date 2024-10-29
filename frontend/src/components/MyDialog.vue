<template>
  <div class="chat-container">
    <div class="messages">
      <div
        class="message"
        v-for="msg in messages.slice().reverse()"
        :key="msg.timestamp"
        :class="{ 'user-message': msg.username === username, 'server-message': msg.username === 'Server' }">
        <span v-if="msg.type === 'text'" class="content">{{ msg.content }}</span>
        <img v-if="msg.type === 'image'" :src="msg.content" alt="Processed Image" class="file-content" />
      </div>
    </div>
    <div class="input-container">
      <input
        v-model="newMessage"
        placeholder="Type a message..."
        @keyup.enter="sendMessage"
        class="message-input"
      />
      <input
        type="file"
        @change="uploadFile"
        class="file-input"
        accept="image/*,video/*"
        id="file-upload"
      />
      <label for="file-upload" class="upload-button">img/video</label>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      messages: [],
      newMessage: '',
      username: 'User', // 可以根据需要修改
      socket: null // WebSocket 实例
    };
  },
  methods: {
    connectWebSocket() {
      this.socket = new WebSocket('ws://localhost:8000/ws/messages/');

      this.socket.onopen = () => {
        console.log('WebSocket connection established');
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.messages.push(data); // 添加服务器消息
        console.log('Received message from server:', data);
      };

      this.socket.onclose = () => {
        console.log('WebSocket connection closed');
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    },
    sendMessage() {
      if (this.newMessage.trim() === '') return; // 防止发送空消息

      const message = {
        username: this.username,
        content: this.newMessage,
        timestamp: Date.now(), // 添加时间戳
        type: 'text' // 添加消息类型
      };

      // 通过 WebSocket 发送消息
      this.socket.send(JSON.stringify(message));
      // 将发送的消息添加到本地消息列表
      this.messages.push(message); // 立即显示发送的消息
      this.newMessage = ''; // 清空输入
    },
    uploadFile(event) {
      const file = event.target.files[0];
      if (file) {
        // 文件类型检查
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!allowedTypes.includes(file.type)) {
          alert("Please upload a valid image file (JPEG/PNG/GIF).");
          return;
        }

        const reader = new FileReader();

        // 当文件读取完成后
        reader.onloadend = () => {
          const base64Image = reader.result; // 获取 Base64 编码的图像
          // 使用 Axios 上传 Base64 字符串
          axios.post('http://localhost:8000/api/upload/', { base64_image: base64Image }, {
            headers: {
              'Content-Type': 'application/json' // 发送 JSON 数据
            }
          })
          .then(response => {
            console.log('File uploaded:', response.data);
            const processedImageUrl = response.data.fileUrl; // 确保后端返回处理后的图像 URL
            //this.displayImage(processedImageUrl, 'Processed Image', false); // false表示服务端的消息 显示处理后的图像

            // 构造 WebSocket 消息
            const fileMessage = {
              username: this.username,
              content: processedImageUrl, // 返回的文件 URL
              timestamp: Date.now(),
              type: 'image' // 添加类型标识
            };

            // 将文件消息添加到本地消息列表
            this.messages.push(fileMessage);
            // 通过 WebSocket 发送文件消息
            this.socket.send(JSON.stringify(fileMessage));
          })
          .catch(error => {
            console.error('File upload failed:', error.response ? error.response.data : error.message);
            alert("File upload failed: " + (error.response ? error.response.data : error.message));
          });
        };
        // 将文件读取为 Data URL（Base64 编码）
        reader.readAsDataURL(file);
      }
    }
  },
  mounted() {
    this.connectWebSocket(); // 建立 WebSocket 连接
  }
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 80vh;
  border: 1px solid #ccc;
  border-radius: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.user-message {
  justify-content: flex-end; /* 用户消息右对齐 */
}

.server-message {
  justify-content: flex-start; /* 服务器消息左对齐 */
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column-reverse; /* 确保最新消息在底部 */
}

.message {
  display: flex;
  align-items: center;
  margin: 5px 0;
}

.content {
  background-color: #e1f5fe;
  padding: 8px 12px;
  border-radius: 15px;
  max-width: 70%;
}

.server-message .content {
  background-color: #f1f0f0;
}

.input-container {
  display: flex;
  align-items: center;
}

.message-input {
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 10px;
  outline: none;
  font-size: 16px;
  flex: 1;
}

.file-input {
  display: none;
}

.file-content {
  max-width: 300px; /* 设置最大宽度 */
  max-height: 500px; /* 设置最大高度 */
  object-fit: cover; /* 保持宽高比 */
}

.upload-button {
  cursor: pointer;
  margin-left: 10px;
  padding: 8px 12px;
  border: 1px solid #007bff;
  border-radius: 20px;
  background-color: #007bff;
  color: white;
  text-align: center;
}

.upload-button:hover {
  background-color: #0056b3;
}

.message-input:focus {
  border-color: #007bff;
}
</style>