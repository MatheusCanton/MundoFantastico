function enviarFormulario(e) {
  e.preventDefault();

  const nome = document.getElementById('nome').value.trim();
  const whatsapp = document.getElementById('whatsapp').value.trim();
  const data = document.getElementById('data').value;
  const personagem = document.getElementById('personagem').value;
  const pacote = document.getElementById('pacote').value;
  const cidade = document.getElementById('cidade').value.trim();
  const mensagem = document.getElementById('mensagem').value.trim();

  const dataFormatada = data
    ? new Date(data + 'T12:00:00').toLocaleDateString('pt-BR')
    : 'A definir';

  const texto = `Olá! Vim pelo site e quero fazer um orçamento! 🎉

*Nome:* ${nome}
*WhatsApp:* ${whatsapp}
*Data da festa:* ${dataFormatada}
*Personagem:* ${personagem || 'A definir'}
*Pacote:* ${pacote || 'A definir'}
*Cidade:* ${cidade}
${mensagem ? `*Mensagem:* ${mensagem}` : ''}`;

  const url = `https://wa.me/5511950577511?text=${encodeURIComponent(texto)}`;

  document.getElementById('formOrcamento').style.display = 'none';
  document.getElementById('formSucesso').style.display = 'block';

  setTimeout(() => { window.open(url, '_blank'); }, 500);
}

// Máscara de telefone
document.getElementById('whatsapp').addEventListener('input', function () {
  let v = this.value.replace(/\D/g, '');
  if (v.length <= 11) {
    v = v.replace(/^(\d{2})(\d)/, '($1) $2');
    v = v.replace(/(\d{5})(\d{4})$/, '$1-$2');
  }
  this.value = v;
});

// Smooth scroll para links âncora
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
