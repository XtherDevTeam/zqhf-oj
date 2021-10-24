# Makefile is for setup your environment quickly
init:
	pip install -i https://pypi.tuna.tsinghua.edu.cn/simple socket flask requests urllib3 pickle websockets demjson markdown
	chmod +x server.py

run: XmediaCenter.py
	./server.py