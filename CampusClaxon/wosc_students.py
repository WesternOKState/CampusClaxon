import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CampusClaxon.settings")
import django
django.setup()
from AlertAdmin.models import Subscriber, TopicSubscription, Setting, Topic
from .AmazonMessage import AmazonMessage
from .lib import get_hash, change_cell_number
import pymysql.cursors


class SubscribeError(Exception):
    def __init__(self, subscription):
        self.message = "Unable to subscribe {}, {} to {}".format(subscription.subscriber.last_name,                                                             subscription.subscriber.first_name,
                                                             subscription.topic.topic_name)


class UnsubscribeError(Exception):
    def __init__(self, subscription):
        self.message = "Unable to unsubscribe {}, {} from {}".format(subscription.subscriber.last_name,
                                                             subscription.subscriber.first_name,
                                                             subscription.topic.topic_name)

class WoscStudents():

    def __init__(self):
        settings = Setting.objects.all()[0]

        self.amz = AmazonMessage(settings.aws_security_key, settings.aws_secret_key)

    def sync_students(self):
        students = self.__get_poise_students()

        for student in students:
            if Subscriber.objects.filter(hash=student['hash']).exists():
                subscriber = Subscriber.objects.get(hash=student['hash'])
            else:
                subscriber = Subscriber()
            subscriber.last_name = student['last_name']
            subscriber.first_name = student['first_name']
            if subscriber.cell_phone != student['cell_phone'] and subscriber.cell_phone is not None:
                change_cell_number(subscriber.cell_phone, student['cell_phone'])
            subscriber.cell_phone = student['cell_phone']
            subscriber.student_id = student['student_id']
            subscriber.school_email = student['school_email']
            subscriber.personal_email = student['personal_email']
            subscriber.hash = student['hash']

            if subscriber.opt_out != student['opt_out'] and subscriber.opt_out is not None:
                # They have opted out.
                if subscriber.opt_out:
                    self.__subscriber_opt_out(subscriber)
                elif not subscriber.opt_out:
                    # They have opted in
                    self.__subscriber_opt_in(subscriber)

            elif subscriber.opt_out is None:
                self.__setup_initial_subscriptions(subscriber)

            subscriber.opt_out = student['opt_out']
            subscriber.save()

    def __setup_initial_subscriptions(self, subscriber):
        topics = Topic.objects.filter(type='required')
        for topic in topics:
            if TopicSubscription.objects.filter(topic=topic, subscriber=subscriber).exists():
                subscription = TopicSubscription.objects.filter(topic=topic, subscriber=subscriber)
            else:
                subscription = TopicSubscription()
                subscription.topic = topic
                subscription.subscriber = subscriber
            res = self.amz.subscribe(subscriber.cell_phone, topic.topic_arn)
            if res != 0:
                subscription.status = 'active'
                subscription.subscription_arn = res
                subscription.save()
            else:
                raise SubscribeError(subscription)
        # TODO Subscribe as inactive to classes and public topics

    def __subscriber_opt_in(self, subscriber):
        # Just update the required subscriptions
        subscriptions = TopicSubscription.objects.filter(type='required')
        for subscription in subscriptions:
            if subscription.status != 'active':
                res = self.amz.subscribe(subscriber.cell_phone)
                if res != 0:
                    subscription.status = 'active'
                    subscriber.subscription_arn = res
                    subscription.save()
            else:
                raise SubscribeError(subscription)

    def __subscriber_opt_out(self, subscriber):
        subscriptions = TopicSubscription.objects.get(subscriber=subscriber, status='active')
        for subscription in subscriptions:
            res = self.amz.unsubscribe(subscription.subscription_arn)
            if (res == 0):
                subscription.status = 'disabled'
                subscription.subscription_arn = "na"
                subscription.save()
            else:
                raise UnsubscribeError(subscription)


    def __get_poise_students(self):
        connection = pymysql.connect(host='10.250.20.125', user="boggybottom", db='poise')

        cursor = connection.cursor()

        sql = '''select r.studentid as StudentID,
            s.cellphone as Cellphone,
            case
                when c.emailother like "%wosc%" then ""
                    else c.emailother
            end as PersonalEmail,
            m.email as SchoolEmail,
            c.lastname as Lastname,
            c.firstname as Firstname,
            case a.txtmessage
                when "N" then 0
                    else 1
            end as OptIn,
            group_concat(cch.section,"-",cch.termcode) as 'Section-Termcode'
            from poise.coursecrshist cch
            join poise.regdat r on r.courseid = cch.courseid
            join poise.student s on s.studentid = r.studentid
            join poise.common c on c.studentid = r.studentid
            left join moodle.mdl_user m on replace(m.idnumber,"-","") = r.studentid
            left join poise.admission_application a on a.studentid = r.studentid
            where str_to_date(lpad(cch.stopdate,8,"0"),"%m%d%Y") >= curdate()
            and r.recordtype = 1
            group by s.studentid limit 10;'''

        cursor.execute(sql)
        results = cursor.fetchall()
        connection.close()
        students = self.__poise_results_to_dict(results)
        return students


    def __poise_results_to_dict(self, results):
        students = []
        for result in results:
            if len(result[1] == 9):
                cell_phone = 1 + result[1]
            else:
                cell_phone = None
            if result[6] == "0":
                opt_out = True
            else:
                opt_out = False
            hash = get_hash(result[0])
            students.append(
                {'student_id': result[0],
                 'cell_phone': cell_phone,
                 'personal_email': result[2],
                 'school_email': result[3],
                 'last_name': result[4],
                 'first_name': result[5],
                 'opt_out': opt_out,
                 'hash': hash
                 }
            )
        return students

def main():
    data = WoscStudents()
    data.sync_students()

if  __name__ == "__main__":
    main()




