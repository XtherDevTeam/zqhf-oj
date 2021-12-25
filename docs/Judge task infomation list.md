## 基本任务明细List的解释

现在我们有
```python
["Judging","Please wait...",now_item[5],now_item[6]]
```
不难看出第一个是Status

第二个则是stdout

仔细观察now_item的结构即可发现5,6分别是author和pid

完整版解释
```python
[status, stdout, author, pid]
```

**但是**！最终的result却不同于task，相比之下他多了一个stderr

所以说result的结构为
```python
[status, stdout, stderr, author, pid]
```