from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import Priority, Status, Ticket, TicketComment


@override_settings(
	DATABASES={
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': ':memory:',
		}
	},
	CACHES={
		'default': {
			'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		}
	},
)
class TicketSecurityTests(APITestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username='owner', password='pass12345', email='owner@example.com')
		self.other = User.objects.create_user(username='other', password='pass12345', email='other@example.com')
		self.staff = User.objects.create_user(
			username='staff', password='pass12345', email='staff@example.com', is_staff=True
		)

		self.open_status = Status.objects.create(name='Open')
		self.low_priority = Priority.objects.create(name='Low', level=1)

		self.owner_ticket = Ticket.objects.create(
			title='Owner ticket',
			description='Owner only ticket',
			status=self.open_status,
			priority=self.low_priority,
			customer=self.owner,
		)
		self.other_ticket = Ticket.objects.create(
			title='Other ticket',
			description='Other only ticket',
			status=self.open_status,
			priority=self.low_priority,
			customer=self.other,
		)

	def test_customer_list_only_shows_own_tickets(self):
		self.client.force_authenticate(user=self.owner)
		res = self.client.get('/api/tickets/')

		self.assertEqual(res.status_code, status.HTTP_200_OK)
		self.assertEqual(res.data['count'], 1)
		self.assertEqual(res.data['results'][0]['id'], self.owner_ticket.id)

	def test_customer_cannot_open_other_ticket_detail(self):
		self.client.force_authenticate(user=self.owner)
		res = self.client.get(f'/api/tickets/{self.other_ticket.id}/')
		self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

	def test_non_staff_cannot_create_status(self):
		self.client.force_authenticate(user=self.owner)
		res = self.client.post('/api/statuses/', {'name': 'In Progress'}, format='json')
		self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

	def test_internal_escalation_comment_is_hidden_for_non_staff(self):
		system_user = User.objects.create_user(username='ai_agent', password='pass12345')
		TicketComment.objects.create(
			ticket=self.owner_ticket,
			user=system_user,
			comment_text='[ESCALATION REVIEW NEEDED] Internal handoff details',
		)

		self.client.force_authenticate(user=self.owner)
		owner_res = self.client.get('/api/comments/')
		self.assertEqual(owner_res.status_code, status.HTTP_200_OK)
		owner_text = owner_res.data['results'][0]['comment_text']
		self.assertTrue(owner_text.startswith('[INTERNAL NOTE HIDDEN]'))

		self.client.force_authenticate(user=self.staff)
		staff_res = self.client.get('/api/comments/')
		self.assertEqual(staff_res.status_code, status.HTTP_200_OK)
		staff_text = staff_res.data['results'][0]['comment_text']
		self.assertEqual(staff_text, '[ESCALATION REVIEW NEEDED] Internal handoff details')

	@patch('api.views.process_new_ticket_task.delay')
	def test_ticket_create_sets_customer_and_returns_201(self, mocked_delay):
		self.client.force_authenticate(user=self.owner)
		payload = {
			'title': 'New ticket',
			'description': 'New ticket description',
			'status_id': self.open_status.id,
			'priority_id': self.low_priority.id,
		}

		res = self.client.post('/api/tickets/', payload, format='json')
		self.assertEqual(res.status_code, status.HTTP_201_CREATED)
		self.assertEqual(res.data['customer']['id'], self.owner.id)
		mocked_delay.assert_called_once()
