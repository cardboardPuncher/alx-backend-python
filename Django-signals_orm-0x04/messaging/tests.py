from django.test import TestCase
from messaging.models import Message, Notification
from django.contrib.auth import get_user_model
# Create your tests here.

User = get_user_model()
class TestMessageModel(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create_user(
            first_name='Test',
            last_name='Boy',
            email='testboy@gmail.com',
            phone_number='233501001000',
            role='HST',
            password='secret12345A',
            username='testboy1')

        cls.user2 = User.objects.create_user(
            first_name='Test',
            last_name='Girl',
            email='testgirl@gmail.com',
            phone_number='233501002000',
            role='GST',
            password='secret12345B',
            username='testgirl1')
        
    def setUp(self) -> None:
        self.message1 = Message.objects.create(
            sender = self.user1,
            content= 'Hello Girly!',
            receiver= self.user2
        )
        self.message2 = Message.objects.create(
            sender = self.user2,
            content= 'Hi TestBoi',
            receiver = self.user1
        )
        
    def test_message_creation(self):
        self.assertIsInstance(self.message1, Message)
        self.assertIsInstance(self.message2, Message)

        self.assertEqual(
            list(self.user1.sent_messages.all()), #type: ignore
            list(Message.objects.filter(sender=self.user1).all()),
        )

        self.assertEqual(
            list(self.user2.recieved_messages.all()), #type: ignore
            list(Message.objects.filter(receiver=self.user2).all())
        )

    def test_notifications_exist(self):
        user2_notify = Notification.objects.filter(user=self.user2).get()
        self.assertIsNotNone(user2_notify)

        self.assertEqual(
            user2_notify.user.user_id,
            self.user2.user_id #type: ignore
        )