(() => {
    'use strict';

    const formGrid = document.getElementById('propostaFormGrid');
    const status = document.getElementById('portalImportStatus');
    if (!formGrid || !status) return;

    let aguardando = false;

    function atualizarEstado(novoEstado, mensagem) {
        aguardando = novoEstado;
        document.body.dataset.crmImportacaoPortal = novoEstado ? 'aguardando' : 'inativa';
        status.textContent = mensagem;
    }

    window.crmImportacaoPortal = {
        estaAguardando: () => aguardando,
    };

    atualizarEstado(true, 'Aguardando dados do Sistemacorban nesta aba.');

    // Ponte chamada pela extensão no contexto principal da aba do CRM.
    // Preenche campos, mas deliberadamente não dispara submit nem requisição.
    window.aplicarDadosConsultaINSS = function (dados = {}) {
        if (!aguardando) {
            return { sucesso: false, motivo: 'A Nova Proposta não está aguardando importação.' };
        }

        const mapa = {
            nome: dados.nome,
            cpf: dados.cpf,
            nascimento: dados.nascimento,
            nb_matricula: dados.nb,
            especie: dados.especie,
            endereco: dados.endereco,
            dados_bancarios: dados.dados_bancarios,
        };
        const preenchidos = [];
        Object.entries(mapa).forEach(([name, value]) => {
            if (value === undefined || value === null || String(value).trim() === '') return;
            const field = document.querySelector(`[name="${name}"]`);
            if (!field) return;
            field.value = String(value);
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
            field.classList.add('portal-import-highlight');
            preenchidos.push(field);
        });

        atualizarEstado(false, 'Dados importados. Revise antes de salvar.');
        window.setTimeout(() => preenchidos.forEach((field) => field.classList.remove('portal-import-highlight')), 3500);
        return { sucesso: true, camposPreenchidos: preenchidos.length };
    };
})();
