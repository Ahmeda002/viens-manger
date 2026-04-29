from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Recipe, Comment, UserProfile


class AuthTests(TestCase):

    def test_register_creates_user_and_redirects(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_saves_email(self):
        self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_register_creates_user_profile(self):
        self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        user = User.objects.get(username='testuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_register_invalid_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'WrongPass123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_login_valid_credentials(self):
        User.objects.create_user(username='testuser', password='StrongPass123!')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'StrongPass123!',
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_invalid_credentials(self):
        User.objects.create_user(username='testuser', password='StrongPass123!')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)


class AuthProtectionTests(TestCase):

    def test_add_recipe_requires_login(self):
        response = self.client.get(reverse('add_recipe'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('add_recipe')}")

    def test_edit_recipe_requires_login(self):
        user = User.objects.create_user(username='owner', password='pass')
        recipe = Recipe.objects.create(user=user, title='Test', description='Desc')
        response = self.client.get(reverse('edit_recipe', args=[recipe.id]))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('edit_recipe', args=[recipe.id])}")

    def test_delete_recipe_requires_login(self):
        user = User.objects.create_user(username='owner', password='pass')
        recipe = Recipe.objects.create(user=user, title='Test', description='Desc')
        response = self.client.post(reverse('delete_recipe', args=[recipe.id]))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('delete_recipe', args=[recipe.id])}")

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('profile')}")

    def test_save_api_recipe_requires_login(self):
        response = self.client.post(reverse('save_api_recipe'), {
            'title': 'API Meal',
            'description': 'From API',
            'image_url': 'http://example.com/img.jpg',
        })
        self.assertRedirects(response, f"/accounts/login/?next={reverse('save_api_recipe')}")


class RecipeCRUDTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.other_user = User.objects.create_user(username='otheruser', password='StrongPass123!')
        self.client.login(username='testuser', password='StrongPass123!')

    def test_create_recipe(self):
        response = self.client.post(reverse('add_recipe'), {
            'title': 'Pasta',
            'description': 'Tasty pasta',
            'ingredients': 'pasta\nsalt',
            'instructions': 'Boil water. Cook pasta.',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Recipe.objects.filter(title='Pasta', user=self.user).exists())

    def test_create_recipe_assigns_logged_in_user(self):
        self.client.post(reverse('add_recipe'), {
            'title': 'Soup',
            'description': 'Hot soup',
            'ingredients': '',
            'instructions': '',
        })
        recipe = Recipe.objects.get(title='Soup')
        self.assertEqual(recipe.user, self.user)

    def test_edit_recipe(self):
        recipe = Recipe.objects.create(user=self.user, title='Old Title', description='Old desc')
        response = self.client.post(reverse('edit_recipe', args=[recipe.id]), {
            'title': 'New Title',
            'description': 'New desc',
            'ingredients': '',
            'instructions': '',
        })
        self.assertRedirects(response, reverse('home'))
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'New Title')

    def test_edit_recipe_blocked_for_other_user(self):
        recipe = Recipe.objects.create(user=self.other_user, title='Their Recipe', description='Desc')
        response = self.client.post(reverse('edit_recipe', args=[recipe.id]), {
            'title': 'Hacked',
            'description': 'Hacked desc',
            'ingredients': '',
            'instructions': '',
        })
        self.assertEqual(response.status_code, 404)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'Their Recipe')

    def test_delete_recipe(self):
        recipe = Recipe.objects.create(user=self.user, title='To Delete', description='Desc')
        response = self.client.post(reverse('delete_recipe', args=[recipe.id]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_recipe_blocked_for_other_user(self):
        recipe = Recipe.objects.create(user=self.other_user, title='Protected', description='Desc')
        self.client.post(reverse('delete_recipe', args=[recipe.id]))
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_home_shows_only_own_recipes(self):
        Recipe.objects.create(user=self.user, title='My Recipe', description='Mine')
        Recipe.objects.create(user=self.other_user, title='Their Recipe', description='Theirs')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'My Recipe')
        self.assertNotContains(response, 'Their Recipe')

    def test_recipe_detail_page(self):
        recipe = Recipe.objects.create(user=self.user, title='Detail Test', description='Desc',
                                       ingredients='eggs\nmilk', instructions='Mix it.')
        response = self.client.get(reverse('recipe_detail', args=[recipe.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Test')
        self.assertContains(response, 'Mix it.')


class SaveAPIRecipeTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.client.login(username='testuser', password='StrongPass123!')

    def test_save_api_recipe_creates_recipe(self):
        response = self.client.post(reverse('save_api_recipe'), {
            'title': 'API Meal',
            'description': 'Chicken — British',
            'image_url': 'http://example.com/img.jpg',
            'ingredients': 'chicken\nsalt',
            'instructions': 'Cook it.',
            'meal_id': '12345',
        })
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(Recipe.objects.filter(title='API Meal', user=self.user).exists())

    def test_save_api_recipe_stores_meal_id(self):
        self.client.post(reverse('save_api_recipe'), {
            'title': 'API Meal',
            'description': 'Desc',
            'image_url': 'http://example.com/img.jpg',
            'ingredients': '',
            'instructions': '',
            'meal_id': '99999',
        })
        recipe = Recipe.objects.get(title='API Meal')
        self.assertEqual(recipe.meal_id, '99999')

    def test_save_api_recipe_missing_title_does_not_save(self):
        self.client.post(reverse('save_api_recipe'), {
            'title': '',
            'description': 'No title',
            'image_url': '',
            'ingredients': '',
            'instructions': '',
            'meal_id': '',
        })
        self.assertFalse(Recipe.objects.filter(description='No title').exists())


class CommentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass123!')
        self.recipe = Recipe.objects.create(user=self.user, title='Recipe', description='Desc')

    def test_post_comment_when_logged_in(self):
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.post(reverse('allow_comment', args=[self.recipe.id]), {
            'comment': 'Great recipe!',
        })
        self.assertRedirects(response, reverse('allow_comment', args=[self.recipe.id]))
        self.assertTrue(Comment.objects.filter(recipe=self.recipe, text='Great recipe!').exists())

    def test_post_comment_unauthenticated_redirects_to_login(self):
        response = self.client.post(reverse('allow_comment', args=[self.recipe.id]), {
            'comment': 'Sneaky comment',
        })
        self.assertRedirects(response, f"/accounts/login/?next=/comment/{self.recipe.id}/")
        self.assertFalse(Comment.objects.filter(text='Sneaky comment').exists())

    def test_empty_comment_not_saved(self):
        self.client.login(username='testuser', password='StrongPass123!')
        self.client.post(reverse('allow_comment', args=[self.recipe.id]), {
            'comment': '   ',
        })
        self.assertEqual(Comment.objects.filter(recipe=self.recipe).count(), 0)

    def test_comment_page_shows_existing_comments(self):
        Comment.objects.create(recipe=self.recipe, user=self.user, text='Looks delicious!')
        self.client.login(username='testuser', password='StrongPass123!')
        response = self.client.get(reverse('allow_comment', args=[self.recipe.id]))
        self.assertContains(response, 'Looks delicious!')
