import redis
from config import REDIS_CONFIG
class opition2redis():
    def __init__(self,):
        pool = redis.ConnectionPool(host = REDIS_CONFIG['host'], port = REDIS_CONFIG['port'],
                                    db=REDIS_CONFIG['db'],password=REDIS_CONFIG['password'])
        self.redis = redis.Redis(connection_pool = pool)
    def insert_hash(self, key, value):
        self.redis.hmset(key, value)

    def read_hash(self,key):
        info = self.redis.hgetall(key)
        info_decode = {}
        for k,v in info.items():
            info_decode[k.decode('utf8')] = v.decode('utf8')
        return info_decode

    def total_keys(self):
        keys = [i.decode('utf8') for i in self.redis.keys()]
        return keys

    def format_keys(self):
        key_list = self.total_keys()
        months = list(set([key.split('M')[0].replace('CALL','').replace('PUT','') for key in key_list]))
        ex_prices = list(set([key.split('M')[1].replace('CALL','').replace('PUT','') for key in key_list]))
        months.sort()
        ex_prices.sort()
        return months,ex_prices
    def flush_db(self,):
        self.redis.flushdb()

# if __name__ == '__main__':
#     foo = opition2redis()
#     foo.format_keys()
#     foo.total_keys()
#     # foo.read_hash('50ETFPUT3M2250')
#     # foo.flush_db()
#     print(opition2redis().read_hash('50ETFPUT3M2250'))
