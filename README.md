# 豆瓣读书封面获取器

一个简单的Python工具，用于根据书名获取豆瓣读书上最新出版版本的书籍封面（缩略图和高清图）。

## 功能特点

- 🔍 根据书名搜索豆瓣书籍
- 📚 获取书籍详细信息（标题、作者、出版社、出版日期）
- 🖼️ 下载多种尺寸的封面图片（缩略图、中等尺寸、高清图）
- 💾 自动创建目录并保存文件
- 📄 保存书籍信息为JSON格式

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 使用默认书籍（活着）

```bash
python douban_book_cover.py
```

### 2. 指定书名

```bash
python douban_book_cover.py "三体"
```

### 3. 交互式输入

```bash
python douban_book_cover.py
# 然后按提示输入书名
```

## 输出文件

程序会在 `covers/` 目录下创建以书名命名的文件夹，包含：

- `small.jpg` - 缩略图封面
- `medium.jpg` - 中等尺寸封面  
- `large.jpg` - 高清封面
- `book_info.json` - 书籍详细信息

## 示例输出

```
豆瓣读书封面获取器
==================================================
正在搜索书籍: 活着

找到书籍:
标题: 活着
作者: 余华
出版社: 作家出版社
出版日期: 2012-8-1

正在下载封面到目录: covers/活着
✓ 缩略图下载成功
✓ 中等尺寸下载成功
✓ 高清图下载成功
✓ 书籍信息已保存: covers/活着/book_info.json

所有文件已保存到: covers/活着

封面URL:
缩略图: https://img9.doubanio.com/view/subject/s/public/s29053580.jpg
中等尺寸: https://img9.doubanio.com/view/subject/m/public/s29053580.jpg
高清图: https://img9.doubanio.com/view/subject/l/public/s29053580.jpg
```

## 注意事项

- 程序使用豆瓣的公开API和搜索功能
- 请遵守豆瓣的使用条款，不要频繁请求
- 如果搜索失败，请检查网络连接或稍后重试
- 封面图片版权归原作者和出版社所有

## 错误处理

程序包含完善的错误处理机制：
- 网络请求超时处理
- 无效URL处理
- 文件保存错误处理
- JSON解析错误处理

