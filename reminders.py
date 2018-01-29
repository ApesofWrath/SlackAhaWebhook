#! /usr/bin/env python3

# Aha! webhook for Slack
# Cody King
# 1/27/2018


import sys
from urllib import request, parse
import requests, json
from datetime import date, datetime, timedelta
import time



def main():
    run()


# Check that number of days has been given
# call method to post message to Slack
def run():
    if len(sys.argv) != 2:
        print('Usage: ./bot.py (time in days)')
        sys.exit(2)

    else:
        send_message_to_slack(sys.argv[1])
        print('Success.')


# Posting to Slack channel
def send_message_to_slack(days):
    # Get upcoming tasks from Aha!
    slack_message = getFeatures(days)


    text = 'Here are the features with deadlines less than {} days away:{}'.format(days, ''.join(slack_message))
    post = {"text": "{0}".format(text)}

    try:
        json_data = json.dumps(post)

        req_sched = request.Request(get_url('apes_sched'),
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'})

        req_gen = request.Request(get_url('apes_gen'),
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'})

        resp1 = request.urlopen(req_sched)
        resp2 = request.urlopen(req_gen)
    except Exception as em:
        print("EXCEPTION: " + str(em))


# fetches features from Aha!
# returns features that are due with in <days> days
def getFeatures(days):
    # Get all features (doesn't have due dates, but we can pull IDs)
    response_features = requests.get('https://secure.aha.io/api/v1/features/?per_page=100', headers=getHeaders())
    data = response_features.json()

    # get reference_nums of all features
    reference_nums = []
    names = []
    for i in range(len(data.get('features'))):
        reference_nums.append(data.get('features')[i].get('reference_num'))
        names.append(data.get('features')[i].get('name'))

    # using the reference_nums, fetch features and extract the due date and release name
    due_dates = []
    release_names = []
    for i in range(len(names)):
        response_indiv = requests.get('https://secure.aha.io/api/v1/features/{}'.format(reference_nums[i]), headers=getHeaders())
        data = response_indiv.json()
        due_dates.append(data.get('feature').get('due_date'))
        release_names.append(data.get('feature').get('release').get('name'))

    # composes message to be returned
    slack_message = []
    for i in range(len(names)):
        if is_upcoming(due_dates[i], days):
            slack_message.append('\n{}, {} ({})'.format(release_names[i], names[i], due_dates[i]))

    # api call return code
    print(response)

    return slack_message


# returns true if <date> is within <days> days from now
def is_upcoming(date, days):
    vals = date.split('-')
    today = time.localtime()
    date_format = "%Y/%m/%d"
    a = datetime.strptime('{}/{}/{}'.format(vals[0], vals[1], vals[2]), date_format)
    b = datetime.strptime('{}/{}/{}'.format(today[0], today[1], today[2]), date_format)
    delta = a - b

    num_days = delta / timedelta (days=1)

    if num_days <= int(days) and num_days >= 0:
        return True

    else:
        return False


# fetches webhook url, api keys, etc.
def get_url(index):
    with open('stuff.txt') as f:
        content = f.readlines()

    if index == 'king_testing':
        return content[7].rstrip('\n')

    if index == 'apes_sched':
        return content[10].rstrip('\n')

    if index == 'apes_gen':
        return content[13].rstrip('\n')

    if index == 'aha_api_key':
        return content[16].rstrip('\n')


# headers for Aha! api call
def getHeaders():
    return {
        'Authorization': 'Bearer {}'.format(get_url('aha_api_key')',
        'X-Aha-Account': 'apesofwrath668',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


if __name__ == '__main__':
    main()
