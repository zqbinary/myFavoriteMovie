
## 项目
需要分析我看过的电影，暂时是为了拿到数据，筛选出2010-2019年之间十佳的电影。
标准随便写的



## 基本模块
* 登录
* 遍历我看过的电影列表，生成数据库记录
* 遍历数据库，取电影详情页，更新记录


## env 
- 数据库
- douban 账号密码


## 环境
- python3 需要安装一些依赖包，各种麻烦，具体问题具体谷歌。
- 因为我的是mac，python2.7 python3.7 共存，后来用pyenv 解决；
- 接着是 openssl 的问题。

##  database table structure
```
-- ----------------------------
-- Table structure for favorite_movie
-- ----------------------------
DROP TABLE IF EXISTS `favorite_movie`;
CREATE TABLE `favorite_movie` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  `rate` decimal(5,2) DEFAULT NULL,
  `title` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `director` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `tags` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `country` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `minutes` decimal(10,2) DEFAULT NULL,
  `my_date` datetime DEFAULT NULL,
  `my_rate` decimal(5,2) DEFAULT NULL,
  `my_comment` text COLLATE utf8mb4_bin,
  `my_tags` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `saw_times` int(11) DEFAULT NULL,
  `info` text COLLATE utf8mb4_bin,
  `year` smallint(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1188 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

```

## 筛选 SQL
````
SELECT url,concat(title,' ',year),my_date,rate,my_rate,my_tags,saw_times FROM favorite_movie WHERE 1
and rate>=8
and my_rate>=4
and title not like '%季%'
and my_tags not like '%韩剧%'
and my_tags not like '%日剧%'
and my_tags not like '%美剧%'
and year>=2010
and saw_times>100000
order by year desc,saw_times desc
````

## TODO...
* 登录模块，验证码交互;
* 一个ip在不登录的情况下，可以抓取500个条目左右。需要ip池；





