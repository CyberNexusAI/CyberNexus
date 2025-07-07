# 启动
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload


# 构建镜像
docker build -t manus-sandbox .

# 运行容器
docker run -d -p 8080:8080 -p 9222:9222 -p 5900:5900 -p 5901:5901 manus-sandbox