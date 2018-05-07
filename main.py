#!/usr/bin/env python3
from Utilities.FilePartition import make_partition, get_partition_range
from Conversation import Conversation
from time import strftime
from collectConversations import genericCommon as extractor
from Utilities.ProgressBar import display_progress_bar
import Utilities.ConvertDataType as conv
from twitter_apps.Keys import get_password
import psycopg2
import requests
import sys
import os
import json
import gzip


def main(**kwarg):
    baseURL = "https://twitter.com/user/status/"
    time_str = strftime("_%Y%m%d.dat")
    local_date = strftime("_%Y%m%d.html.gz")
    root_url = 'https://twitter.com/'

    db_account = kwarg['user']
    password = get_password(db_account)
    db = kwarg['db']

    print('\nMaking connection to <<{}>> DB ...'.format(db))
    dsn = "host={} dbname={} user={} password={}".format('localhost', db, db_account, password)
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    print('Connection successful ...')

    vmp_accounts = os.listdir(kwarg['tweet_path'])
    for k, account in enumerate(vmp_accounts):
        account = account.split('.')
        vmp_accounts[k] = account[0]

    vmp_accounts = list(set(vmp_accounts))
    vmp_accounts.sort()
    vmp_count = len(vmp_accounts)

    print('\nTotal number of VMPs: {}'.format(vmp_count))

    start = 0
    end = vmp_count

    if 'part' in kwarg:
        print('Partition: {}'.format(kwarg['part']))
        value = kwarg['part'].split('-')
        number_partitions = int(value[1])
        bloc_part = int(value[0])

        blocks = make_partition(vmp_count, number_partitions)
        work_range = get_partition_range(blocks, bloc_part)

        start = work_range[0]
        if len(work_range) == 1:
            end = vmp_count
        else:
            end = work_range[1]

        conversation_file = kwarg['path'] + 'Conversation_' + value[0] + '_' + value[1] + time_str

    else:
        conversation_file = kwarg['path'] + 'Conversation' + time_str

    if not os.path.isfile(conversation_file):
        f = open(conversation_file, mode='w')
        f.close()

    if 'rewrite' in kwarg:
        kwarg['rewrite'] = bool(kwarg['rewrite'])

    old_conversation = Conversation(conversation_file)

    print('Conversation will be recorded at: {}'.format(conversation_file))
    print('Capturing conversations from the Twitter VMP account {:,} to {:,} ...'.format(start + 1, end))
    print('\nObtaining available profiles ...')

    handle_files = os.listdir(kwarg['profile_path'])
    num_profiles = len(handle_files)
    for k, handle in enumerate(handle_files):
        display_progress_bar(25, k / num_profiles)
        handle_files[k] = handle[:handle.rfind('_')]
        sql = 'SELECT handle, status FROM profiles WHERE handle = \'{}\';'.format(handle_files[k])
        cur.execute(sql)
        if cur.rowcount < 1:
            sql = 'INSERT INTO profiles (handle, status) VALUES (\'{}\', {});'.format(handle_files[k], 2)
            cur.execute(sql)
            conn.commit()

    print('\nFound {:,} profiles'.format(num_profiles))
    del handle_files

    conversations_idx = set()
    vmp_tweetsID = []

    for counter, handle in enumerate(vmp_accounts):
        if start <= counter < end:
            try:
                for tweet_in in old_conversation.handle_conversations_id(handle):
                    conversations_idx.add(int(tweet_in))
                    sql = 'SELECT id, status FROM conversations WHERE id = \'{}\';'.format(tweet_in)
                    cur.execute(sql)
                    if cur.rowcount < 1:
                        sql = 'INSERT INTO conversations (id, status) VALUES (\'{}\', {});'.format(tweet_in, 0)
                        cur.execute(sql)
                        conn.commit()
            except KeyError:
                "No conversations were recorded for current handle"
                pass

            with gzip.open(kwarg['tweet_path'] + handle + '.twt.gz', mode='rb') as tweetIDFile:
                for records in tweetIDFile.read().decode('utf-8').split("\n"):
                    if records:
                        tweets = json.loads(records)
                        for tweet in tweets:
                            vmp_tweetsID.append(tweet['id'])

    rewriting = True
    conversations = []

    if 'rewrite' in kwarg and not kwarg['rewrite']:
        print('Not re-writing previous recorded conversations...')
        rewriting = False
        with open(conversation_file, mode='r') as inFile:
            for conversation in inFile:
                if conversation.strip() != '{}':
                    loaded_conversation = json.loads(conversation.strip())
                    conversations.append(loaded_conversation)

    with open(conversation_file, "w") as outFile:
        if not rewriting:
            for conversation in conversations:
                outFile.write(json.dumps(conversation))
                outFile.write("\n")

        for tweetID in vmp_tweetsID:
            sql = 'SELECT id, status FROM conversations WHERE id = \'{}\';'.format(tweetID)
            cur.execute(sql)
            if cur.rowcount < 1:
                sql = 'INSERT INTO conversations (id, status) VALUES (\'{}\', {});'.format(tweetID, 1)
                cur.execute(sql)
                conn.commit()

            if tweetID not in conversations_idx:
                print('Extracting conversation-id: {}'.format(tweetID))
                url = baseURL + str(tweetID)
                convoDict = extractor.extractTweetsFromTweetURI(tweetConvURI=url)
                outFile.write(json.dumps(convoDict))

                tmp_file = '/tmp/' + str(tweetID) + '.tmp'
                f = open(tmp_file, mode='w')
                f.write('{}\n'.format(json.dumps(convoDict)))
                f.close()
                capture_conv = Conversation(tmp_file)

                for handle in capture_conv.all_conversation_elements_set():
                    sql = 'SELECT handle, status FROM profiles WHERE handle = \'{}\';'.format(handle)
                    cur.execute(sql)
                    if cur.rowcount < 1:
                        sql = 'INSERT INTO profiles (handle, status) VALUES (\'{}\', {});'.format(handle, 1)
                        cur.execute(sql)
                        conn.commit()

                        profile_url = root_url + handle
                        print('Getting profile for Twitter account: {}'.format(profile_url))
                        r = requests.get(profile_url)

                        if r.status_code == 200:
                            print('\tWriting profile ...')
                            filename = kwarg['profile_path'] + handle + local_date
                            fh = gzip.open(filename, mode='wb')
                            fh.write(r.text.encode())
                            fh.close()
                        elif r.status_code == 302:
                            print('\tAccount was recently suspended ...')
                        elif r.status_code == 404:
                            print('\tAccount was deleted ...')
                        else:
                            print('\tEncountered unanticipated exception. Status:'.format(r.status_code))

                        sql = 'UPDATE profiles SET status = 2 WHERE handle = \'{}\';'.format(handle)
                        cur.execute(sql)
                        conn.commit()

                    else:
                        print('Skipping account {}. Already on file...'.format(handle))

                os.remove(tmp_file)
                outFile.write("\n")

                sql = 'UPDATE conversations SET status = 2 WHERE id = \'{}\';'.format(tweetID)
                cur.execute(sql)
                conn.commit()
            else:
                print('Skipping conversation-id: {} ...'.format(tweetID))


if __name__ == '__main__':
    """
    Parameters for the script are:
    :path: path to the file where capture conversations will be stored. The conversations will be uploaded into memory.
           This is a MANDATORY parameter.

    :tweet_path: path of folder where VMPs tweets are stored. This is a MANDATORY parameter.

    :profile_pah: path of folder where interacting profiles will be stored. This is a MANDATORY parameter.

           
    :db: name of database in use
    
    :user: user which has access to database.
    
    :part: this is an optional parameter. If provided, the list of interacting Twitter accounts will be broken in (n)
           parts. The parameter has the format d1-d2. Where d2 is an integer that represents the number of parts the list
           will be broken into. While d1 is the section that will be inspected.

           Ex: A conversation containing 100 handles could be broken in two pieces. Then, passing the parameter
               part=1-2 indicates that the running instance will work with elements 0-49. Another instance could run
               concurrently (part=2-2) to work elements 50-100.

    :rewrite: this is an optional parameter. This is parameter requires a boolean value. Possible values are True or False.
              The default value of this parameter is TRUE. If the values is FALSE and a conversation was recorded then 
              the script will load the file and it will skip any conversation that was included in the file.               

    running example: ./main.py part=1-10 path=data/verifiedUserDataset/ 
                     del_path=data/DeletedSuspendedAccounts/ profile_path=data/AccountProfiles/
    """
    if len(sys.argv) < 6:
        print('\nNot enough arguments..', file=sys.stderr)
        print('Usage: ./main.py path=path-to-conversations tweet_path=path-where-tweets-reside db=database-name ' +
              'user=database-user profile_path="path-to-profile-folder>', file=sys.stderr)
        sys.exit(-1)

    params = conv.list2kwarg(sys.argv[1:])

    if 'path' not in params or 'tweet_path' not in params or 'profile_path' not in params or 'db' not in params or \
       'user' not in params:
        print('\npath, profile_path, and tweet_path are MANDATORY parameters', file=sys.stderr)
        print('Usage: ./main.py path=path-to-conversations tweet_path=path-where-tweets-reside db=database-name ' +
              'user=database-user profile_path="path-to-profile-folder>', file=sys.stderr)
        sys.exit(-1)

    if not os.path.isdir(params['path']):
        print('\nCould not find folder where conversation will be stored: {}'.format(params['path']), file=sys.stderr)
        sys.exit(-1)

    if not os.path.isdir(params['tweet_path']):
        print('\nCould not find folder where VMPs tweets reside: {}'.format(params['tweet_path']), file=sys.stderr)
        sys.exit(-1)

    if not os.path.isdir(params['profile_path']):
        print('\nCould not find folder where profiles will be stored: {}'.format(params['profile_path']),
              file=sys.stderr)
        sys.exit(-1)

    # add / to end of folder path if not given
    if params['tweet_path'][-1] != '/':
        params['tweet_path'] = params['tweet_path'] + '/'

    if params['profile_path'][-1] != '/':
        params['profile_path'] = params['profile_path'] + '/'

    if params['path'][-1] != '/':
        params['path'] = params['path'] + '/'

    if 'part' in params:
        part = params['part'].split('-')
        if len(part) != 2:
            print('\nParameter <part> MUST have two integers between a dash. Ex: part=1-10', file=sys.stderr)
            sys.exit(-1)

        try:
            value0 = int(part[0])
            value1 = int(part[1])

        except ValueError:
            print('\nParameter <part> MUST have two integers between a dash. Ex: part=1-10', file=sys.stderr)
            sys.exit(-1)

    if 'rewrite' in params:
        if params['rewrite'].lower() not in ['false', 'true', '1', '0']:
            print('\nParameter <rewrite> possible values are: True, False, 0, or 1', file=sys.stderr)
            sys.exit(-1)
        elif params['rewrite'].lower() in ['false', '0']:
            params['rewrite'] = ''
    else:
        params['rewrite'] = ''

    main(**params)

    sys.exit(1)
