# Makefile is for setup your environment quickly
init:
	pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask requests urllib3 websockets
	chmod +x server.py

run: XmediaCenter.py
	./server.py