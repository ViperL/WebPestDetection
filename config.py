#----配置数据库连接参数----#
HostName="127.0.0.1"
Port = 3306                     #默认为3306，需要自行修改
UserName=""                     #登录用户名，一般为root
Password=""                     #登录密码
DataBase=""                     #数据库库名

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{UserName}:{Password}@{HostName}:{Port}/{DataBase}?charset=utf8mb4"

SECRET_KEY = ''       #用于session加密的密钥,随便写一个就行了
