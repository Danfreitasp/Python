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
        matriculaSelect.innerHTML = '<option value="">Selecione uma matrícula cadastrada</option>';

        clientes.forEach((cliente, index) => {
            const option = document.createElement('option');
            option.value = String(index);
            option.textContent = cliente.label || `Matrícula ${index + 1}`;
            matriculaSelect.appendChild(option);
        });

        const nova = document.createElement('option');
        nova.value = 'nova';
        nova.textContent = 'Cadastrar nova matrícula';
        matriculaSelect.appendChild(nova);
    }

    async function buscarClientesPorCpf() {
        if (!cpfField || !matriculaSelect) return;
        const consultaAtual = ++ultimaConsultaClientes;
        const digits = cpfField.value.replace(/\D/g, '');

        matriculaSelect.classList.add('hidden');
        matriculaSelect.innerHTML = '<option value="">Selecione uma matrícula cadastrada</option>';
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
            if (clienteAjuda) clienteAjuda.textContent = 'CPF já cadastrado. Selecione uma matrícula ou cadastre uma nova.';
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
                if (clienteAjuda) clienteAjuda.textContent = 'Nova matrícula: dados básicos reaproveitados. Informe a matrícula nova.';
                return;
            }
            const cliente = clientesCPFCache[Number(value)];
            if (cliente) {
                preencherDadosCliente(cliente, false);
                if (clienteAjuda) clienteAjuda.textContent = 'Dados do cliente preenchidos automaticamente.';
            }
        });
    }


    document.querySelectorAll('.money-mask').forEach((input) => {
        input.addEventListener('blur', () => {
            const digits = input.value.replace(/\D/g, '');
            if (!digits) {
                input.value = 'R$ 0,00';
                return;
            }
            const number = Number(digits) / 100;
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

    const trocoInput = document.querySelector('input[name="troco"]');
    const percentualInput = document.querySelector('input[name="comissao_percentual"]');
    const comissaoInput = document.querySelector('input[name="comissao"]');

    function parseBRNumber(value) {
        const text = String(value || '').replace('R$', '').replace('%', '').trim();
        if (!text) return 0;
        return Number(text.replace(/\./g, '').replace(',', '.')) || 0;
    }

    function formatBRL(number) {
        return Number(number || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    }

    function calcularComissaoAutomatica() {
        if (!trocoInput || !percentualInput || !comissaoInput) return;
        const percentualTexto = percentualInput.value.trim();
        if (!percentualTexto) return;
        const troco = parseBRNumber(trocoInput.value);
        const percentual = parseBRNumber(percentualTexto);
        const comissao = troco * (percentual / 100);
        comissaoInput.value = formatBRL(comissao);
    }

    if (trocoInput && percentualInput && comissaoInput) {
        percentualInput.addEventListener('input', calcularComissaoAutomatica);
        percentualInput.addEventListener('blur', calcularComissaoAutomatica);
        trocoInput.addEventListener('blur', calcularComissaoAutomatica);
    }

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
