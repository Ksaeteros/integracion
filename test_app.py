import unittest
from app import app
 
class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
 
    def test_index_and_recomendar(self):
        # Test the index page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sistema de Recomendaci\xc3\xb3n de PC', response.data)
 
        # Test the recomendar endpoint
        response = self.app.post('/recomendar', data=dict(
            procesador='Intel Core i5',
            ram='16',
            gpu='NVIDIA GTX 1660',
            presupuesto='1500'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<div class="resultado">', response.data)
 
if __name__ == '__main__':
    unittest.main()