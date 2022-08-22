import sys
import json
import spacy
import pandas as pd
import traceback
from tqdm import tqdm

nlp = spacy.load('en_core_web_sm')

names_set = set()

file_names = [".annotation.txt", ".ascii.txt", ".raw.txt", ".tok.txt"]

def process(filename):
    data_list = []
    with open(filename + '/content.annotation.txt', 'w+') as file:
        pass
    csv_file = filename + '/content.raw.txt'
    with open(filename + '/all_messagesFull.json', 'r') as inputfile:
        with open(csv_file, 'w+', encoding='utf-8') as outfile:
            outfile.write('id\ttext\ttime\tmentions\n')
            js = json.loads(inputfile.read())
            for node in js:
                try:
                    id = node['id']
                    text = node['text']
                    text = text.replace('\t', ' ')
                    text = text.replace('\n', ' ')
                    text = text.replace('\r', ' ')
                    time = node['sent']
                    username = node['fromUser']['username']
                    all_mention = []
                    all_mention_txt = ''
                    mentions = node['mentions']
                    for mention in mentions:
                        all_mention.append(mention['screenName'])
                        all_mention_txt = all_mention_txt + ';' + mention['screenName']

                    data_list.append([time, username, text, id])

                    names_set.add(str.lower(username))
                except:
                    pass
            data_list = sorted(data_list, key=lambda x: x[0], reverse=False)
            for line in data_list:
                outfile.write('[' + line[0] + ']\t<' + line[1] + '>\t' + line[2] + '\n')  # '\t' + line[3] +
        print(mentions)


#out = pd.read_csv(csv_file, sep='\t')


def process_ascii(filename):
    with open(filename + '/content.ascii.txt', 'w', encoding='utf-8') as outputfile:
        with open(filename + '/content.raw.txt', 'r', encoding='utf-8') as inputfile:
            lines = inputfile.readlines()
            for line in tqdm(lines, total=len(lines)):
                # if not line.strip():
                #	continue
                values = line.split('\t')
                time = values[0]
                name = values[1]
                text = values[2]
                id = values[3]
                id = id.replace('\n', '')
                doc = nlp(str.lower(text))
                sent = ''
                for token in doc:
                    print('"' + token.text + '"')
                    if token.text.isalpha():
                        token_text = token.text
                        if token_text in names_set:
                            sent += ' <user> '
                            continue
                        sent += str.lower(token.lemma_) + ' '
                outputfile.write(time + '\t' + name + '\t' + sent + '\t' + id + '\n')


def process_tok(filename):
    with open(filename + '/content.tok.txt', 'w', encoding='utf-8') as outputfile:
        with open(filename + '/content.ascii.txt', 'r', encoding='utf-8') as inputfile:
            lines = inputfile.readlines()
            for line in lines:
                line = line.replace('\n', '')
                values = line.split('\t')
                text = values[2]
                text = '<s> ' + text + ' </s>'
                outputfile.write(text + '\n')


def main(filename):
    with open(filename, 'r') as inputfile:

        for line in inputfile:
            l = line.replace("https://gitter.im/", "")  # Remove url header
            l = l.replace("\n", "")  # Remove newline
            l = 'data/gitter/' + l
            print(l)
            try:
                process(l)
                process_ascii(l)
                process_tok(l)
            except Exception as e:
                print('exception', traceback.print_exc())


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("USAGE: python3.x <filename>")
        # sys.exit()
        token = 'HARDCODED TOKEN'
        filename = sys.argv[1]
        main(filename)
