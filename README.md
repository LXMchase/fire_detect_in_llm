conda create --name myenv python=3.10.9
conda activate myenv
conda install -c conda-forge nodejs
验证 Node.js 和 npm 是否安装成功：
node -v
npm -v
# environment：
设置淘宝镜像：
npm config set registry https://registry.npmmirror.com
npm install -g @vue/cli
npm install axios
# dependency：
django>=3.0,<4.0
djangorestframework>=3.12,<4.0
django-cors-headers
daphne
Pillow>=8.0,<9.0
channels>=3.0,<4.0
dashscope>=1.0,<2.0
opencv-python>=4.5,<5.0
numpy>=1.19,<2.0
scikit-image>=0.18,<1.0
scikit-learn>=0.24,<1.0
# run:
fire_detect/：
daphne fire_detect.asgi:application
frontend/:
npm run serve
