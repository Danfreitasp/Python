import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QMessageBox,
    QHeaderView
)
from PySide6.QtCore import Qt


class ClienteApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exemplo PySide6 - Cadastro de Clientes")
        self.setMinimumSize(900, 600)

        self.clientes = []

        self.criar_interface()
        self.aplicar_estilo()

    def criar_interface(self):
        container = QWidget()
        self.setCentralWidget(container)

        layout_principal = QVBoxLayout(container)

        titulo = QLabel("Cadastro de Clientes")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setObjectName("titulo")

        layout_principal.addWidget(titulo)

        # Formulário
        form_layout = QFormLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Ex: Maria Silva")

        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("Ex: 123.456.789-00")

        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("Ex: (27) 99999-9999")

        self.input_observacao = QTextEdit()
        self.input_observacao.setPlaceholderText("Digite alguma observação...")
        self.input_observacao.setFixedHeight(80)

        form_layout.addRow("Nome:", self.input_nome)
        form_layout.addRow("CPF:", self.input_cpf)
        form_layout.addRow("Telefone:", self.input_telefone)
        form_layout.addRow("Observação:", self.input_observacao)

        layout_principal.addLayout(form_layout)

        # Botões
        layout_botoes = QHBoxLayout()

        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_limpar = QPushButton("Limpar")
        self.btn_excluir = QPushButton("Excluir selecionado")

        self.btn_adicionar.clicked.connect(self.adicionar_cliente)
        self.btn_limpar.clicked.connect(self.limpar_campos)
        self.btn_excluir.clicked.connect(self.excluir_cliente)

        layout_botoes.addWidget(self.btn_adicionar)
        layout_botoes.addWidget(self.btn_limpar)
        layout_botoes.addWidget(self.btn_excluir)

        layout_principal.addLayout(layout_botoes)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels([
            "Nome",
            "CPF",
            "Telefone",
            "Observação"
        ])

        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

        layout_principal.addWidget(self.tabela)

    def adicionar_cliente(self):
        nome = self.input_nome.text().strip()
        cpf = self.input_cpf.text().strip()
        telefone = self.input_telefone.text().strip()
        observacao = self.input_observacao.toPlainText().strip()

        if not nome:
            QMessageBox.warning(self, "Atenção", "Informe o nome do cliente.")
            return

        if not cpf:
            QMessageBox.warning(self, "Atenção", "Informe o CPF do cliente.")
            return

        cliente = {
            "nome": nome,
            "cpf": cpf,
            "telefone": telefone,
            "observacao": observacao
        }

        self.clientes.append(cliente)
        self.atualizar_tabela()
        self.limpar_campos()

        QMessageBox.information(self, "Sucesso", "Cliente adicionado com sucesso.")

    def atualizar_tabela(self):
        self.tabela.setRowCount(len(self.clientes))

        for linha, cliente in enumerate(self.clientes):
            self.tabela.setItem(linha, 0, QTableWidgetItem(cliente["nome"]))
            self.tabela.setItem(linha, 1, QTableWidgetItem(cliente["cpf"]))
            self.tabela.setItem(linha, 2, QTableWidgetItem(cliente["telefone"]))
            self.tabela.setItem(linha, 3, QTableWidgetItem(cliente["observacao"]))

    def limpar_campos(self):
        self.input_nome.clear()
        self.input_cpf.clear()
        self.input_telefone.clear()
        self.input_observacao.clear()
        self.input_nome.setFocus()

    def excluir_cliente(self):
        linha_selecionada = self.tabela.currentRow()

        if linha_selecionada < 0:
            QMessageBox.warning(
                self,
                "Atenção",
                "Selecione um cliente na tabela para excluir."
            )
            return

        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja realmente excluir o cliente selecionado?",
            QMessageBox.Yes | QMessageBox.No
        )

        if resposta == QMessageBox.Yes:
            del self.clientes[linha_selecionada]
            self.atualizar_tabela()

    def aplicar_estilo(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f6f8;
            }

            QLabel {
                font-size: 14px;
            }

            QLabel#titulo {
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
                margin: 12px;
            }

            QLineEdit, QTextEdit {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #2563eb;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                gridline-color: #e5e7eb;
                font-size: 13px;
            }

            QHeaderView::section {
                background-color: #e5e7eb;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    janela = ClienteApp()
    janela.show()

    sys.exit(app.exec())