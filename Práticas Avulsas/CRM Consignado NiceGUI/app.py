from nicegui import ui
import main  # noqa: F401 - registers pages and styles

if __name__ == '__main__':
    ui.run(
        title='CRM Consignado',
        favicon='📋',
        host='127.0.0.1',
        port=8080,
        reload=False,
        show=False,
    )
