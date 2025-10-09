import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import timezone, datetime, timedelta
import unittest
from app import db, web_app
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.web_app_context = web_app.app_context()
        self.web_app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.web_app_context.pop()

    def testPasswordHashing(self):
        u = User(login='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def testAvatar(self):
        u = User(login='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_follow(self):
        u1 = User(login='anakin', email='anakin@example.com')
        u2 = User(login='david', email='david@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        follower = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(follower, [])
        
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_follower = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].login, 'david')
        self.assertEqual(u2_follower[0].login, 'anakin')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)

    def test_follow_post(self):
        u1 = User(login='john', email='john@example.com')
        u2 = User(login='susan', email='susan@example.com')
        u3 = User(login='mary', email='mary@example.com')
        u4 = User(login='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        now = datetime.now(timezone.utc)
        p1 = Post(body="post from john", author=u1,
                  timestamp=now + timedelta(seconds=1))
        