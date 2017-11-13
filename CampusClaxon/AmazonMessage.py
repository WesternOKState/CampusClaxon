# AWS Version 4 signing example

# EC2 API (DescribeRegions)

# See: http://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
# This version makes a GET request and passes the signature
# in the Authorization header.
import sys, os, base64, datetime, hashlib, hmac, urllib
import requests # pip install requests
import xml.etree.ElementTree as etree


class AmazonMessage():
    # ************* REQUEST VALUES *************
    method = 'GET'
    service = 'sns'
    host = 'sns.us-east-1.amazonaws.com'
    region = 'us-east-1'
    endpoint = 'https://sns.us-east-1.amazonaws.com'

    def __init__(self, access_key, secret_key):
        '''
        Initialize the AmazonMessage Class
        :param access_key: The accesskey fo rhte IAM user that has permission to use the SNS service
        :param secret_key: The secret key for that user.
        :return: Instance of class
        '''
        self.__access_key = access_key
        self.__secret_key = secret_key

    def __sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def __getSignatureKey(self, key, dateStamp, regionName, serviceName):
        kDate = self.__sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = self.__sign(kDate, regionName)
        kService = self.__sign(kRegion, serviceName)
        kSigning = self.__sign(kService, 'aws4_request')
        return kSigning

    def __generate_headers(self, canonical_querystring):
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')
        canonical_uri = '/'
        canonical_headers = 'host:' + self.host + '\n' + 'x-sms-date:' + amzdate + '\n'
        signed_headers = 'host;x-sms-date'
        payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()
        canonical_request = self.method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + \
                        canonical_headers + '\n' + signed_headers + '\n' + payload_hash
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = datestamp + '/' + self.region + '/' + self.service + '/' + 'aws4_request'
        string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  \
                     hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        signing_key = self.__getSignatureKey(self.__secret_key, datestamp, self.region, self.service)
        signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
        authorization_header = algorithm + ' ' + 'Credential=' + self.__access_key + '/' + credential_scope + ', ' +  \
                           'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
        headers = {'x-sms-date':amzdate, 'Authorization':authorization_header}
        return headers

    def send_message(self, message, topicArn):
        '''
        Sends message to every one subscribed to the topicArn
        :param message: The message to send
        :param topicArn: The topic to send it to.
        :return: True if successful HTTP error if unsuccessful
        '''
        topicArn = urllib.parse.quote(topicArn)
        message = urllib.parse.quote(message)
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        canonical_querystring = 'AWSAccessKeyId='+ self.__access_key + \
                                    '&Action=Publish' \
                                    '&Message=' + message + \
                                    '&SignatureMethod=HmacSHA256' \
                                    '&SignatureVersion=4' \
                                    '&Timestamp='+amzdate+ \
                                    '&TopicArn=' + topicArn + \
                                    '&Version=2010-03-31'

        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        print('************************************************')
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200: return True
        return res.status_code

    def get_subscribers(self, topicArn):
        '''
        Gets a dictionary of the current subscribers to the topic specified by topicArn
        :param topicArn: The topic from which to get the users
        :return: a dictionary keyed on the users phone number
        '''

        # TODO: Account for more than 100 subscribers
        topicArn = urllib.parse.quote(topicArn)
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        canonical_querystring = 'AWSAccessKeyId=' + self.__access_key + \
                            '&Action=ListSubscriptionsByTopic' \
                            '&SignatureMethod=HmacSHA256' \
                            '&SignatureVersion=4' \
                            '&Timestamp='+ amzdate + \
                            '&TopicArn=' + topicArn + \
                            '&Version=2010-03-31'

        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        r = requests.get(request_url, headers=headers)
        print(r.text)
        if r.status_code == 200:
            root = etree.fromstring(r.text)
            res = []
            results = self.__get_all_endpoints(root, res)
        return results

    def subscribe(self, end_point, topicArn):
        '''
        subscribes a users phone to the topic specified by topicArn
        :param end_point: User's phone number
        :param topicArn: The topic in which to subscribe
        :return: SubscriptionArn if successfull, 0 if not
        '''
        topicArn = urllib.parse.quote(topicArn)
        canonical_querystring = 'Action=Subscribe' \
                                '&Endpoint={}' \
                                '&Protocol=sms&TopicArn={}' \
                                '&Version=2010-03-31'.format(end_point, topicArn)

        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200:
            print("Subscribed: {} to {}".format(end_point, topicArn))
            root = etree.fromstring(res.text)
            return root[0][0].text
        else:
            print(res.text)
            return 0

    def unsubscribe(self, subscription_arn):
        '''
        Method for unsubscribing to the specified topic.
        :param access_key: Provided by amazon for that account
        :param secret_key: Provided by amazon for that account
        :param end_point: The user's phone number in the for 15803010000
        :param topicArn: The Arn for the topic to unsubscribe from
        :return: True if successful error code if not
        '''

        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        subscription_arn = urllib.parse.quote(subscription_arn)
        canonical_querystring = 'AWSAccessKeyId={}' \
                            '&Action=Unsubscribe' \
                            '&SignatureMethod=HmacSHA256' \
                            '&SignatureVersion=4' \
                            '&SubscriptionArn={}' \
                            '&Timestamp={}'.format(self.__access_key, subscription_arn, amzdate)

        # print("querystring = {}".format(canonical_querystring))
        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200: return 0
        print(res.text)
        return res.status_code

    def create_topic(self, topic_name):
        '''
        Creates new topic
        :param topic_name: The name for the topic
        :return: topicArn for the new topic. or XML Error information
        '''
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        canonical_querystring = 'AWSAccessKeyId={}' \
                            '&Action=CreateTopic' \
                            '&Name={}' \
                            '&SignatureMethod=HmacSHA256' \
                            '&SignatureVersion=4' \
                            '&Timestamp={}'.format(self.__access_key, topic_name, amzdate)

        # print("querystring = {}".format(canonical_querystring))
        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200:
            r = requests.get(request_url, headers=headers)
            tree = etree.fromstring(r.text)
            return tree[0][0].text
        # print(res.text)
        return 0

    def get_topics(self):
        '''
                Creates new topic
                :param topic_name: The name for the topic
                :return: topicArn for the new topic. or XML Error information
                '''

        # TODO: Account for more than 100 topics.
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        canonical_querystring = 'AWSAccessKeyId={}' \
                                '&Action=ListTopics' \
                                '&SignatureMethod=HmacSHA256' \
                                '&SignatureVersion=4' \
                                '&Timestamp={}'.format(self.__access_key, amzdate)

        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200:
            r = requests.get(request_url, headers=headers)
            root = etree.fromstring(r.text)
            res = []
            results = self.__find_all_topics('TopicArn', root, res)
        return results

    def set_topic_attributes(self, topic_arn, display_name):
        """
                Sets the display name for an existing topic.
                :param display_name: the prefix to display befor every text message.
                :param  topic_arn: The arn for the topic
                :return: topicArn for the new topic. or XML Error information
        """

        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        topic_arn = urllib.parse.quote(topic_arn)
        canonical_querystring = 'AWSAccessKeyId={}' \
                                '&Action=SetTopicAttributes' \
                                '&AttributeName=DisplayName' \
                                '&AttributeValue={}' \
                                '&SignatureMethod=HmacSHA256' \
                                '&SignatureVersion=4' \
                                '&TimeStamp={}' \
                                '&TopicArn={}'.format(self.__access_key, display_name, amzdate, topic_arn)

        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200:
            results = 0
        else:
            print(res.content)
            results = -1
        return results

    def delete_topic(self, topic_arn):
        '''
        Deletes topic
        :param topic_name: The name for the topic
        :return: 0 if it worked.
        '''
        topic_arn = urllib.parse.quote(topic_arn)
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        canonical_querystring = 'AWSAccessKeyId={}' \
                                '&Action=DeleteTopic' \
                                '&SignatureMethod=HmacSHA256' \
                                '&SignatureVersion=4' \
                                '&Timestamp={}' \
                                '&TopicArn={}'.format(self.__access_key, amzdate, topic_arn)

        headers = self.__generate_headers(canonical_querystring)
        request_url = self.endpoint + '?' + canonical_querystring
        res = requests.get(request_url, headers=headers)
        if res.status_code == 200:
            return 0
        print(res.status_code)
        print(res.text)
        return res.text

    def get_topcs(self):
        pass

    def __find_all_topics(self, find_str, root, res):
        # finds all the occurences of the topics and returns a dictionary keyed on the topic name and contains the arn
        ns = "{http://sns.amazonaws.com/doc/2010-03-31/}"
        if root.tag == ns + find_str:
            groups = root.text.split(':')
            res.append({'name':groups[5], 'arn': root.text})
        for child in root:
            self.__find_all_topics(find_str, child, res)
        return res

    def __get_all_endpoints(self, root, res):
        ns = "{http://sns.amazonaws.com/doc/2010-03-31/}"
        if root.tag == ns + 'member':
            res.append({'endpoint' : root[1].text, 'SubscriptionArn': root[3].text})
            print({'endpoint' : root[1].text, 'SubscriptionArn': root[3].text})
        for child in root:
            self.__get_all_endpoints(child, res)
        return res