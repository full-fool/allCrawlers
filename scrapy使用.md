##scrapy使用
1. 新建项目:scrapy startproject (projectname)，会生成一系列文件，
scrapy.cfg: 项目的配置文件
tutorial/: 该项目的python模块。之后您将在此加入代码。
tutorial/items.py: 项目中的item文件.
tutorial/pipelines.py: 项目中的pipelines文件.
tutorial/settings.py: 项目的设置文件.
tutorial/spiders/: 放置spider代码的目录.
2. Item 是保存爬取到的数据的容器；其使用方法和python字典类似， 并且提供了额外保护机制来避免拼写错误导致的未定义字段错误。
3. 为了创建一个Spider，您必须继承 scrapy.Spider 类， 且定义以下三个属性:name(用于区别Spider。 该名字必须是唯一的，您不可以为不同的Spider设定相同的名字。),start_urls(包含了Spider在启动时进行爬取的url列表。 因此，第一个被获取到的页面将是其中之一。 后续的URL则从初始的URL获取到的数据中提取。),parse()(是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 该方法负责解析返回的数据(response data)，提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。)
4. 爬虫的运行：在 根目录下键入scrapy crawl dmoz，其中dmoz为spider中定义的name。即上一步中的name。
4. 从网页中提取数据有很多方法。Scrapy使用了一种基于 XPath 和 CSS 表达式机制: Scrapy Selectors 。 关于选择器<http://scrapy-chs.readthedocs.org/zh_CN/latest/topics/selectors.html#topics-selectors>.XPath的文档：<http://www.w3school.com.cn/xpath/index.asp>。几个例子：/html/head/title: 选择HTML文档中 \<head\> 标签内的 \<title\> 元素，/html/head/title/text(): 选择上面提到的 \<title\> 元素的文字, //td: 选择所有的 \<td\> 元素,//div[@class="mine"]: 选择所有具有 class="mine" 属性的 div 元素
5. 为了配合XPath，Scrapy除了提供了 Selector 之外，还提供了方法来避免每次从response中提取数据时生成selector的麻烦。
6. Selector有四个基本的方法，
	* xpath(): 传入xpath表达式，返回该表达式所对应的所有节点的selector list列表 。
	* css(): 传入CSS表达式，返回该表达式所对应的所有节点的selector list列表.
	* extract(): 序列化该节点为unicode字符串并返回list。
	* re(): 根据传入的正则表达式对数据进行提取，返回unicode字符串list列表。
7. Item 对象是自定义的python字典。 您可以使用标准的字典语法来获取到其每个字段的值。
8. 使用内置的Scrapy shell：进入项目根目录，键入scrapy shell "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/"，（必须预装ipython）
9. 包含yield语句的函数会被特地编译成生成器。当函数被调用时，他们返回一个生成器对象，这个对象支持迭代器接口。函数也许会有个return语句，但它的作用是用来yield产生值的。不像一般的函数会生成值后退出，生成器函数在生成值后会自动挂起并暂停他们的执行和状态，他的本地变量将保存状态信息，这些信息在函数恢复时将再度有效
10. 保存爬取到的数据：scrapy crawl dmoz -o items.json。