import ayaka

# 使用fastapi作为驱动，返回fastapi对象
app = ayaka.init(logger_rank="SUCCESS")

# 使用uvicorn启动fastapi对象
if __name__ == "__main__":
    ayaka.run(app="__main__:app",host="127.0.0.1", port=19900)
