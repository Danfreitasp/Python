document.addEventListener('DOMContentLoaded', () => {
    const propostaFormGrid = document.getElementById('propostaFormGrid');
    if (propostaFormGrid) {
        const labels = Array.from(propostaFormGrid.children).filter((item) => item.tagName === 'LABEL');
        const localizarCampo = (name) => labels.find((label) => label.querySelector(`[name="${name}"]`));
        const grupos = [
            ['Dados do cliente', ['nome', 'cpf', 'nascimento', 'nb_matricula', 'especie', 'tipo_cliente', 'telefone']],
            ['Dados da proposta', ['numero_proposta', 'produto', 'banco_atual', 'banco_digitado', 'status', 'parcela_atual', 'nova_parcela', 'margem_apos', 'troco', 'numero_port_vinculada', 'numero_refin_vinculada', 'data_retorno']],
            ['Dados da promotora', ['promotora', 'beneficio_bloqueado', 'valor_caiu_promotora', 'valor_sacado', 'comissao_percentual', 'comissao']],
        ];
        const usados = new Set();
        const fragment = document.createDocumentFragment();
        grupos.forEach(([titulo, campos]) => {
            const coluna = document.createElement('section');
            coluna.className = 'proposal-form-column';
            coluna.innerHTML = `<h3>${titulo}</h3><div class="proposal-form-column-fields"></div>`;
            const destino = coluna.querySelector('.proposal-form-column-fields');
            campos.forEach((name) => {
                const campo = localizarCampo(name);
                if (campo) { destino.appendChild(campo); usados.add(campo); }
            });
            fragment.appendChild(coluna);
        });
        labels.filter((label) => !usados.has(label)).forEach((label) => fragment.appendChild(label));
        propostaFormGrid.replaceChildren(fragment);
        propostaFormGrid.classList.add('proposal-form-columns');
    }

    const produtoSelect = document.getElementById('propostaProduto');
    if (produtoSelect) {
        const atualizarCamposPortabilidade = () => {
            const produto = (produtoSelect.value || '').toLocaleLowerCase('pt-BR');
            const portabilidade = ['portabilidade', 'portabilidade com refinanciamento'].includes(produto);
            const portabilidadeComRefin = produto === 'portabilidade com refinanciamento';
            const refinVinculado = propostaFormGrid?.dataset.refinVinculado === 'true';
            document.querySelectorAll('[data-portability-field]').forEach((campo) => { campo.hidden = !portabilidade; });
            document.querySelectorAll('[data-linked-refin-field]').forEach((campo) => { campo.hidden = !portabilidadeComRefin; });
            document.querySelectorAll('[data-refin-vinculado-field]').forEach((campo) => { campo.hidden = !(produto === 'refinanciamento' && refinVinculado); });
        };
        produtoSelect.addEventListener('change', atualizarCamposPortabilidade);
        atualizarCamposPortabilidade();
    }

    const weekTimeline = document.querySelector('[data-week-timeline]');
    if (weekTimeline) {
        const esconderDestaquesSemana = () => {
            weekTimeline.querySelectorAll('.week-hover-slot').forEach((item) => { item.hidden = true; });
        };
        const now = new Date();
        const localDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
        const minute = now.getHours() * 60 + now.getMinutes();
        const top = Math.max(0, (minute - 420) * 64 / 60);
        const todayLane = weekTimeline.querySelector(`[data-week-day="${localDate}"]`);
        const nowLine = todayLane?.querySelector('[data-week-now-line]');
        if (nowLine && minute >= 420 && minute <= 1260) nowLine.style.setProperty('--now-top', `${top}px`);
        if (todayLane && minute >= 420 && minute <= 1260) weekTimeline.scrollTop = Math.max(0, top - 170);

        weekTimeline.querySelectorAll('.week-empty-slot').forEach((slot) => {
            const lane = slot.closest('.week-day-lane');
            if (!lane) return;
            const hoverSlot = document.createElement('span');
            hoverSlot.className = 'week-hover-slot';
            hoverSlot.hidden = true;
            lane.appendChild(hoverSlot);

            function horarioDoPonteiro(event) {
                const offset = event.clientY - lane.getBoundingClientRect().top;
                const rawMinute = 420 + (offset * 60 / 64);
                return Math.max(420, Math.min(1245, Math.round(rawMinute / 15) * 15));
            }

            function mostrarHorario(event) {
                weekTimeline.querySelectorAll('.week-hover-slot').forEach((item) => {
                    if (item !== hoverSlot) item.hidden = true;
                });
                const rounded = horarioDoPonteiro(event);
                const horario = `${String(Math.floor(rounded / 60)).padStart(2, '0')}:${String(rounded % 60).padStart(2, '0')}`;
                hoverSlot.style.setProperty('--hover-top', `${(rounded - 420) * 64 / 60}px`);
                hoverSlot.textContent = `${horario} · Criar compromisso`;
                hoverSlot.hidden = false;
            }

            slot.addEventListener('mouseenter', mostrarHorario);
            slot.addEventListener('mousemove', mostrarHorario);
            slot.addEventListener('mouseleave', () => { hoverSlot.hidden = true; });
            lane.addEventListener('mouseleave', () => { hoverSlot.hidden = true; });
            slot.addEventListener('click', (event) => {
                event.preventDefault();
                const rounded = horarioDoPonteiro(event);
                const horario = `${String(Math.floor(rounded / 60)).padStart(2, '0')}:${String(rounded % 60).padStart(2, '0')}`;
                const target = new URL(slot.href, window.location.origin);
                target.searchParams.set('horario', horario);
                window.location.href = target.toString();
            });
        });
        weekTimeline.addEventListener('mouseleave', esconderDestaquesSemana);
    }

    const notifyCheckbox = document.getElementById('taskNotify');
    const notificationPermission = document.getElementById('notificationPermission');
    const notificationTest = document.getElementById('notificationTest');
    function atualizarEstadoNotificacao() {
        if (!notificationPermission) return;
        if (!('Notification' in window)) {
            notificationPermission.textContent = 'Este navegador não oferece notificações. O CRM exibirá o alerta dentro da página.';
        } else if (Notification.permission === 'granted') {
            notificationPermission.textContent = 'Permissão concedida: o alerta aparecerá no CRM e como notificação do navegador.';
        } else if (Notification.permission === 'denied') {
            notificationPermission.textContent = 'Notificações do navegador estão bloqueadas. O lembrete aparecerá dentro do CRM.';
        } else {
            notificationPermission.textContent = 'Ao marcar esta opção, permita as notificações quando o navegador solicitar.';
        }
    }

    async function pedirPermissaoNotificacao() {
        if (!('Notification' in window) || Notification.permission !== 'default') return;
        await Notification.requestPermission();
        atualizarEstadoNotificacao();
    }

    if (notifyCheckbox) {
        notifyCheckbox.addEventListener('change', () => {
            if (notifyCheckbox.checked) pedirPermissaoNotificacao();
        });
    }
    atualizarEstadoNotificacao();
    if (notificationTest) {
        notificationTest.addEventListener('click', async () => {
            await pedirPermissaoNotificacao();
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('CRM: teste de notificação', { body: 'As notificações do navegador estão funcionando.', icon: '/static/favicon.svg' });
                mostrarAvisoCopiado('Teste enviado também como notificação do navegador.');
            } else {
                mostrarAvisoCopiado('O navegador bloqueou o alerta externo. O CRM continuará exibindo os lembretes dentro da página.', 'erro');
            }
        });
    }

    async function verificarLembretesAgenda() {
        try {
            const response = await fetch('/api/agenda/lembretes', { headers: { Accept: 'application/json' } });
            if (!response.ok) return;
            const payload = await response.json();
            const lembretes = Array.isArray(payload.lembretes) ? payload.lembretes : [];
            if (!lembretes.length) return;
            const ids = [];
            lembretes.forEach((lembrete) => {
                const vinculo = lembrete.proposta_nome ? ` — ${lembrete.proposta_nome}` : '';
                const mensagem = `Lembrete ${lembrete.horario}: ${lembrete.titulo}${vinculo}`;
                mostrarAvisoCopiado(mensagem, 'erro');
                if ('Notification' in window && Notification.permission === 'granted') {
                    new Notification(`CRM: ${lembrete.titulo}`, {
                        body: `${lembrete.horario}${vinculo}${lembrete.descricao ? `\n${lembrete.descricao}` : ''}`,
                        icon: '/static/favicon.svg', tag: `crm-lembrete-${lembrete.id}`,
                    });
                }
                ids.push(lembrete.id);
            });
            await fetch('/api/agenda/lembretes/confirmar', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ids }),
            });
        } catch (error) {
            console.warn('Não foi possível verificar os lembretes da agenda.', error);
        }
    }
    verificarLembretesAgenda();
    window.setInterval(verificarLembretesAgenda, 30000);

    const notificationMenu = document.querySelector('.notification-menu');
    if (notificationMenu) {
        document.addEventListener('click', (event) => {
            if (!notificationMenu.contains(event.target)) notificationMenu.open = false;
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') notificationMenu.open = false;
        });
    }

    const notificationPanelContent = document.getElementById('notificationPanelContent');
    const notificationBadge = document.querySelector('.notification-badge');
    async function atualizarNotificacoesAutomaticamente() {
        if (!notificationPanelContent || document.hidden) return;
        try {
            const url = new URL('/api/notificacoes', window.location.origin);
            url.searchParams.set('origem', `${window.location.pathname}${window.location.search}`);
            const response = await fetch(url, { headers: { Accept: 'application/json' } });
            if (!response.ok) return;
            const payload = await response.json();
            notificationPanelContent.innerHTML = payload.html || '';
            if (notificationBadge) {
                notificationBadge.textContent = String(payload.total || '');
                notificationBadge.hidden = !payload.total;
            }
        } catch (error) {
            console.warn('Não foi possível atualizar as notificações.', error);
        }
    }
    window.setInterval(atualizarNotificacoesAutomaticamente, 15000);
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) atualizarNotificacoesAutomaticamente();
    });

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
        matriculaSelect.innerHTML = '';

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
        matriculaSelect.innerHTML = '';
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

    function mostrarAvisoCopiado(mensagem, tipo = 'ok') {
        const aviso = document.createElement('div');
        aviso.textContent = mensagem;
        aviso.className = `crm-toast toast-copiado ${tipo === 'erro' ? 'toast-erro' : 'toast-ok'}`;
        document.body.appendChild(aviso);
        setTimeout(() => aviso.remove(), tipo === 'erro' ? 3200 : 1800);
    }

    document.querySelectorAll('[data-toast="true"]').forEach((alerta, index) => {
        alerta.classList.add('crm-toast');
        document.body.appendChild(alerta);
        alerta.style.marginTop = `${index * 58}px`;
        setTimeout(() => alerta.remove(), 3200);
    });

    document.querySelectorAll('.alerts').forEach((alerts) => {
        if (!alerts.querySelector('.alert')) alerts.remove();
    });

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
                    const original = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check-circle" aria-hidden="true"></i><span>Copiado</span>';
                    setTimeout(() => button.innerHTML = original, 1300);
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
                        const original = button.innerHTML;
                        button.innerHTML = '<i class="bi bi-check-circle" aria-hidden="true"></i><span>Copiado</span>';
                        setTimeout(() => button.innerHTML = original, 1300);
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
    const funilContextKey = 'crmFunilContext';

    function funilUrlSemDestaque() {
        const url = new URL(window.location.href);
        url.searchParams.delete('destaque_proposta');
        return `${url.pathname}${url.search}`;
    }

    function limparDestaqueDaUrl() {
        const url = new URL(window.location.href);
        if (!url.searchParams.has('destaque_proposta')) return;
        url.searchParams.delete('destaque_proposta');
        const limpa = `${url.pathname}${url.search}${url.hash}`;
        window.history.replaceState({}, '', limpa);
    }

    function salvarContextoFunil(card = null) {
        const kanban = document.querySelector('.kanban[data-modulo="funil"]');
        if (!kanban) return;

        const colunas = {};
        kanban.querySelectorAll('.kanban-cards[data-status]').forEach((area) => {
            colunas[area.dataset.status] = area.scrollTop || 0;
        });

        try {
            sessionStorage.setItem(funilContextKey, JSON.stringify({
                url: funilUrlSemDestaque(),
                at: Date.now(),
                pageX: window.scrollX || 0,
                pageY: window.scrollY || 0,
                kanbanX: kanban.scrollLeft || 0,
                colunas,
                propostaId: card?.dataset.propostaId || '',
            }));
        } catch (error) {
            // Se o navegador bloquear sessionStorage, o CRM apenas segue sem restaurar posição.
        }
    }

    function destacarCardRecemSalvo(card) {
        if (!card) return;
        card.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
        card.classList.add('card-recently-saved');
        setTimeout(() => card.classList.remove('card-recently-saved'), 3500);
    }

    function propostaSelector(propostaId) {
        const seguro = String(propostaId || '').replace(/\\/g, '\\\\').replace(/"/g, '\\"');
        return `[data-proposta-id="${seguro}"]`;
    }

    function destacarCardDaPaginaAtual() {
        const params = new URLSearchParams(window.location.search);
        const destaqueId = params.get('destaque_proposta');
        if (!destaqueId) return;
        const card = document.querySelector(`.today-card${propostaSelector(destaqueId)}`) || document.querySelector(propostaSelector(destaqueId));
        if (card) destacarCardRecemSalvo(card);
        limparDestaqueDaUrl();
    }

    function restaurarContextoFunil() {
        const kanban = document.querySelector('.kanban[data-modulo="funil"]');
        if (!kanban) return;

        const params = new URLSearchParams(window.location.search);
        const destaqueId = params.get('destaque_proposta');
        let estado = null;

        try {
            estado = JSON.parse(sessionStorage.getItem(funilContextKey) || 'null');
        } catch (error) {
            estado = null;
        }

        const estadoRecente = estado && (Date.now() - Number(estado.at || 0)) < 30 * 60 * 1000;
        const mesmaUrl = estadoRecente && estado.url === funilUrlSemDestaque();

        if (mesmaUrl) {
            requestAnimationFrame(() => {
                window.scrollTo(estado.pageX || 0, estado.pageY || 0);
                kanban.scrollLeft = estado.kanbanX || 0;
                kanban.querySelectorAll('.kanban-cards[data-status]').forEach((area) => {
                    area.scrollTop = estado.colunas?.[area.dataset.status] || 0;
                });
            });
            try { sessionStorage.removeItem(funilContextKey); } catch (error) {}
        }

        if (destaqueId) {
            const card = kanban.querySelector(`.kanban-card${propostaSelector(destaqueId)}`);
            if (card) {
                setTimeout(() => destacarCardRecemSalvo(card), mesmaUrl ? 120 : 0);
            }
            limparDestaqueDaUrl();
        }
    }

    document.querySelectorAll('.kanban[data-modulo="funil"] .kanban-card a[href]').forEach((link) => {
        link.addEventListener('click', () => {
            salvarContextoFunil(link.closest('.kanban-card'));
        });
    });

    restaurarContextoFunil();
    destacarCardDaPaginaAtual();

    function updateTodayCount(name, delta) {
        document.querySelectorAll(`[data-today-count="${name}"]`).forEach((el) => {
            const current = Number(el.textContent || 0);
            el.textContent = String(Math.max(0, current + delta));
        });
    }

    function refreshTodaySection(section) {
        if (!section) return;
        const count = section.querySelectorAll('.today-card').length;
        const countEl = section.querySelector('[data-section-count]');
        if (countEl) countEl.textContent = String(count);
        const grid = section.querySelector('.today-card-grid');
        if (grid && count === 0 && !grid.querySelector('[data-empty-message]')) {
            const empty = document.createElement('p');
            empty.className = 'empty small';
            empty.dataset.emptyMessage = 'true';
            empty.textContent = section.dataset.todaySection === 'verificar'
                ? 'Nenhuma proposta para verificar.'
                : 'Nenhuma proposta nesta seção.';
            grid.appendChild(empty);
        }
    }

    function setTodayCardVerified(card, statusText) {
        const dot = card.querySelector('.verification-dot');
        if (dot) {
            dot.classList.remove('dot-pending');
            dot.classList.add('dot-ok');
            dot.title = statusText || 'Verificado hoje';
        }
        const form = card.querySelector('.today-verify-form');
        if (form) {
            const label = document.createElement('span');
            label.className = 'today-verified-label';
            label.textContent = statusText || 'Verificada hoje';
            form.replaceWith(label);
        }
    }

    document.querySelectorAll('.today-verify-form').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const button = form.querySelector('button');
            if (button) button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'fetch' },
                    body: new FormData(form),
                });
                const payload = await response.json();
                if (!response.ok || payload.success === false) {
                    throw new Error(payload.message || 'Não foi possível marcar como verificada.');
                }

                const params = new URLSearchParams(window.location.search);
                const somentePendentes = params.get('verificacao') === 'pendente';
                let removidasVerificar = 0;
                const cardsDaProposta = Array.from(document.querySelectorAll(propostaSelector(payload.proposta_id)));
                cardsDaProposta.forEach((card) => {
                    setTodayCardVerified(card, payload.status_texto);
                    if (somentePendentes || card.dataset.section === 'verificar') {
                        const section = card.closest('[data-today-section]');
                        if (card.dataset.section === 'verificar') removidasVerificar += 1;
                        card.remove();
                        refreshTodaySection(section);
                    }
                });
                const aindaVisivel = Boolean(document.querySelector(propostaSelector(payload.proposta_id)));
                if (removidasVerificar) {
                    updateTodayCount('verificar', -removidasVerificar);
                }
                if (!aindaVisivel) {
                    updateTodayCount('total', -1);
                }
                if (cardsDaProposta.length) {
                    updateTodayCount('verificadas', 1);
                    updateTodayCount('pendentes', -1);
                }
                mostrarAvisoCopiado(payload.message || 'Verificação diária atualizada.');
            } catch (error) {
                console.error(error);
                if (button) button.disabled = false;
                mostrarAvisoCopiado(error.message || 'Não foi possível marcar como verificada.', 'erro');
            }
        });
    });

    document.querySelectorAll('.today-contact-form').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const button = form.querySelector('button');
            const card = form.closest('.today-card');
            const section = card?.closest('[data-today-section]');
            if (button) button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'fetch' },
                    body: new FormData(form),
                });
                const payload = await response.json();
                if (!response.ok || payload.success === false) {
                    throw new Error(payload.message || 'Não foi possível registrar o contato.');
                }

                const lastInteraction = card?.querySelector('[data-last-interaction]');
                if (lastInteraction) lastInteraction.textContent = `Última interação: ${payload.ultima_interacao || 'Hoje'}`;

                const label = document.createElement('span');
                label.className = 'today-verified-label';
                label.textContent = 'Contatado hoje';
                form.replaceWith(label);

                updateTodayCount('interacoes_hoje', 1);
                updateTodayCount('pendentes', -1);

                const params = new URLSearchParams(window.location.search);
                const somentePendentes = params.get('verificacao') === 'pendente';
                if (card && (somentePendentes || card.dataset.section === 'paradas')) {
                    const sectionKey = card.dataset.section;
                    card.remove();
                    refreshTodaySection(section);
                    updateTodayCount('total', -1);
                    if (sectionKey === 'paradas') updateTodayCount('paradas', -1);
                }

                mostrarAvisoCopiado(payload.message || 'Contato registrado.');
            } catch (error) {
                console.error(error);
                if (button) button.disabled = false;
                mostrarAvisoCopiado(error.message || 'Não foi possível registrar o contato.', 'erro');
            }
        });
    });

    function updateAgendaCount(name, delta) {
        document.querySelectorAll(`[data-agenda-count="${name}"]`).forEach((el) => {
            const current = Number(el.textContent || 0);
            el.textContent = String(Math.max(0, current + delta));
        });
    }

    function refreshAgendaSection(section) {
        if (!section) return;
        const count = section.querySelectorAll('.agenda-item').length;
        const countEl = section.querySelector('[data-agenda-section-count]');
        if (countEl) countEl.textContent = String(count);
        const list = section.querySelector('.agenda-list');
        if (list && count === 0 && !list.querySelector('[data-empty-message]')) {
            const empty = document.createElement('p');
            empty.className = 'empty small';
            empty.dataset.emptyMessage = 'true';
            empty.textContent = 'Nenhuma proposta nesta seção.';
            list.appendChild(empty);
        }
    }

    function agendaCountName(sectionKey) {
        if (sectionKey === 'agenda_atrasadas') return 'atrasadas';
        if (sectionKey === 'agenda_hoje') return 'hoje';
        if (sectionKey === 'agenda_proximas') return 'proximas';
        if (sectionKey === 'agenda_concluidas') return 'concluidas_hoje';
        return '';
    }

    document.querySelectorAll('.agenda-action-form, .agenda-delay-form').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const item = form.closest('.agenda-item');
            const section = item?.closest('[data-agenda-section]');
            const button = form.querySelector('button');
            if (button) button.disabled = true;
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'fetch' },
                    body: new FormData(form),
                });
                const payload = await response.json();
                if (!response.ok || payload.success === false) {
                    throw new Error(payload.message || 'Não foi possível atualizar a tarefa.');
                }
                if (item) item.remove();
                refreshAgendaSection(section);
                const countName = agendaCountName(section?.dataset.agendaSection || '');
                if (countName) updateAgendaCount(countName, -1);
                if (payload.status === 'concluida') updateAgendaCount('concluidas_hoje', 1);
                mostrarAvisoCopiado(payload.message || 'Tarefa atualizada.');
            } catch (error) {
                console.error(error);
                if (button) button.disabled = false;
                mostrarAvisoCopiado(error.message || 'Não foi possível atualizar a tarefa.', 'erro');
            }
        });
    });

    document.querySelectorAll('.agenda-delete-form').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            if (!window.confirm('Excluir esta tarefa?')) return;
            const item = form.closest('.agenda-item');
            const section = item?.closest('[data-agenda-section]');
            const button = form.querySelector('button');
            if (button) button.disabled = true;
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'fetch' },
                    body: new FormData(form),
                });
                const payload = await response.json();
                if (!response.ok || payload.success === false) {
                    throw new Error(payload.message || 'Não foi possível excluir a tarefa.');
                }
                if (item) item.remove();
                refreshAgendaSection(section);
                const countName = agendaCountName(section?.dataset.agendaSection || '');
                if (countName) updateAgendaCount(countName, -1);
                mostrarAvisoCopiado(payload.message || 'Tarefa excluída.');
            } catch (error) {
                console.error(error);
                if (button) button.disabled = false;
                mostrarAvisoCopiado(error.message || 'Não foi possível excluir a tarefa.', 'erro');
            }
        });
    });

    const taskLinkBox = document.querySelector('.task-link-box');
    if (taskLinkBox) {
        const searchInput = document.getElementById('taskProposalSearch');
        const results = document.getElementById('taskProposalResults');
        const propostaInput = document.getElementById('taskPropostaId');
        const selected = document.getElementById('taskSelectedProposal');
        const clearButton = document.getElementById('clearTaskProposal');
        const searchUrl = taskLinkBox.dataset.propostaSearchUrl;
        let timer = null;

        function escapeHtmlTask(value) {
            return String(value || '')
                .replaceAll('&', '&amp;')
                .replaceAll('<', '&lt;')
                .replaceAll('>', '&gt;')
                .replaceAll('"', '&quot;')
                .replaceAll("'", '&#039;');
        }

        function hideTaskResults() {
            if (!results) return;
            results.hidden = true;
            results.innerHTML = '';
        }

        function selectTaskProposal(item) {
            if (propostaInput) propostaInput.value = item.id || '';
            if (selected) selected.textContent = `${item.nome || 'Proposta'}${item.cpf ? ' · ' + item.cpf : ''}`;
            hideTaskResults();
        }

        if (clearButton) {
            clearButton.addEventListener('click', () => {
                if (propostaInput) propostaInput.value = '';
                if (selected) selected.textContent = 'Nenhuma proposta vinculada.';
                if (searchInput) searchInput.value = '';
                hideTaskResults();
            });
        }

        if (searchInput && results && searchUrl) {
            searchInput.addEventListener('input', () => {
                clearTimeout(timer);
                const q = searchInput.value.trim();
                if (q.length < 2) {
                    hideTaskResults();
                    return;
                }
                timer = setTimeout(async () => {
                    try {
                        const response = await fetch(`${searchUrl}?q=${encodeURIComponent(q)}`);
                        if (!response.ok) throw new Error('Falha ao buscar proposta.');
                        const items = await response.json();
                        if (!items.length) {
                            results.innerHTML = '<div class="quick-search-empty">Nenhuma proposta encontrada.</div>';
                            results.hidden = false;
                            return;
                        }
                        results.innerHTML = items.map((item) => `
                            <button type="button" class="task-proposal-result" data-proposta='${escapeHtmlTask(JSON.stringify(item))}'>
                                <strong>${escapeHtmlTask(item.nome)}</strong>
                                <small>${escapeHtmlTask(item.cpf || 'CPF não informado')} · ${escapeHtmlTask(item.status || '')}</small>
                                <span>${escapeHtmlTask(item.match_campo || 'Resultado')}: ${escapeHtmlTask(item.match_valor || '')}</span>
                            </button>
                        `).join('');
                        results.hidden = false;
                    } catch (error) {
                        console.error(error);
                        hideTaskResults();
                    }
                }, 180);
            });

            results.addEventListener('click', (event) => {
                const button = event.target.closest('.task-proposal-result');
                if (!button) return;
                try {
                    selectTaskProposal(JSON.parse(button.dataset.proposta || '{}'));
                } catch (error) {
                    hideTaskResults();
                }
            });
        }
    }

    function getColumn(cardsArea) {
        return cardsArea?.closest('.kanban-column') || null;
    }

    function refreshEmptyState(cardsArea) {
        if (!cardsArea) return;
        const empty = cardsArea.querySelector('[data-empty-message]');
        const hasCards = Boolean(cardsArea.querySelector('.kanban-card'));
        if (hasCards && empty) {
            empty.remove();
        } else if (!hasCards && !empty) {
            const message = document.createElement('p');
            message.className = 'empty small';
            message.dataset.emptyMessage = 'true';
            message.textContent = 'Sem propostas.';
            cardsArea.appendChild(message);
        }
    }

    function appendCard(cardsArea, card) {
        const empty = cardsArea.querySelector('[data-empty-message]');
        if (empty) empty.remove();
        cardsArea.appendChild(card);
    }

    function restoreCard(card, sourceArea, nextSibling) {
        if (nextSibling && nextSibling.parentElement === sourceArea) {
            sourceArea.insertBefore(card, nextSibling);
        } else {
            sourceArea.appendChild(card);
        }
    }

    function updateColumnCounter(column, dados = null) {
        if (!column) return;
        const countEl = column.querySelector('[data-column-count]') || column.querySelector('.column-title small');
        const commissionEl = column.querySelector('[data-column-commission]');
        if (countEl) {
            const count = dados ? dados.quantidade : column.querySelectorAll('.kanban-card').length;
            countEl.textContent = `${count} proposta(s)`;
        }
        if (commissionEl && dados?.comissao) {
            commissionEl.textContent = dados.comissao;
        }
    }

    function formatarMoeda(valor) {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(valor) || 0);
    }

    function atualizarResumoEncerradas(coluna) {
        if (!coluna?.closest('.kanban[data-modulo="encerradas"]')) return;
        const cards = coluna.querySelectorAll('.encerrada-card');
        const total = Array.from(cards).reduce((soma, card) => soma + (Number(card.dataset.comissao) || 0), 0);
        updateColumnCounter(coluna);
        const comissao = coluna.querySelector('[data-column-commission]');
        if (comissao) comissao.textContent = formatarMoeda(total);
    }

    function atualizarVisualStatusEncerrada(card, destino) {
        if (!card?.classList.contains('encerrada-card')) return;
        const perdido = destino === 'Perdido / Cancelado';
        card.classList.toggle('card-paid', !perdido);
        card.classList.toggle('card-lost', perdido);
    }

    document.querySelectorAll('.encerrada-finance-form').forEach((form) => {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const card = form.closest('.encerrada-card');
            const button = form.querySelector('button[type="submit"]');
            if (!card || !button) return;
            button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'fetch' },
                    body: new FormData(form),
                });
                const payload = await response.json();
                if (!response.ok || payload.success === false) throw new Error(payload.message || 'Não foi possível atualizar os valores.');

                card.dataset.comissao = String(payload.comissao_numero || 0);
                card.querySelector('[data-finance-value]').textContent = payload.troco;
                card.querySelector('[data-finance-commission]').textContent = payload.comissao;
                card.querySelector('[data-finance-percent]').textContent = payload.comissao_percentual;
                card.querySelector('.encerrada-finance-editor').open = false;
                atualizarResumoEncerradas(card.closest('.kanban-column'));
                card.classList.add('card-recently-saved');
                setTimeout(() => card.classList.remove('card-recently-saved'), 1400);
                mostrarAvisoCopiado(payload.message || 'Valores atualizados.');
            } catch (error) {
                console.error(error);
                mostrarAvisoCopiado(error.message || 'Não foi possível atualizar os valores.', 'erro');
            } finally {
                button.disabled = false;
            }
        });
    });

    function restoreScroll(kanban, scrollLeft, sourceArea, sourceScrollTop, targetArea, targetScrollTop) {
        requestAnimationFrame(() => {
            if (kanban) kanban.scrollLeft = scrollLeft;
            if (sourceArea) sourceArea.scrollTop = sourceScrollTop;
            if (targetArea) targetArea.scrollTop = targetScrollTop;
        });
    }

    document.querySelectorAll('.kanban-card[draggable="true"]').forEach((card) => {
        card.addEventListener('dragstart', (event) => {
            if (card.dataset.busy === 'true') {
                event.preventDefault();
                return;
            }
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

            if (!propostaId || !novoStatus || !card || card.dataset.busy === 'true') return;

            const sourceArea = card.closest('.kanban-cards');
            const statusAtual = sourceArea?.dataset.status;
            if (!sourceArea || statusAtual === novoStatus) return;

            const sourceColumn = getColumn(sourceArea);
            const targetColumn = getColumn(cardsArea);
            const nextSibling = card.nextElementSibling;
            const kanban = cardsArea.closest('.kanban');
            const kanbanScrollLeft = kanban?.scrollLeft || 0;
            const sourceScrollTop = sourceArea.scrollTop;
            const targetScrollTop = cardsArea.scrollTop;
            const modulo = kanban?.dataset.modulo || 'funil';

            const formData = new URLSearchParams();
            formData.append('status', novoStatus);
            formData.append('origem', modulo);
            formData.append('observacao', 'Movido no funil por arrastar e soltar');

            card.dataset.busy = 'true';
            card.classList.add('is-processing');
            card.setAttribute('draggable', 'false');
            appendCard(cardsArea, card);
            refreshEmptyState(sourceArea);
            refreshEmptyState(cardsArea);
            restoreScroll(kanban, kanbanScrollLeft, sourceArea, sourceScrollTop, cardsArea, targetScrollTop);

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

                const success = payload ? (payload.success ?? payload.ok) : response.ok;
                if (!response.ok || success === false) {
                    const msg = payload?.message || payload?.erro || `Falha ao mover proposta. Código: ${response.status}`;
                    throw new Error(msg);
                }

                if (modulo === 'funil' && payload?.colunas) {
                    updateColumnCounter(sourceColumn, payload.colunas.origem);
                    updateColumnCounter(targetColumn, payload.colunas.destino);
                } else {
                    atualizarResumoEncerradas(sourceColumn);
                    atualizarResumoEncerradas(targetColumn);
                }
                atualizarVisualStatusEncerrada(card, novoStatus);
                card.classList.add('move-success');
                mostrarAvisoCopiado(payload?.message || 'Proposta movida com sucesso');
                setTimeout(() => card.classList.remove('move-success'), 1400);
            } catch (error) {
                console.error(error);
                restoreCard(card, sourceArea, nextSibling);
                refreshEmptyState(sourceArea);
                refreshEmptyState(cardsArea);
                if (modulo === 'funil') {
                    updateColumnCounter(sourceColumn);
                    updateColumnCounter(targetColumn);
                } else {
                    atualizarResumoEncerradas(sourceColumn);
                    atualizarResumoEncerradas(targetColumn);
                }
                card.classList.add('move-error');
                mostrarAvisoCopiado(error.message || 'Não foi possível mover a proposta', 'erro');
                setTimeout(() => card.classList.remove('move-error'), 1800);
            } finally {
                card.dataset.busy = 'false';
                card.classList.remove('is-processing');
                card.setAttribute('draggable', 'true');
                restoreScroll(kanban, kanbanScrollLeft, sourceArea, sourceScrollTop, cardsArea, targetScrollTop);
            }
        });
    });

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
            <a class="quick-search-item" href="${appendOrigin(item.url)}">
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

    function appendOrigin(url) {
        const separator = String(url || '').includes('?') ? '&' : '?';
        const origem = window.location.pathname + window.location.search;
        return `${url}${separator}origem=${encodeURIComponent(origem || '/propostas')}`;
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
            window.location.href = appendOrigin(lastItems[0].url);
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
        botaoTema.innerHTML = tema === 'escuro'
            ? '<i class="bi bi-sun" aria-hidden="true"></i><span>Modo claro</span>'
            : '<i class="bi bi-moon" aria-hidden="true"></i><span>Modo escuro</span>';
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
        });
    });

    activateTab('resumo');
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
    const prazosJson = document.getElementById('simPrazosJson');
    const adicionarPrazo = document.getElementById('simAdicionarPrazo');
    const editarCoeficiente = document.getElementById('simEditarCoeficiente');
    const prazoEditor = document.getElementById('simPrazoEditor');
    const prazoLabelInput = document.getElementById('simPrazoLabel');
    const prazoCoefInput = document.getElementById('simPrazoCoeficiente');
    const salvarPrazo = document.getElementById('simSalvarPrazo');
    const cancelarPrazo = document.getElementById('simCancelarPrazo');
    const resumoTexto = document.getElementById('simResumoTexto');
    const copiarResumo = form.querySelector('[data-copy]');
    const storageKey = 'crmSimuladorInssPrazos';
    let prazoEmEdicao = null;

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

    function parseCoeficiente(value) {
        return Number(String(value || '').trim().replace(',', '.')) || 0;
    }

    function sincronizarPrazos() {
        if (prazosJson) prazosJson.value = JSON.stringify(dados.novo || {});
        try { localStorage.setItem(storageKey, JSON.stringify(dados.novo || {})); } catch (e) {}
    }

    function aplicarPrazosSalvos() {
        try {
            const salvos = JSON.parse(localStorage.getItem(storageKey) || '{}');
            if (salvos && typeof salvos === 'object') {
                dados.novo = { ...(dados.novo || {}), ...salvos };
            }
        } catch (e) {}
    }

    function atualizarOpcoesPrazo(valorSelecionado = null) {
        if (!prazo) return;
        const atual = valorSelecionado || prazo.value;
        Object.entries(dados.novo || {}).forEach(([codigo, item]) => {
            let option = prazo.querySelector(`option[value="${CSS.escape(codigo)}"]`);
            if (!option) {
                option = document.createElement('option');
                option.value = codigo;
                prazo.appendChild(option);
            }
            option.textContent = item.label || codigo;
            option.dataset.label = item.label || codigo;
            option.dataset.coef = item.coeficiente || '';
        });
        if (atual && prazo.querySelector(`option[value="${CSS.escape(atual)}"]`)) {
            prazo.value = atual;
        }
        sincronizarPrazos();
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

        const item = dados.novo[prazo.value] || dados.novo['108_carencia'] || {};
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

    function abrirEditor(modo) {
        if (!prazoEditor || !prazoLabelInput || !prazoCoefInput) return;
        prazoEmEdicao = modo === 'novo' ? null : (prazo ? prazo.value : null);
        const item = prazoEmEdicao ? (dados.novo[prazoEmEdicao] || {}) : {};
        prazoLabelInput.value = item.label || '';
        prazoCoefInput.value = item.coeficiente ? Number(item.coeficiente).toFixed(6) : '';
        prazoEditor.classList.remove('hidden');
        prazoLabelInput.focus();
    }

    function fecharEditor() {
        if (prazoEditor) prazoEditor.classList.add('hidden');
        prazoEmEdicao = null;
    }

    function salvarEdicaoPrazo() {
        if (!prazoLabelInput || !prazoCoefInput || !prazo) return;
        const label = prazoLabelInput.value.trim();
        const coeficiente = parseCoeficiente(prazoCoefInput.value);
        if (!label || !coeficiente) {
            window.alert('Informe o nome do prazo e um coeficiente válido.');
            return;
        }
        const codigo = prazoEmEdicao || `custom_${Date.now()}`;
        dados.novo[codigo] = { label, coeficiente, idade: '' };
        atualizarOpcoesPrazo(codigo);
        prazo.value = codigo;
        fecharEditor();
        calcular(tipo && tipo.value === 'novo_margem' ? margem : valorBase);
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
    if (adicionarPrazo) adicionarPrazo.addEventListener('click', () => abrirEditor('novo'));
    if (editarCoeficiente) editarCoeficiente.addEventListener('click', () => abrirEditor('editar'));
    if (salvarPrazo) salvarPrazo.addEventListener('click', salvarEdicaoPrazo);
    if (cancelarPrazo) cancelarPrazo.addEventListener('click', fecharEditor);
    form.addEventListener('submit', sincronizarPrazos);

    aplicarPrazosSalvos();
    atualizarOpcoesPrazo(prazo ? prazo.value : null);
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

