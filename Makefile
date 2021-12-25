# Makefile is for setup your environment quickly
init:
	pip install -i https://pypi.tuna.tsinghua.edu.cn/simple flask requests urllib3 websockets demjson markdown markdown-katex shutil
	chmod +x server.py

dbrun:
	python3 ./database_server.py

clean_pyc:
	rm -rf $(shell find * | grep pyc)

runapp:
	python3 ./server.py

jsrun:
	python3 judge-server.py