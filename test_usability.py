import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

@pytest.fixture
def driver():
    driver = webdriver.Chrome()  # Asegúrate de tener el ChromeDriver instalado y en tu PATH
    yield driver
    driver.quit()

def test_index_page(driver):
    driver.get("http://127.0.0.1:5000")  # URL de tu aplicación
    assert "Sistema de Recomendación de PC" in driver.title

    # Verificar que la respuesta es correcta
    assert "Resultados" in driver.page_source
