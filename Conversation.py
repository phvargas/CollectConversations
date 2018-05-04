import os
import sys
import json


class Conversation:
    def __init__(self, conversation_filename):
        self.conversations = {}

        self.counter = 0

        if os.path.isfile(conversation_filename):
            self.load_conversations(conversation_filename)
        else:
            print("Could not find file: {}".format(conversation_filename), file=sys.stderr)
            exit(-1)

        try:
            self.max_number_conversations = max([len(self.handle_conversations_id(x))
                                                 for x in self.conversations])
        except ValueError:
            self.max_number_conversations = []

    def load_conversations(self, filename):
        with open(filename, "r", encoding='iso-8859-1') as fs:
            for record in fs:
                if record.strip() != '{}':
                    loaded_conversation = json.loads(record.strip())
                    conversation_block = {'interactions': []}

                    # gets the Twitter Conversation-ID from the thread
                    for _idx in loaded_conversation:
                        conversation_idx = loaded_conversation[_idx]['data-conversation-id']
                        conversation_block['data-conversation-id'] = conversation_idx
                        break

                    # separate root from response conversations
                    for _idx in loaded_conversation:
                        # print('{}: {}'.format(_idx, loaded_conversation[_idx]))

                        # check if conversation-id is the root
                        if loaded_conversation[_idx]['data-conversation-id'] == _idx:
                            conversation_block['data-screen-name'] = loaded_conversation[_idx][
                                'data-screen-name'].lower()
                            conversation_block['tweet-time'] = loaded_conversation[_idx]['tweet-time']
                            conversation_block['tweet-text'] = loaded_conversation[_idx]['tweet-text']
                        else:
                            conversation_block['interactions'].append({
                                'data-tweet-id': loaded_conversation[_idx]['data-tweet-id'],
                                'data-screen-name': loaded_conversation[_idx]['data-screen-name'].lower(),
                                'tweet-time': loaded_conversation[_idx]['tweet-time'],
                                'tweet-text': loaded_conversation[_idx]['tweet-text']
                            })

                    if 'data-screen-name' in conversation_block and conversation_block['data-screen-name'] in self.conversations:
                        self.conversations[conversation_block['data-screen-name']][conversation_idx] = {
                            'tweet-time': conversation_block['tweet-time'],
                            'tweet-text': conversation_block['tweet-text'],
                            'interactions': conversation_block['interactions']
                        }
                    elif 'data-screen-name' in conversation_block:
                        self.conversations[conversation_block['data-screen-name']] = {
                            conversation_idx: {
                                'tweet-time': conversation_block['tweet-time'],
                                'tweet-text': conversation_block['tweet-text'],
                                'interactions': conversation_block['interactions']
                            }
                        }
                    else:
                        self.counter += 1

        return

    def handle_conversations_id(self, handle):
        """
        finds accounts interacting in an observed conversation for a given Twitter handle. Some accounts may be
        interacting more than once in the conversation

        :param handle: Twitter handle of observed accounts
        :return: a vector containing tweets data-conversation-id from all conversations observed by a given
                 Twitter handle.
                 Ex: ['891800580842246145', '891809774769254404', '924629283447955462', '914822313799045120']
        """
        return [x for x in self.conversations[handle.lower()]]

    def handle_total_responses(self, handle):
        """
        Provides the sum of all responses to all observed tweets made by a given Twitter handle

        :param handle: Twitter handle of an observed account
        :return: number of tweeted responses. Ex: 24
        """
        return sum(self.conversation_response_vector(handle))

    def conversation_response_vector(self, handle):
        """
        Provides the sum of all responses per conversation initiated by an observed Twitter handle

        :param handle: Twitter handle of an observed account
        :return: list of number of responses. Ex: [10, 20, 0, 11, 99]
        """
        return [len(self.conversations[handle][x]['interactions']) for x in self.conversations[handle]]

    def conversation_elements_list(self, handle, conversation_id):
        """
        finds accounts interacting in an observed conversation for a given Twitter handle. Some accounts may be
        interacting more than once in the conversation

        :param handle: Twitter handle of observed accounts
        :param conversation_id: Twitter conversation-id number
        :return: a vector containing deleted tweet handles in a conversation. Ex: [Handle1, Handle2, Handle1]
        """

        if conversation_id not in self.conversations[handle.lower()]:
            return []

        return [x['data-screen-name'] for x in self.conversations[handle.lower()][conversation_id]['interactions']]

    def common_elements_list(self, handle, conversation_id, _list):
        """
        finds ONLY deleted accounts interacting in an observed conversation for a given Twitter handle

        :param handle: Twitter handle of observed accounts
        :param conversation_id: Twitter conversation-id number
        :param _list: elements comparing with a specific conversation for a given Twitter handle
        :return: a vector containing handles in the passed list and the conversation. Ex: [Handle1, Handle2, Handle1]
        """

        _common_elements = []
        accounts = self.conversation_elements_list(handle, conversation_id)

        for _account in accounts:
            if _account.lower() in _list:
                _common_elements.append(_account)

        return _common_elements

    def handle_common_element_vector_count(self, handle, _list):
        """
        creates a vector that given a list L any element L(i) appearing in a conversation a the observed Twitter handle
        adds the number of occurrences L(i) is present in the conversation.

        :param handle: Twitter handle of observed accounts which initiated conversations
        :param _list: elements comparing with a specific conversation for a given Twitter handle
        :return: a vector containing number of deleted tweets per conversation. Ex: [3, 1, 0, 33, 0]
        """
        _occurrence_vector = []

        for _idx in self.handle_conversations_id(handle):
            accounts = self.conversation_elements_list(handle, _idx)
            _occurrence_elements = []

            for _account in accounts:
                if _account.lower() in _list:
                    _occurrence_elements.append(_account)
            _occurrence_vector.append(len(_occurrence_elements))

        return _occurrence_vector

    def conversation_elements_set(self, handle):
        """
        Provide a set of all handles responding to tweets made by ONE SPECIFIC observed Twitter account

        :return: set of Twitter handles. Ex: {'Handle1, Handle2, ..., HandleN}
        """
        _conversation_handles = set()

        handle = handle.lower()
        for _conversation in self.conversations[handle.lower()]:
            if self.conversations[handle][_conversation]['interactions']:
                for _account in self.conversations[handle][_conversation]['interactions']:
                    _conversation_handles.add(_account['data-screen-name'].lower())

        return _conversation_handles

    def all_conversation_elements_set(self):
        """
        Provide a set of all handles responding to tweets made by ALL observed Twitter accounts

        :return: set of Twitter handles. Ex: {'Handle1, Handle2, ..., HandleN}
        """
        _conversation_handles = set()

        for _handle in self.conversations:
            for _conversation in self.conversations[_handle]:
                if self.conversations[_handle][_conversation]['interactions']:
                    for _account in self.conversations[_handle][_conversation]['interactions']:
                        _conversation_handles.add(_account['data-screen-name'].lower())

        return _conversation_handles

    def all_handle_tweets(self, handle):
        """
        Given a Twitter handle that started a conversation returns all tweets sent by the handle

        :param handle: Twitter handle
        return: object containing tweet features conversation-id, tweet-text, and tweet-time
        """

        _conversation_list = []

        if handle in self.conversations:
            for _idx in self.conversations[handle]:
                _conversation_list.append({
                    'data-conversation-id': _idx,
                    'tweet-time': self.conversations[handle][_idx]['tweet-time'],
                    'tweet-text': self.conversations[handle][_idx]['tweet-text'],
                })

        return _conversation_list

    def handle_conversation_matrix(self, _handle, _element_list):
        """
        Given a Twitter handle that started a conversation and a list containing a set of handles that participated
        in the conversation (this set of handles could be the entire list of handles that participated in the
        conversation or a partial set of handles, such as handles which Twitter account was deleted or suspended, etc.

        :param _handle: Twitter handle that initiated a conversation
        :param _element_list: set of handles that participated in the Twitter conversation (all or partial, such as
                              handles associated with a deleted or suspended Twitter account.
        :return: two objects: obj1, obj2

                 obj1: is a list containing a dictionary of all conversation initiated by the handle. The dictionary has
                 for index the conversation-id, and its value is a dictionary containing the handles that participated
                 in the conversation (index), and the number of tweets that handle contributed (value).

                 obj1 Ex:
                 -------
                 [{'927337524808347648': {'AndreaEscobar77': 1,'Anniepie10': 5}}, {'794926969829920768': {'mary': 20'}}]

                 obj1
                 ====
                 has two conversations '927337524808347648' and '794926969829920768'; handle mary appeared in the
                 second conversation and tweeted 20 times.

                 obj2: is a dictionary containing the handles intercepting _element list (index) across all
                 conversations initiated by the Twitter _handle. The dictionary value is the number of interaction the
                 index contributed across all conversations.

                 obj2 Ex:
                 -------
                 { 'agardendesign': 1, 'Saul0074u': 5, 'patriot08642': 1}

                 obj2
                 ====
                 There were three handles that were involved in _handle conversations. Handle 'Saul0074u' contributed
                 5 tweets across all conversations.
        """
        _conversation_id = []
        _handle_count = {}

        for _idx in self.handle_conversations_id(_handle):
            _conversation_row = {_idx: self.common_elements_list(_handle, _idx, _element_list),
                                 'id': _idx,
                                 'count': {}}
            for _account in _conversation_row[_idx]:
                if _account in _conversation_row['count']:
                    _conversation_row['count'][_account] += 1
                else:
                    _conversation_row['count'][_account] = 1

                if _account in _handle_count:
                    _handle_count[_account] += 1
                else:
                    _handle_count[_account] = 1

            if _conversation_row['count']:
                _conversation_id.append({_idx: _conversation_row['count']})

        return _conversation_id, _handle_count

    def handle_text_conversation_replies(self, _handle, _conversation_id, _handle_replying):
        """
        Given a Twitter handle that started a conversation, the conversation-id, and a handle that interacting in the
        conversation, it returns all the tweets made by the interacting handle

        :param _handle: Twitter handle that started a conversation
        :param _conversation_id: Twitter conversation-id
        :param _handle_replying: Twitter handle that interacted in the conversation.
        :return: a list of text
        """
        _replying_text = []

        if _conversation_id in self.conversations[_handle]:
            for _record in self.conversations[_handle][_conversation_id]['interactions']:
                if _record['data-screen-name'].lower() == _handle_replying.lower():
                    _replying_text.append(_record['tweet-text'])

        return _replying_text

    def retrieve_root_handles(self):
        """
        From all the conversations captured return a set of handles that initiated a conversations
        :return: a set of all VMP handles. Ex: {'barackobama', 'seanhannity'}
        """

        return set([_handle.lower() for _handle in self.conversations])
