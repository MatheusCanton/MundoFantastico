import os
import time
import random
import logging
from urllib.parse import quote
from dataclasses import dataclass
from typing import Optional, Callable

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


@dataclass
class ResultadoEnvio:
    sucesso: bool
    telefone: str
    mensagem: str
    erro: Optional[str] = None


class WhatsAppSender:
    WHATSAPP_URL = "https://web.whatsapp.com"
    SEND_URL = "https://web.whatsapp.com/send?phone={phone}&text={text}"

    # Seletores CSS do WhatsApp Web (com fallbacks)
    SELETORES_BOTAO_ENVIAR = [
        '[data-testid="send"]',
        'button[aria-label="Enviar"]',
        'button[aria-label="Send"]',
        'span[data-icon="send"]',
    ]
    SELETOR_CAIXA_MENSAGEM = '[data-testid="conversation-compose-box-input"]'
    SELETOR_POPUP_ERRO = '[data-animate-modal-popup="true"]'
    SELETOR_LISTA_CHATS = '[data-testid="chat-list"]'

    def __init__(self, pausa: int = 18, variacao: int = 7):
        self.driver: Optional[webdriver.Chrome] = None
        self.pausa = pausa
        self.variacao = variacao

    def iniciar(self, headless: bool = False) -> bool:
        """Abre o Chrome com WhatsApp Web. Retorna True quando pronto."""
        opcoes = Options()
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("--disable-dev-shm-usage")
        opcoes.add_argument("--disable-blink-features=AutomationControlled")
        opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
        opcoes.add_experimental_option("useAutomationExtension", False)

        # Mantém sessão entre execuções (evita re-scan do QR toda vez)
        session_dir = os.path.join(_BASE_DIR, "chrome_session")
        os.makedirs(session_dir, exist_ok=True)
        opcoes.add_argument(f"--user-data-dir={session_dir}")

        if headless:
            opcoes.add_argument("--headless=new")

        servico = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=servico, options=opcoes)
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.driver.get(self.WHATSAPP_URL)
        return True

    def aguardar_login(self, timeout: int = 120, callback: Optional[Callable] = None) -> bool:
        """Aguarda o usuário escanear o QR code. Retorna True quando logado."""
        logger.info("Aguardando login no WhatsApp Web...")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.SELETOR_LISTA_CHATS))
            )
            logger.info("Login detectado com sucesso.")
            if callback:
                callback("logado")
            return True
        except TimeoutException:
            logger.error("Timeout aguardando login.")
            return False

    def esta_logado(self) -> bool:
        """Verifica se já está logado sem aguardar."""
        try:
            self.driver.find_element(By.CSS_SELECTOR, self.SELETOR_LISTA_CHATS)
            return True
        except NoSuchElementException:
            return False

    def enviar_mensagem(self, telefone: str, mensagem: str) -> ResultadoEnvio:
        """Envia uma mensagem para um número específico."""
        url = self.SEND_URL.format(phone=telefone, text=quote(mensagem))
        logger.info(f"Abrindo chat: {telefone}")

        try:
            self.driver.get(url)

            # Aguarda botão de envio OU popup de erro
            WebDriverWait(self.driver, 20).until(
                EC.any_of(
                    *[EC.presence_of_element_located((By.CSS_SELECTOR, s))
                      for s in self.SELETORES_BOTAO_ENVIAR],
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.SELETOR_POPUP_ERRO)),
                )
            )

            # Verifica popup de número inválido
            try:
                popup = self.driver.find_element(By.CSS_SELECTOR, self.SELETOR_POPUP_ERRO)
                if popup.is_displayed():
                    self._fechar_popup()
                    return ResultadoEnvio(
                        sucesso=False,
                        telefone=telefone,
                        mensagem=mensagem,
                        erro="Número não encontrado no WhatsApp",
                    )
            except NoSuchElementException:
                pass

            # Localiza e clica no botão enviar
            botao = self._localizar_botao_enviar()
            if not botao:
                return ResultadoEnvio(
                    sucesso=False,
                    telefone=telefone,
                    mensagem=mensagem,
                    erro="Botão de envio não encontrado",
                )

            botao.click()
            time.sleep(2)

            logger.info(f"Mensagem enviada para {telefone}")
            return ResultadoEnvio(sucesso=True, telefone=telefone, mensagem=mensagem)

        except TimeoutException:
            return ResultadoEnvio(
                sucesso=False,
                telefone=telefone,
                mensagem=mensagem,
                erro="Timeout ao carregar o chat",
            )
        except Exception as e:
            logger.exception(f"Erro inesperado ao enviar para {telefone}")
            return ResultadoEnvio(sucesso=False, telefone=telefone, mensagem=mensagem, erro=str(e))

    def _localizar_botao_enviar(self):
        """Tenta múltiplos seletores para encontrar o botão enviar."""
        for seletor in self.SELETORES_BOTAO_ENVIAR:
            try:
                botao = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, seletor))
                )
                return botao
            except TimeoutException:
                continue
        return None

    def _fechar_popup(self):
        """Fecha popup de erro do WhatsApp."""
        try:
            botao = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="popup-confirm"]')
            botao.click()
        except NoSuchElementException:
            try:
                botao = self.driver.find_element(By.CSS_SELECTOR, "button.popup-btn-ok")
                botao.click()
            except NoSuchElementException:
                pass

    def pausa_aleatoria(self):
        """Aguarda um tempo aleatório entre envios para parecer humano."""
        espera = self.pausa + random.uniform(-self.variacao / 2, self.variacao)
        espera = max(10, espera)
        logger.info(f"Aguardando {espera:.1f}s antes do próximo envio...")
        time.sleep(espera)

    def fechar(self):
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()
            self.driver = None
