const CRM_URL_PADRAO = 'http://127.0.0.1:5000';

function normalizarOrigem(url) {
  const parsed = new URL(url || CRM_URL_PADRAO);
  if (!['http:', 'https:'].includes(parsed.protocol)) throw new Error('A URL do CRM deve usar HTTP ou HTTPS.');
  return parsed.origin;
}

function remetenteEhPortal(sender) {
  try {
    return new URL(sender?.url || '').origin === 'https://gestao.sistemacorban.com.br';
  } catch (_) {
    return false;
  }
}

async function enviarParaCrm(dados) {
  const configuracao = await chrome.storage.local.get({ crmBaseUrl: CRM_URL_PADRAO });
  const origem = normalizarOrigem(configuracao.crmBaseUrl);
  const permissao = `${origem}/*`;
  const permitido = await chrome.permissions.contains({ origins: [permissao] });
  if (!permitido) {
    return { sucesso: false, mensagem: 'Autorize a URL do CRM nas configurações da extensão.' };
  }

  const abas = await chrome.tabs.query({ url: permissao });
  const candidatas = abas.filter((aba) => {
    try {
      return new URL(aba.url).pathname.replace(/\/$/, '') === '/nova';
    } catch (_) {
      return false;
    }
  });
  if (!candidatas.length) {
    return { sucesso: false, mensagem: 'Abra a página Nova Proposta no CRM configurado.' };
  }

  for (const aba of candidatas) {
    const resultados = await chrome.scripting.executeScript({
      target: { tabId: aba.id },
      world: 'MAIN',
      func: (payload) => {
        if (!window.crmImportacaoPortal?.estaAguardando?.()) {
          return { sucesso: false, motivo: 'A aba não está aguardando importação.' };
        }
        if (typeof window.aplicarDadosConsultaINSS !== 'function') {
          return { sucesso: false, motivo: 'A integração não está disponível nesta página.' };
        }
        return window.aplicarDadosConsultaINSS(payload);
      },
      args: [dados],
    });
    const retorno = resultados?.[0]?.result;
    if (retorno?.sucesso) {
      return { sucesso: true, mensagem: 'Dados enviados ao CRM. Revise a Nova Proposta antes de salvar.' };
    }
  }
  return { sucesso: false, mensagem: 'Na Nova Proposta, clique primeiro em “Aguardar importação do portal”.' };
}

chrome.runtime.onMessage.addListener((mensagem, sender, responder) => {
  if (mensagem?.tipo !== 'enviar-para-crm') return false;
  if (!remetenteEhPortal(sender)) {
    responder({ sucesso: false, mensagem: 'Origem não autorizada.' });
    return false;
  }
  enviarParaCrm(mensagem.dados || {})
    .then(responder)
    .catch(() => responder({ sucesso: false, mensagem: 'Não foi possível concluir a importação. Verifique a configuração do CRM.' }));
  return true;
});
