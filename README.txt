在当前目录运行命令：
scrapy crawl jingjunews -a mdate=2017-3-20 -o out.json -t json

mdate参数为上次爬取数据的日期，爬取结果保存在out.json中，追加在文件最后。