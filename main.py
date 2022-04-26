import time, random, uuid
from pylsl import StreamInfo, StreamOutlet

info = StreamInfo(name='Test', 
                type = 'MyType', 
                channel_count = 20,
                nominal_srate=100,          #   if irregular sample, nominal_srate = 0
                channel_format='float32',   #   TODO only numbers can be transmitted 
                source_id=str(uuid.uuid1()))     #   TODO add python unique id

outlet = StreamOutlet(info)



if __name__ == "__main__":
    print("now sending data...")
    while True:
        mysample = [time.time(), random.random(), random.random(), random.random(),random.random(),random.random(),
                    random.random(), random.random(), random.random(),random.random(),random.random(), random.random(),
                    random.random(), random.random(), random.random(), random.random(), random.random(), random.random()
                    , random.random(), random.random()]
        # now send it and wait for a bit
        outlet.push_sample(mysample)
        time.sleep(0.001)
