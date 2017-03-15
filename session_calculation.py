import datetime
import time
import json

class Headers:
    def __init__(self, ai5, debug, random, sdkv):
        self.ai5 = ai5
        self.debug = debug
        self.random = random
        self.sdkv = sdkv
    def get_headers(json_string):
        json_ = json.loads(json_string)
        return Headers(**json_)

class Post:
    def __init__(self, event, ts):
        self.event = event
        self.ts = ts
    def get_post(json_string):
        json_ = json.loads(json_string)
        return Post(**json_)  

class Bottle:
    def __init__(self, timestamp, game_id):
        self.timestamp = timestamp
        self.game_id = game_id
        self.timestamp_in_seconds = to_sec(timestamp)
    def get_bottle(json_string):
        json_ = json.loads(json_string)
        return Bottle(**json_)

class Instance:
    def __init__(self, headers, post, bottle):
        self.headers = headers
        self.post = post
        self.bottle = bottle
    def get_instance(json_string):
        json_ = json.loads(json_string)
        headers = Headers.get_headers(json.dumps(json_["headers"]))
        post = Post.get_post(json.dumps(json_["post"]))
        bottle = Bottle.get_bottle(json.dumps(json_["bottle"]))
        return Instance(headers, post, bottle)

class Session:
    def __init__(self, ai5, val_sessions, tot_sessions, avg_session_time):
        self.ai5 = ai5
        self.val_sessions = val_sessions
        self.tot_sessions = tot_sessions
        self.avg_session_time = avg_session_time
    def to_json(self):
        return json.dumps(self.__dict__)

def read_json():
    user_map = {}
    with open('/home/shubham/Downloads/ggevent/ggevent.json') as infile:
        file = infile.readlines()
    for line in file:
        instance = Instance.get_instance(line)
        users_instances = user_map.get(instance.headers.ai5, [])
        users_instances.append(instance)
        user_map[instance.headers.ai5] = users_instances
    return user_map

def gaming_sessions(user_ins):
    sessions = []
    for ai5, instances in user_ins.items():
        instances.sort(key=lambda x: x.bottle.timestamp_in_seconds)
        flag = True
        start = None  
        prev = None  
        end = None  
        tot_sessions = 0  
        val_sessions = 0  
        total_time = 0  
        for instance in instances:
            if flag:
                if instance.post.event == "ggstart":
                    prev = start = instance
                    flag = False
                continue
            diff = instance.bottle.timestamp_in_seconds - prev.bottle.timestamp_in_seconds
            
            if prev.post.event == "ggstart" and instance.post.event == "ggstop":
                prev = end = instance
            elif diff > 30:  
                if prev.post.event == instance.post.event == "ggstop":
                    flag = True
                elif prev.post.event == "ggstop" and instance.post.event == "ggstart":
                    prev = start = instance
                elif prev.post.event == "ggstart" and instance.post.event == "ggstart":
                    prev = start = instance
                if end:
                    session_time = end.bottle.timestamp_in_seconds - start.bottle.timestamp_in_seconds
                
                if session_time >= 60:
                    val_sessions += 1
                    total_time += session_time
                
                if session_time > 1:
                    tot_sessions += 1

            if val_sessions !=0:
                average_session_time= total_time/val_sessions
            else:
                average_session_time=0
        sessions.append(
            Session(ai5, val_sessions, tot_sessions,average_session_time))
    return sessions
    

def to_sec(time_):
    datetime_format = "%Y-%m-%d %H:%M:%S.%f"
    strptime = datetime.datetime.strptime(time_, datetime_format)
    return int(time.mktime(strptime.timetuple()))

if __name__ == '__main__':
    user_ins = read_json()
    sessions = gaming_sessions(user_ins)
    with open('/home/shubham/session_calculation_output.txt', "w") as fp:
        for session in sessions:
            fp.write(session.to_json() + "\n")
