import requests
import argparse
import json

import sched, time

from pathlib import Path

def send_request(url, sample):
    print("sending request: %s at time: %f" % (sample,  time.time()))
    return requests.post(url, data=sample)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="send sample requests to a target api endpoint")
    parser.add_argument("target_url", type=str, help="endpoint url")
    parser.add_argument("sample_path", type=str, help="path to test requests")
    parser.add_argument("-r", "--rate", type=float, help="rate at which to send requests, in Hz", default=1.0)

    args = parser.parse_args()
    sample_path = Path(args.sample_path)

    sample_strings = None
    scheduler = sched.scheduler(time.time, time.sleep)

    delay = (1.0 / args.rate)

    with open(sample_path) as sample_file:
        sample_strings = sample_file.readlines()

    for test_sample in sample_strings:
        scheduler.enter(delay, 1, send_request, argument=(args.target_url, test_sample))
        scheduler.run()


    
