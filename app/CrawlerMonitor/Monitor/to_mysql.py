#-*-coding:UTF-8-*-
import pymysql
from .config import MYSQL_CONFIG
from .Log_Info.error_output import logError

connection = pymysql.connect(host=MYSQL_CONFIG['host'], port=MYSQL_CONFIG['port'], user=MYSQL_CONFIG['user'], password=MYSQL_CONFIG['password'],
                             db=MYSQL_CONFIG['db'],charset=MYSQL_CONFIG['charset'], cursorclass=pymysql.cursors.DictCursor)



def get_tot_crawlers():
    try:
        connection.ping()
    except:
        connection.ping(True)
    tot = []
    try:
        sql = "SELECT `ID`, `CRAWLER_MANAGE_ID`, `CRAWLER_NAME`, `STATUS` ,`CRAWLER_PATH`  FROM crawler_monitor"
        cursor = connection.cursor()
        cursor.execute(sql)
        tot = cursor.fetchall()
        # print(tot)
    except Exception as e:
        print('{} ERROR : {}'.format(__name__,str(e)))
        logError('{} ERROR : {}'.format(__name__,str(e)))
    finally:
        connection.close()
        return tot

# get_tot_crawlers()

def update_crawler_status(*args):
    try:
        connection.ping()
    except:
        connection.ping(True)
    try:
        sql = "UPDATE crawler_monitor SET `STATUS`={},UPDATETIME='{}' WHERE ID = {}".format(args[0],args[1],args[2])
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    except Exception as e:
        print('{} ERROR : {}'.format(__name__,str(e)))
        logError('{} ERROR : {}'.format(__name__,str(e)))
    finally:
        connection.close()

