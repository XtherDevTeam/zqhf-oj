# Makefile is for setup your environment quickly
init:
	pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask requests urllib3 websockets demjson markdown markdown-katex shutil
	chmod +x server.py

dbrun:
	python3 ./database_server.py

runapp:
	python3 ./server.py

run: XmediaCenter.py
	./server.py