用python爬取384个美国城市就业信息

文件说明：
Bureau_of_Labor_Statistics_Data.html 查询结果的html文件
cities.txt 城市名称和对应州的缩写
citiCodes.txt 查询号码，由三部分组成：success codes是查找成功的城市（333个），fail to find city是在对应州网站查不到信息的城市（1个），fail to find the manufacturing data是能查到该城市，但该城市没有manufacturing的数据（50个）
data.xls 查询结果的excel汇总表
main.py 爬虫代码
states.txt 州缩写对应的全称
statesAndCity 城市以及对应州的全称

运行说明：
1. getCities() 从wiki获取城市信息和对应州的简称，保存在cities.txt
2. getStateCity() 把州简称转化为全称，保存在statesAndCity.txt
3. getStatePage() 从州对应网站，查询城市manufacturing对应的编号
4. getSimilarCity() 一些名字很长的城市在州网站查不到，就取一些名字相似的城市
5. extractTable() 从查询结果的html文件中抽出333个表，写入一个excel

