document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.cpf-mask').forEach((input) => {
        input.addEventListener('input', () => {
            let v = input.value.replace(/\D/g, '').slice(0, 11);
            v = v.replace(/(\d{3})(\d)/, '$1.$2');
            v = v.replace(/(\d{3})(\d)/, '$1.$2');
            v = v.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            input.value = v;
        });
    });

    // v32: sugestões de cliente por CPF + matrícula.
    const cpfField = document.querySelector('input[name="cpf"]');
    const matriculaField = document.querySelector('input[name="nb_matricula"]');
    const matriculaSelect = document.getElementById('cliente-matricula-select');
    const clienteAjuda = document.querySelector('.cliente-sugestao-ajuda');

    function setFieldValue(name, value) {
        const field = document.querySelector(`[name="${name}"]`);
        if (field && value !== undefined && value !== null) {
            field.value = value;
        }
    }

    function preencherDadosCliente(cliente, novaMatricula = false) {
        if (!cliente) return;
        setFieldValue('nome', cliente.nome || '');
        setFieldValue('telefone', cliente.telefone || '');
        setFieldValue('tipo_cliente', cliente.tipo_cliente || '');
        setFieldValue('endereco', cliente.endereco || '');
        setFieldValue('dados_bancarios', cliente.dados_bancarios || '');
        if (!novaMatricula) {
            setFieldValue('nb_matricula', cliente.nb_matricula || '');
        } else if (matriculaField) {
            matriculaField.value = '';
            matriculaField.focus();
        }
        // Importante: benefício bloqueado não é reaproveitado, porque pode mudar a cada proposta.
    }

    let clientesCPFCache = [];
    let ultimaConsultaClientes = 0;

    function montarSelectMatriculas(clientes) {
        matriculaSelect.innerHTML = '<option value="">Cliente encontrado</option>';

        clientes.forEach((cliente, index) => {
            const option = document.createElement('option');
            option.value = String(index);
            option.textContent = cliente.label || `Matrícula ${index + 1}`;
            matriculaSelect.appendChild(option);
        });

        const nova = document.createElement('option');
        nova.value = 'nova';
        nova.textContent = 'Nova matrícula';
        matriculaSelect.appendChild(nova);
    }

    async function buscarClientesPorCpf() {
        if (!cpfField || !matriculaSelect) return;
        const consultaAtual = ++ultimaConsultaClientes;
        const digits = cpfField.value.replace(/\D/g, '');

        matriculaSelect.classList.add('hidden');
        matriculaSelect.innerHTML = '<option value="">Cliente encontrado</option>';
        clientesCPFCache = [];

        if (digits.length !== 11) {
            if (clienteAjuda) clienteAjuda.textContent = 'Digite o CPF para consultar matrículas já cadastradas.';
            return;
        }

        try {
            const response = await fetch(`/api/clientes/por-cpf?cpf=${encodeURIComponent(cpfField.value)}`);
            if (!response.ok) throw new Error('Falha ao consultar clientes.');
            const clientes = await response.json();

            // Evita duplicação quando blur/change disparam consultas quase ao mesmo tempo.
            if (consultaAtual !== ultimaConsultaClientes) return;

            clientesCPFCache = clientes;

            if (!clientesCPFCache.length) {
                if (clienteAjuda) clienteAjuda.textContent = 'Nenhum cliente cadastrado para este CPF. Cadastre normalmente.';
                return;
            }

            montarSelectMatriculas(clientesCPFCache);
            matriculaSelect.classList.remove('hidden');
            if (clienteAjuda) clienteAjuda.textContent = 'Cliente encontrado';
        } catch (error) {
            console.error(error);
            if (consultaAtual === ultimaConsultaClientes && clienteAjuda) clienteAjuda.textContent = 'Não foi possível consultar matrículas agora.';
        }
    }

    if (cpfField && matriculaSelect) {
        cpfField.addEventListener('blur', buscarClientesPorCpf);
        cpfField.addEventListener('change', buscarClientesPorCpf);
        if (cpfField.value.replace(/\D/g, '').length === 11) {
            buscarClientesPorCpf();
        }

        matriculaSelect.addEventListener('change', () => {
            const value = matriculaSelect.value;
            if (value === 'nova') {
                const base = clientesCPFCache[0];
                preencherDadosCliente(base, true);
                if (clienteAjuda) clienteAjuda.textContent = 'Cliente encontrado · nova matrícula';
                return;
            }
            const cliente = clientesCPFCache[Number(value)];
            if (cliente) {
                preencherDadosCliente(cliente, false);
                if (clienteAjuda) clienteAjuda.textContent = 'Cliente encontrado · dados preenchidos automaticamente.';
            }
        });
    }


    function parseMoneyInputValue(value) {
        let text = String(value || '').replace('R$', '').replace(/\s/g, '').trim();
        if (!text) return 0;

        // Quando o usuário digita 5000, interpretar como 5000,00 e não 50,00.
        // Quando digita 5.000, interpretar como milhar brasileiro.
        // Quando digita 5000,50 ou 5.000,50, respeitar a vírgula decimal.
        if (text.includes(',')) {
            text = text.replace(/\./g, '').replace(',', '.');
            return Number(text) || 0;
        }

        if (/^\d{1,3}(\.\d{3})+$/.test(text)) {
            text = text.replace(/\./g, '');
            return Number(text) || 0;
        }

        return Number(text.replace(',', '.')) || 0;
    }

    document.querySelectorAll('.money-mask').forEach((input) => {
        input.addEventListener('blur', () => {
            const number = parseMoneyInputValue(input.value);
            input.value = number.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        });
    });



    document.querySelectorAll('.percent-mask').forEach((input) => {
        input.addEventListener('blur', () => {
            let value = input.value.trim().replace('%', '').replace(',', '.');
            if (!value) return;
            const number = Number(value);
            if (Number.isNaN(number)) {
                input.value = '';
                return;
            }
            input.value = String(number).replace('.', ',');
        });
    });

    function parseBRNumber(value) {
        const text = String(value || '').replace('R$', '').replace('%', '').trim();
        if (!text) return 0;
        return Number(text.replace(/\./g, '').replace(',', '.')) || 0;
    }

    function formatBRL(number) {
        return Number(number || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    // Calcula comissão em qualquer formulário/tela que tenha Valor + % comissão + Comissão.
    // Isso cobre os formulários administrativos de edição da proposta.
    function calcularComissaoNoEscopo(escopo) {
        if (!escopo) return;
        const trocoInput = escopo.querySelector('input[name="troco"]');
        const percentualInput = escopo.querySelector('input[name="comissao_percentual"]');
        const comissaoInput = escopo.querySelector('input[name="comissao"]');
        if (!trocoInput || !percentualInput || !comissaoInput) return;

        const percentualTexto = percentualInput.value.trim();
        if (!percentualTexto) return;

        const valor = parseBRNumber(trocoInput.value);
        const percentual = parseBRNumber(percentualTexto);
        const comissao = valor * (percentual / 100);
        comissaoInput.value = formatBRL(comissao);
    }

    document.querySelectorAll('form').forEach((form) => {
        const trocoInput = form.querySelector('input[name="troco"]');
        const percentualInput = form.querySelector('input[name="comissao_percentual"]');
        const comissaoInput = form.querySelector('input[name="comissao"]');

        if (!trocoInput || !percentualInput || !comissaoInput) return;

        percentualInput.addEventListener('input', () => calcularComissaoNoEscopo(form));
        percentualInput.addEventListener('change', () => calcularComissaoNoEscopo(form));
        percentualInput.addEventListener('blur', () => calcularComissaoNoEscopo(form));
        trocoInput.addEventListener('input', () => {
            if (percentualInput.value.trim()) calcularComissaoNoEscopo(form);
        });
        trocoInput.addEventListener('change', () => calcularComissaoNoEscopo(form));
        trocoInput.addEventListener('blur', () => calcularComissaoNoEscopo(form));
    });

    function mostrarAvisoCopiado(mensagem) {
        const aviso = document.createElement('div');
        aviso.textContent = mensagem;
        aviso.className = 'toast-copiado';
        document.body.appendChild(aviso);
        setTimeout(() => aviso.remove(), 1800);
    }

    function copiarTextoFallback(texto, button = null) {
        const campoTemporario = document.createElement('textarea');
        campoTemporario.value = texto;
        campoTemporario.setAttribute('readonly', '');
        campoTemporario.style.position = 'fixed';
        campoTemporario.style.left = '-9999px';
        campoTemporario.style.top = '0';

        document.body.appendChild(campoTemporario);
        campoTemporario.focus();
        campoTemporario.select();
        campoTemporario.setSelectionRange(0, campoTemporario.value.length);

        try {
            const copiou = document.execCommand('copy');
            if (copiou) {
                if (button) {
                    const original = button.textContent;
                    button.textContent = 'Copiado';
                    setTimeout(() => button.textContent = original, 1300);
                }
                mostrarAvisoCopiado('Copiado!');
            } else {
                alert('Não foi possível copiar automaticamente. Texto: ' + texto);
            }
        } catch (error) {
            alert('Não foi possível copiar automaticamente. Texto: ' + texto);
        } finally {
            document.body.removeChild(campoTemporario);
        }
    }

    function copiarTexto(texto, button = null) {
        if (!texto) {
            alert('Nada para copiar.');
            return;
        }

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(texto)
                .then(() => {
                    if (button) {
                        const original = button.textContent;
                        button.textContent = 'Copiado';
                        setTimeout(() => button.textContent = original, 1300);
                    }
                    mostrarAvisoCopiado('Copiado!');
                })
                .catch(() => copiarTextoFallback(texto, button));
        } else {
            copiarTextoFallback(texto, button);
        }
    }

    document.querySelectorAll('.copy-btn').forEach((button) => {
        button.addEventListener('click', () => {
            const texto = button.dataset.copy || '';
            copiarTexto(texto, button);
        });
    });

    let draggedCard = null;

    document.querySelectorAll('.kanban-card[draggable="true"]').forEach((card) => {
        card.addEventListener('dragstart', (event) => {
            draggedCard = card;
            card.classList.add('dragging');
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', card.dataset.propostaId || '');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
            draggedCard = null;
            document.querySelectorAll('.kanban-cards.drop-target').forEach((column) => {
                column.classList.remove('drop-target');
            });
        });
    });

    document.querySelectorAll('.kanban-cards[data-status]').forEach((cardsArea) => {
        cardsArea.addEventListener('dragover', (event) => {
            event.preventDefault();
            cardsArea.classList.add('drop-target');
        });

        cardsArea.addEventListener('dragleave', () => {
            cardsArea.classList.remove('drop-target');
        });

        cardsArea.addEventListener('drop', async (event) => {
            event.preventDefault();
            cardsArea.classList.remove('drop-target');

            const propostaId = event.dataTransfer.getData('text/plain');
            const novoStatus = cardsArea.dataset.status;
            const card = draggedCard || document.querySelector(`.kanban-card[data-proposta-id="${propostaId}"]`);

            if (!propostaId || !novoStatus || !card) return;

            const statusAtual = card.closest('.kanban-cards')?.dataset.status;
            if (statusAtual === novoStatus) return;

            const formData = new URLSearchParams();
            formData.append('status', novoStatus);
            formData.append('origem', 'funil');
            formData.append('observacao', 'Movido no funil por arrastar e soltar');

            try {
                const response = await fetch(`/proposta/${propostaId}/status`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                        'X-Requested-With': 'fetch'
                    },
                    body: formData.toString(),
                    redirect: 'follow'
                });

                let payload = null;
                const contentType = response.headers.get('content-type') || '';
                if (contentType.includes('application/json')) {
                    payload = await response.json();
                }

                if (!response.ok || (payload && payload.ok === false)) {
                    const msg = payload?.erro || `Falha ao mover proposta. Código: ${response.status}`;
                    throw new Error(msg);
                }

                cardsArea.appendChild(card);
                const oldColumn = document.querySelector(`.kanban-cards[data-status="${statusAtual}"]`)?.closest('.kanban-column');
                const newColumn = cardsArea.closest('.kanban-column');
                updateColumnCounter(oldColumn);
                updateColumnCounter(newColumn);
            } catch (error) {
                console.error(error);
                alert(error.message || 'Não foi possível mover o card. Recarregue a página e tente novamente.');
            }
        });
    });

    function updateColumnCounter(column) {
        if (!column) return;
        const counter = column.querySelector('.column-title small');
        if (!counter) return;
        const count = column.querySelectorAll('.kanban-card').length;
        counter.textContent = `${count} proposta(s)`;
    }

});

// v11 - Pesquisa rápida com sugestões por nome, CPF ou telefone.
document.addEventListener('DOMContentLoaded', () => {
    const searchWrap = document.querySelector('.quick-search');
    const input = document.getElementById('quickSearchInput');
    const results = document.getElementById('quickSearchResults');
    if (!searchWrap || !input || !results) return;

    const searchUrl = searchWrap.dataset.searchUrl;
    let timer = null;
    let lastItems = [];

    function hideResults() {
        results.hidden = true;
        results.innerHTML = '';
    }

    function renderResults(items) {
        lastItems = items || [];
        if (!lastItems.length) {
            results.innerHTML = '<div class="quick-search-empty">Nenhum cliente encontrado.</div>';
            results.hidden = false;
            return;
        }

        results.innerHTML = lastItems.map((item) => `
            <a class="quick-search-item" href="${item.url}">
                <strong>${escapeHtml(item.nome)}</strong>
                <small>${escapeHtml(item.cpf || 'CPF não informado')} · ${escapeHtml(item.status || '')}</small>
                <span>${escapeHtml(item.produto || '')}${item.banco ? ' · Banco: ' + escapeHtml(item.banco) : ''}</span>
                <em class="quick-search-match">Encontrado em ${escapeHtml(item.match_campo || 'resultado')}: ${escapeHtml(item.match_valor || '')}</em>
            </a>
        `).join('');
        results.hidden = false;
    }

    function escapeHtml(value) {
        return String(value || '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;')
            .replaceAll("'", '&#039;');
    }

    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) {
            hideResults();
            return;
        }
        timer = setTimeout(async () => {
            try {
                const response = await fetch(`${searchUrl}?q=${encodeURIComponent(q)}`);
                if (!response.ok) throw new Error('Falha na pesquisa');
                renderResults(await response.json());
            } catch (error) {
                console.error(error);
                hideResults();
            }
        }, 180);
    });

    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && lastItems.length) {
            event.preventDefault();
            window.location.href = lastItems[0].url;
        }
        if (event.key === 'Escape') hideResults();
    });

    document.addEventListener('click', (event) => {
        if (!searchWrap.contains(event.target)) hideResults();
    });
});

// v23 - Alternância de modo claro/escuro com preferência salva no navegador.
document.addEventListener('DOMContentLoaded', () => {
    const botaoTema = document.getElementById('themeToggle');
    if (!botaoTema) return;

    function aplicarTema(tema) {
        document.documentElement.setAttribute('data-theme', tema);
        localStorage.setItem('crmTema', tema);
        botaoTema.textContent = tema === 'escuro' ? '☀️ Modo claro' : '🌙 Modo escuro';
        botaoTema.title = tema === 'escuro' ? 'Alternar para modo claro' : 'Alternar para modo escuro';
    }

    const temaAtual = localStorage.getItem('crmTema') || document.documentElement.getAttribute('data-theme') || 'claro';
    aplicarTema(temaAtual);

    botaoTema.addEventListener('click', () => {
        const atual = document.documentElement.getAttribute('data-theme') || 'claro';
        aplicarTema(atual === 'escuro' ? 'claro' : 'escuro');
    });
});

// v27 - Abas internas na tela de detalhes da proposta.
document.addEventListener('DOMContentLoaded', () => {
    const tabs = document.querySelectorAll('.proposal-tab[data-tab-target]');
    const panels = document.querySelectorAll('.proposal-tab-panel[data-tab-panel]');
    if (!tabs.length || !panels.length) return;

    function activateTab(target) {
        tabs.forEach((tab) => {
            tab.classList.toggle('is-active', tab.dataset.tabTarget === target);
        });
        panels.forEach((panel) => {
            const isActive = panel.dataset.tabPanel === target;
            panel.classList.toggle('is-active', isActive);
            panel.hidden = !isActive;
        });
    }

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tabTarget;
            activateTab(target);
            try {
                sessionStorage.setItem('crmProposalTab', target);
            } catch (error) {
                // Ignora navegadores que bloqueiam sessionStorage.
            }
        });
    });

    try {
        const savedTab = sessionStorage.getItem('crmProposalTab');
        if (savedTab && document.querySelector(`.proposal-tab[data-tab-target="${savedTab}"]`)) {
            activateTab(savedTab);
        }
    } catch (error) {
        // Mantém a primeira aba ativa.
    }
});

// v35 - Editor visual de etapas: arrastar, reordenar e salvar tudo de uma vez.
document.addEventListener('DOMContentLoaded', () => {
    const list = document.getElementById('statusEditorList');
    const preview = document.getElementById('statusPreviewLine');
    if (!list || !preview) return;

    let dragging = null;

    function getCards() {
        return Array.from(list.querySelectorAll('[data-status-card="true"]'));
    }

    function atualizarOrdensEPreview() {
        const cards = getCards();
        preview.innerHTML = '';

        cards.forEach((card, index) => {
            const ordemInput = card.querySelector('input[name="ordem"]');
            const nomeInput = card.querySelector('[data-status-name-input]');
            const ativoSelect = card.querySelector('[data-status-active-select]');
            const nome = (nomeInput?.value || 'Sem nome').trim() || 'Sem nome';
            const ativo = (ativoSelect?.value || '1') === '1';

            if (ordemInput) ordemInput.value = String(index + 1);

            const step = document.createElement('div');
            step.className = 'status-preview-step' + (ativo ? '' : ' inactive');
            step.dataset.previewId = card.dataset.etapaId || '';

            const dot = document.createElement('div');
            dot.className = 'status-preview-dot';
            dot.textContent = String(index + 1);

            const label = document.createElement('span');
            label.textContent = nome;

            step.appendChild(dot);
            step.appendChild(label);
            preview.appendChild(step);
        });
    }

    function getDragAfterElement(container, y) {
        const cards = [...container.querySelectorAll('[data-status-card="true"]:not(.dragging)')];
        return cards.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset, element: child };
            }
            return closest;
        }, { offset: Number.NEGATIVE_INFINITY, element: null }).element;
    }

    getCards().forEach((card) => {
        card.addEventListener('dragstart', (event) => {
            dragging = card;
            card.classList.add('dragging');
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', card.dataset.etapaId || '');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
            dragging = null;
            atualizarOrdensEPreview();
        });
    });

    list.addEventListener('dragover', (event) => {
        event.preventDefault();
        if (!dragging) return;
        const afterElement = getDragAfterElement(list, event.clientY);
        if (afterElement == null) {
            list.appendChild(dragging);
        } else {
            list.insertBefore(dragging, afterElement);
        }
    });

    list.addEventListener('input', (event) => {
        if (event.target.matches('[data-status-name-input]')) atualizarOrdensEPreview();
    });

    list.addEventListener('change', (event) => {
        if (event.target.matches('[data-status-active-select]')) atualizarOrdensEPreview();
    });

    atualizarOrdensEPreview();
});

// v41 - Simulador INSS: cálculo automático entre valor e parcela/margem.
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('simuladorInssForm');
    const dataTag = document.getElementById('inssCoeficientes');
    if (!form || !dataTag) return;

    let dados = { novo: {} };
    try { dados = JSON.parse(dataTag.textContent || '{}'); } catch (e) { return; }

    const tipo = document.getElementById('simTipoOperacao');
    const prazo = document.getElementById('simPrazo');
    const valorBase = document.getElementById('simValorBase');
    const margem = document.getElementById('simMargem');
    const valorOut = document.getElementById('simValorEstimado');
    const parcelaOut = document.getElementById('simParcelaEstimativa');
    const coefOut = document.getElementById('simCoeficiente');
    const resumoTexto = document.getElementById('simResumoTexto');
    const copiarResumo = form.querySelector('[data-copy]');

    function parseBR(value) {
        const text = String(value || '').replace('%', '').trim();
        if (!text) return 0;
        if (typeof parseMoneyInputValue === 'function') {
            return parseMoneyInputValue(text);
        }
        return Number(text.replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
    }

    function brl(value) {
        return Number(value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function prazoLabel() {
        const selected = prazo ? prazo.options[prazo.selectedIndex] : null;
        return selected ? (selected.dataset.label || selected.textContent || '') : '';
    }

    function montarMensagem(valor, parcela, descricao) {
        return `Simulação INSS - ${descricao}\n\n` +
            `Valor estimado: ${brl(valor)}\n` +
            `Parcela estimada: ${brl(parcela)}\n` +
            `Prazo: ${prazoLabel()}\n\n` +
            'Valores sujeitos à análise e confirmação do banco.';
    }

    function atualizarResumo(mensagem) {
        if (resumoTexto) resumoTexto.innerHTML = mensagem.replace(/\n/g, '<br>');
        if (copiarResumo) copiarResumo.dataset.copy = mensagem;
    }

    function calcular(campoOrigem = null) {
        if (!tipo || !prazo || !valorBase || !margem) return;

        if (campoOrigem === valorBase) tipo.value = 'novo_valor';
        if (campoOrigem === margem) tipo.value = 'novo_margem';

        const item = dados.novo[prazo.value] || dados.novo['84'] || {};
        const coef = Number(item.coeficiente || 0);
        let valor = 0;
        let parcela = 0;
        let descricao = 'Novo INSS por valor';

        if (tipo.value === 'novo_margem') {
            parcela = parseBR(margem.value);
            valor = coef ? parcela / coef : 0;
            descricao = 'Novo INSS por margem';
            if (campoOrigem === margem && document.activeElement !== valorBase) {
                valorBase.value = brl(valor);
            }
        } else {
            valor = parseBR(valorBase.value);
            parcela = valor * coef;
            descricao = 'Novo INSS por valor';
            if (campoOrigem === valorBase && document.activeElement !== margem) {
                margem.value = brl(parcela);
            }
        }

        if (valorOut) valorOut.textContent = brl(valor);
        if (parcelaOut) parcelaOut.textContent = brl(parcela);
        if (coefOut) coefOut.textContent = coef ? coef.toFixed(6) : '-';
        atualizarResumo(montarMensagem(valor, parcela, descricao));
    }

    if (valorBase) {
        valorBase.addEventListener('input', () => calcular(valorBase));
        valorBase.addEventListener('blur', () => calcular(valorBase));
    }
    if (margem) {
        margem.addEventListener('input', () => calcular(margem));
        margem.addEventListener('blur', () => calcular(margem));
    }
    if (prazo) {
        prazo.addEventListener('change', () => calcular(tipo.value === 'novo_margem' ? margem : valorBase));
    }
    calcular(tipo && tipo.value === 'novo_margem' ? margem : valorBase);
});

// v42 - Seleção de modelos de mensagem na aba Mensagens.
document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('modeloMensagemSelect');
    const items = document.querySelectorAll('.selected-message-item[data-message-index]');
    if (!select || !items.length) return;

    function atualizarModeloSelecionado() {
        const value = select.value;
        items.forEach((item) => {
            item.classList.toggle('hidden', item.dataset.messageIndex !== value);
        });
    }

    select.addEventListener('change', atualizarModeloSelecionado);
    atualizarModeloSelecionado();
});

// v44 - Gerador de mensagens comercial separado, inspirado no gerador desktop antigo.
document.addEventListener('DOMContentLoaded', () => {
    const root = document.getElementById('geradorMensagens');
    if (!root) return;

    let modelos = {};
    try { modelos = JSON.parse(root.dataset.modelos || '{}'); } catch (error) { modelos = {}; }

    const modeloSelect = document.getElementById('gerModeloSelect');
    const nome = document.getElementById('gerNome');
    const banco = document.getElementById('gerBanco');
    const parcelaAntiga = document.getElementById('gerParcelaAntiga');
    const parcelaNova = document.getElementById('gerParcelaNova');
    const troco = document.getElementById('gerTroco');
    const atendente = document.getElementById('gerAtendente');
    const economia = document.getElementById('gerEconomia');
    const saida = document.getElementById('gerMensagemResultado');
    const copiar = document.getElementById('copiarGeradorBtn');
    const gerar = document.getElementById('gerarMensagemBtn');
    const limpar = document.getElementById('limparGeradorBtn');

    function parseMoneyGerador(value) {
        let text = String(value || '').replace('R$', '').replace(/\s/g, '').trim();
        if (!text) return 0;
        if (text.includes(',')) {
            text = text.replace(/\./g, '').replace(',', '.');
            return Number(text) || 0;
        }
        if (/^\d{1,3}(\.\d{3})+$/.test(text)) {
            text = text.replace(/\./g, '');
            return Number(text) || 0;
        }
        return Number(text) || 0;
    }

    function brl(value) {
        return Number(value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function calcularEconomia() {
        const antiga = parseMoneyGerador(parcelaAntiga?.value);
        const nova = parseMoneyGerador(parcelaNova?.value);
        const valor = antiga - nova;
        if (economia) economia.value = valor > 0 ? brl(valor) : brl(0);
        return valor > 0 ? valor : 0;
    }

    function preencherModelo(modelo, dados) {
        return String(modelo || '').replace(/\{(nome|banco|parcela_antiga|parcela_nova|troco|valor|economia|atendente)\}/g, (match, key) => dados[key] ?? '');
    }

    function gerarMensagem() {
        const modeloNome = modeloSelect?.value || Object.keys(modelos)[0];
        const modelo = modelos[modeloNome] || '';
        const eco = calcularEconomia();
        const dados = {
            nome: nome?.value.trim() || '',
            banco: banco?.value.trim() || '',
            parcela_antiga: brl(parseMoneyGerador(parcelaAntiga?.value)),
            parcela_nova: brl(parseMoneyGerador(parcelaNova?.value)),
            troco: brl(parseMoneyGerador(troco?.value)),
            valor: brl(parseMoneyGerador(troco?.value)),
            economia: brl(eco),
            atendente: atendente?.value.trim() || '',
        };
        const mensagem = preencherModelo(modelo, dados);
        if (saida) saida.value = mensagem;
        if (copiar) copiar.dataset.copy = mensagem;
        return mensagem;
    }

    [modeloSelect, nome, banco, parcelaAntiga, parcelaNova, troco, atendente].forEach((field) => {
        if (!field) return;
        field.addEventListener('input', gerarMensagem);
        field.addEventListener('change', gerarMensagem);
        field.addEventListener('blur', gerarMensagem);
    });

    if (gerar) gerar.addEventListener('click', gerarMensagem);
    if (limpar) {
        limpar.addEventListener('click', () => {
            [nome, banco, parcelaAntiga, parcelaNova, troco].forEach((field) => { if (field) field.value = ''; });
            if (atendente) atendente.value = 'Poliana';
            if (economia) economia.value = '';
            if (saida) saida.value = '';
            if (copiar) copiar.dataset.copy = '';
        });
    }

    gerarMensagem();
});

