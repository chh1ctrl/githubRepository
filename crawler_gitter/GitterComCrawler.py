# Copyright (C) <2020> <Esteban Parra>
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import random
import time
import requests
import sys
import os
import pycurl
import json
from io import BytesIO
import datetime
import certifi


def main(token, filename):
    with open(filename, 'r') as inputfile:
        for line in inputfile:
            l = line.replace("https://gitter.im/", "")  # Remove url header
            l = l.replace("\n", "")  # Remove newline
            print(l)
            chatRoomURI = l
            print("URI is: {}".format(chatRoomURI))
            room_id = getRoomIdByURI(token, chatRoomURI)
            getMessagesOutputToFile(token, chatRoomURI, room_id)
            print('End ', chatRoomURI)


def getRoomIdByURI(token, chatRoomURI):
    myBuffer = BytesIO()

    headers = ['Authorization: Bearer {}'.format(token),
               'Content-Type: application/json',
               'Accept: application/json']

    curlConnect = pycurl.Curl()
    curlConnect.setopt(pycurl.CAINFO, certifi.where())
    curlConnect.setopt(pycurl.URL, 'https://api.gitter.im/v1/rooms')
    curlConnect.setopt(pycurl.POST, 1)
    curlConnect.setopt(pycurl.HTTPHEADER, headers)
    curlConnect.setopt(pycurl.POSTFIELDS, json.dumps({'uri': '{}'.format(chatRoomURI)}))
    curlConnect.setopt(pycurl.WRITEDATA, myBuffer)
    curlConnect.perform()

    print(curlConnect.getinfo(pycurl.HTTP_CODE))
    # --> 200
    print(curlConnect.getinfo(pycurl.EFFECTIVE_URL))
    # --> "https://www.python.org/"
    certinfo = curlConnect.getinfo(pycurl.INFO_CERTINFO)
    print("certinfo: {} ".format(certinfo))

    curlConnect.close()
    body = json.loads(myBuffer.getvalue().decode())
    room_id = body['id']
    print("{} room id:".format(chatRoomURI), room_id)
    return room_id


def getMessagesOutputToFile(token, chatRoomURI, room_id):
    try:
        os.makedirs(chatRoomURI)
    except FileExistsError as e:
        print(e)
        pass

    consecutiveRequests = 0
    messages = []
    messageIds = []

    with open("{}/all_messagesData_Json.json".format(chatRoomURI), 'w') as fullFile:
        fullFile.write('[')
        r = requests.get("https://api.gitter.im/v1/rooms/{}/chatMessages?access_token={}".format(room_id, token))
        output = [{"message_id": x['id'], "timestamp": x['sent'], "username": x['fromUser']['username'],
                   "message_text": x['text']} for x in r.json()]
        try:
            old_id = output[0]["message_id"]
            for x in r.json():
                if x['id'] not in messageIds:
                    messageIds.append(x['id'])
                    messages = [x] + messages
                    fullFile.write(json.dumps(x, indent=4))
                    fullFile.write(',')
            # print(x['id'])
            new_id = 0
            while old_id != new_id:
                try:
                    old_id = output[0]['message_id']
                except IndexError:
                    break
                # print("Downloading messages before message id: ", old_id)
                r = requests.get(
                    "https://api.gitter.im/v1/rooms/{}/chatMessages?beforeId={}&access_token={}".format(room_id, old_id,
                                                                                                        token))
                consecutiveRequests += 1
                if consecutiveRequests == 30:
                    delays = [207, 134, 60, 128, 100, 329, 99]
                    delay = random.choice(delays)
                    print('Sleeping for {} seconds at {}'.format(delay, datetime.datetime.now()))
                    time.sleep(delay)
                    consecutiveRequests = 0
                for x in r.json():
                    try:
                        if x['id'] not in messageIds:
                            messageIds.append(x['id'])
                            messages = [x] + messages
                            fullFile.write(json.dumps(x, indent=4))
                            fullFile.write(',')
                            # print(x['id'])
                            try:
                                if 'fromUser' in x.keys():
                                    output = [{"message_id": x['id'], "timestamp": x['sent'],
                                               "username": x['fromUser']['username'],
                                               "message_text": x['text']}] + output
                                else:
                                    output = [{"message_id": x['id'], "timestamp": x['sent'], "username": 'N/A',
                                               "message_text": x['text']}] + output
                            except AttributeError:
                                print("Error on: \n", x)
                            except TypeError:
                                print("Type Error:\n", r.json())
                            except KeyError:
                                print("Key Error:\n", r.json())
                        else:
                            pass
                    # print("-->{}".format(x['id']))
                    except TypeError:
                        print("Type Error:\n", r.json())

                if len(output) > 0:
                    new_id = output[0]["message_id"]
        except IndexError:
            print("Index error")
        fullFile.write(']')
    with open("{}/all_messages.json".format(chatRoomURI), 'w') as outfile:
        outfile.write(json.dumps(output, indent=4))
        print(outfile)
    with open("{}/all_messagesFull.json".format(chatRoomURI), 'w') as outfile:
        outfile.write(json.dumps(messages, indent=4))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("USAGE: python3.x <auth token> <filename>")
        # sys.exit()
        token = 'HARDCODED TOKEN'
        filename = sys.argv[1]
    else:
        token = sys.argv[1]
        filename = sys.argv[2]
    print(filename)
    main(token, filename)
