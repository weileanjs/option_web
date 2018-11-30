#-*-coding:UTF-8-*-
import os
import time,datetime
from .to_mysql import get_tot_crawlers,update_crawler_status

def now():
    timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return timenow

def monitoring_spider(spiderD):
    # 监控爬虫状态
    format_name = '[{}]{}'.format(spiderD['CRAWLER_NAME'][:1],spiderD['CRAWLER_NAME'][1:])   # 构造查询爬虫名  spider-> [s]pider
    r = "ps -ef | awk '/%s/{print $2}'"%(format_name)                                        # LINUX 根据爬虫名查询 pid
    processList = os.popen(r)
    process_pid_list = [int(i.strip()) for i in processList]
    if len(process_pid_list) > 0 and spiderD['STATUS']==1:
        pass
    elif len(process_pid_list) > 0 and spiderD['STATUS'] != 1:
        # `STATUS`={},UPDATETIME={} WHERE ID
        updateTime = now()
        update_crawler_status(1,updateTime,spiderD['ID'])
    elif len(process_pid_list) == 0 and spiderD['STATUS'] == 1:
        updateTime = now()
        update_crawler_status(0,updateTime,spiderD['ID'])
    elif len(process_pid_list) == 0 and spiderD['STATUS'] == 0:
        pass
    return process_pid_list

def stop_spider(spiderD):
    spider_pid_list = monitoring_spider(spiderD)
    for pid in spider_pid_list:
        # print('kill {}'.format(pid))
        os.popen("kill -9 {}".format(pid))
    monitoring_spider(spiderD)

def start_spider(spiderD):
    # 若当前爬虫已存在，kill当前爬虫，再启动
    if len(monitoring_spider(spiderD)) > 0:
        stop_spider(spiderD)
    command = "nohup python3 -u {}/{}.py > {}.out 2>&1 &".format(spiderD['CRAWLER_PATH'],spiderD['CRAWLER_NAME'],spiderD['CRAWLER_NAME'])
    print(command)
    os.popen(command)
    time.sleep(2)
    monitoring_spider(spiderD)




def master_monitor():
    spiders = get_tot_crawlers()
    for spiderDict in spiders:
        print(spiderDict)
        monitoring_spider(spiderDict)




# if __name__ == '__main__':
#     # monitoring_spider('crawler_test1')
#     # master_monitor()
#     stop_spider({'ID': 1, 'CRAWLER_MANAGE_ID': 3, 'CRAWLER_NAME': 'crawler_test1', 'STATUS': 1, 'CRAWLER_PATH': '/data/python_crawler/test_crawler_manage'})
#     # start_spider({'ID': 1, 'CRAWLER_MANAGE_ID': 3, 'CRAWLER_NAME': 'crawler_test1', 'STATUS': 0, 'CRAWLER_PATH': '/data/python_crawler/test_crawler_manage'})
