#!/usr/bin/env python3
"""
Debian Control Center - QtWidgets front-end
"""

import sys
import shutil
import subprocess
from pathlib import Path

# ----------------------------
# Import Qt (PyQt6 → fallback PyQt5)
# ----------------------------
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
        QGroupBox, QGridLayout, QFileDialog, QMessageBox, QLabel
    )
    from PyQt6.QtGui import (QIcon, QGuiApplication)
    from PyQt6.QtCore import Qt
    PYQT_VERSION = 6
except Exception:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout,
        QGroupBox, QGridLayout, QFileDialog, QMessageBox
    )
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import Qt
    PYQT_VERSION = 5


APP_DIR = Path(__file__).resolve().parent


# ----------------------------
# Helpers
# ----------------------------

def ask_question(parent, title, text):
    """Cross-compatible confirmation dialog for PyQt5 and PyQt6."""
    if PYQT_VERSION == 6:
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        reply = QMessageBox.question(parent, title, text, buttons)
        return reply == QMessageBox.StandardButton.Yes
    else:
        reply = QMessageBox.question(
            parent, title, text,
            QMessageBox.Yes | QMessageBox.No
        )
        return reply == QMessageBox.Yes


def run_polkit_command(cmd):
    """Runs a command via pkexec (non-interactive)."""
    try:
        subprocess.Popen([
            "pkexec", "env",
            "DISPLAY=" + shutil.os.environ.get("DISPLAY", ""),
            "XAUTHORITY=" + shutil.os.environ.get("XAUTHORITY", ""),
            "bash", "-lc", cmd
        ])
    except Exception as e:
        print("Error executing pkexec:", e)


def run_terminal_command(title, cmd):
    """
    Opens a terminal safely under Wayland/X11.
    Supports konsole, konsole6, qterminal, tilix, xfce4-terminal, kgx, xterm.
    """

    terminals = [
        ("konsole", ["konsole", "-e"]),
        ("konsole6", ["konsole6", "-e"]),
        ("qterminal", ["qterminal", "-e"]),
        ("tilix", ["tilix", "-e"]),
        ("xfce4-terminal", ["xfce4-terminal", "-e"]),
        ("kgx", ["kgx", "--"]),   # GNOME Console
        ("xterm", ["xterm", "-T", title, "-e"])
    ]

    for binary, launch in terminals:
        if shutil.which(binary):
            try:
                full_cmd = launch + [
                    f'bash -lc "sudo {cmd}; echo; echo \'[Comando APT finalizado!]\'; read -p \'Pressione ENTER para fechar...\' _"'
                ]
                subprocess.Popen(full_cmd)
                return
            except Exception as e:
                print(f"Erro ao tentar terminal {binary}:", e)

    QMessageBox.warning(
        None,
        "Erro",
        "Nenhum terminal compatível encontrado.\n"
        "Instale: konsole, xterm, tilix, qterminal, kgx ou xfce4-terminal."
    )


# ----------------------------
# Main Window
# ----------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Debian Control Center")
        self.setMinimumSize(650, 500)
        self.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/debian-control-center.svg"))

        central = QWidget()
        main = QVBoxLayout(central)
        main.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setCentralWidget(central)

        titulo_topo = QLabel("Bem vindo ao Debian Control Center!")
        titulo_topo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_topo.setStyleSheet("font-weight: bold; padding: 8px;")
        main.addWidget(titulo_topo)

        # -------------------------------------------------
        # DEBIAN ADMIN GROUP
        # -------------------------------------------------
        group_deb_admin = QGroupBox("Administração Debian")
        grid = QGridLayout()

        btn_synaptic = QPushButton("Gerenciador de Pacotes Synaptic")
        btn_synaptic.setIcon(QIcon.fromTheme("box_debian_disc"))
        btn_synaptic.clicked.connect(lambda: run_polkit_command("synaptic"))

        btn_gkdebconf = QPushButton("Gerenciador de Configurações Debconf")
        btn_gkdebconf.setIcon(QIcon.fromTheme("gkdebconf-icon"))
        btn_gkdebconf.clicked.connect(lambda: run_polkit_command("gkdebconf"))

        btn_editorconf = QPushButton("Editor de Configurações Dconf")
        btn_editorconf.setIcon(QIcon.fromTheme("folder-deb"))
        btn_editorconf.clicked.connect(lambda: subprocess.Popen(["dconf-editor"]))

        btn_galternatives = QPushButton("Configurações de Apps Alternativos")
        btn_galternatives.setIcon(QIcon.fromTheme("galternatives"))
        btn_galternatives.clicked.connect(lambda: subprocess.Popen(["galternatives"]))

        btn_aptclean = QPushButton("APT - Limpar o Cache de Pacotes")
        btn_aptclean.setIcon(QIcon.fromTheme("debian-emblem-black"))
        btn_aptclean.clicked.connect(self.confirm_autoclean)

        btn_aptautoremove = QPushButton("APT - Remover Pacotes Órfãos")
        btn_aptautoremove.setIcon(QIcon.fromTheme("debian-emblem-black"))
        btn_aptautoremove.clicked.connect(self.confirm_autoremove)

        btn_aptfixbroken = QPushButton("APT - Corrigir Dependências Quebradas")
        btn_aptfixbroken.setIcon(QIcon.fromTheme("debian-emblem-black"))
        btn_aptfixbroken.clicked.connect(self.confirm_fixbroken)

        btn_aptupgrade = QPushButton("APT - Atualizar Pacotes")
        btn_aptupgrade.setIcon(QIcon.fromTheme("debian-emblem-black"))
        btn_aptupgrade.clicked.connect(self.confirm_upgrade)

        btn_open_deb = QPushButton("Visualizador de Pacotes .deb")
        btn_open_deb.setIcon(QIcon.fromTheme("deb-gview"))
        btn_open_deb.clicked.connect(self.open_deb_dialog)

        btn_calamares = QPushButton("Instalador Debian Live Calamares")
        btn_calamares.setIcon(QIcon.fromTheme("calamares"))
        btn_calamares.clicked.connect(lambda: run_polkit_command("calamares"))

        grid.addWidget(btn_synaptic, 0, 0)
        grid.addWidget(btn_gkdebconf, 0, 1)
        grid.addWidget(btn_editorconf, 1, 0)
        grid.addWidget(btn_galternatives, 1, 1)
        grid.addWidget(btn_aptclean, 2, 0)
        grid.addWidget(btn_aptautoremove, 2, 1)
        grid.addWidget(btn_aptfixbroken, 3, 0)
        grid.addWidget(btn_aptupgrade, 3, 1)
        grid.addWidget(btn_open_deb, 4, 0)
        grid.addWidget(btn_calamares, 4, 1)

        group_deb_admin.setLayout(grid)
        main.addWidget(group_deb_admin)

        # -------------------------------------------------
        # ADMIN GROUP
        # -------------------------------------------------
        group_admin = QGroupBox("Administração do Sistema")
        grid = QGridLayout()

        btn_hardinfo = QPushButton("Gerenciador de Dispositivos (hardinfo)")
        btn_hardinfo.setIcon(QIcon.fromTheme("hardinfo2"))
        btn_hardinfo.clicked.connect(self.open_hardinfo)

        btn_gparted = QPushButton("Gerenciamento de Disco (gparted)")
        btn_gparted.setIcon(QIcon.fromTheme("gparted"))
        btn_gparted.clicked.connect(lambda: run_polkit_command("gparted"))

        btn_sysd = QPushButton("Gerenciador de Serviços (systemd)")
        btn_sysd.setIcon(QIcon.fromTheme("io.github.plrigaux.sysd-manager"))
        btn_sysd.clicked.connect(self.open_sysd_manager)

        btn_resources = QPushButton("Gerenciador de Tarefas e Recursos")
        btn_resources.setIcon(QIcon.fromTheme("net.nokyan.Resources"))
        btn_resources.clicked.connect(self.open_resources)

        btn_network = QPushButton("Configurações de Rede")
        btn_network.setIcon(QIcon.fromTheme("preferences-system-network"))
        btn_network.clicked.connect(lambda: subprocess.Popen(["nm-connection-editor"]))

        btn_open_printer = QPushButton("Gerenciador de Impressoras")
        btn_open_printer.setIcon(QIcon.fromTheme("preferences-devices-printer"))
        btn_open_printer.clicked.connect(lambda: subprocess.Popen(["system-config-printer"]))

        btn_timeshift = QPushButton("Restauração e Backup (timeshift)")
        btn_timeshift.setIcon(QIcon.fromTheme("timeshift"))
        btn_timeshift.clicked.connect(lambda: run_polkit_command("timeshift-launcher"))

        btn_warehouse = QPushButton("Administrar Flatpaks (Warehouse)")
        btn_warehouse.setIcon(QIcon.fromTheme("io.github.flattool.Warehouse"))
        btn_warehouse.clicked.connect(self.open_warehouse)

        grid.addWidget(btn_hardinfo, 1, 0)
        grid.addWidget(btn_gparted, 1, 1)
        grid.addWidget(btn_sysd, 2, 0)
        grid.addWidget(btn_resources, 2, 1)
        grid.addWidget(btn_network, 3, 0)
        grid.addWidget(btn_open_printer, 3, 1)
        grid.addWidget(btn_timeshift, 4, 0)
        grid.addWidget(btn_warehouse, 4, 1)

        group_admin.setLayout(grid)
        main.addWidget(group_admin)

        # -------------------------------------------------
        # SEGURANCA
        # -------------------------------------------------
        group_security = QGroupBox("Administração da Segurança")
        grid = QGridLayout()

        btn_gufw = QPushButton("Configurações do Firewall")
        btn_gufw.setIcon(QIcon.fromTheme("gufw"))
        btn_gufw.clicked.connect(lambda: run_polkit_command("gufw"))

        btn_firetools = QPushButton("Configurações do Firejail")
        btn_firetools.setIcon(QIcon.fromTheme("firetools"))
        btn_firetools.clicked.connect(lambda: subprocess.Popen(["firetools"]))

        btn_users = QPushButton("Contas de Usuários e Grupos")
        btn_users.setIcon(QIcon.fromTheme("debian-security"))
        btn_users.clicked.connect(lambda: subprocess.Popen(["lxqt-admin-user"]))

        btn_linux_assistant = QPushButton("Assistente Linux")
        btn_linux_assistant.setIcon(QIcon.fromTheme("io.github.jean28518.Linux-Assistant"))
        btn_linux_assistant.clicked.connect(self.open_linux_assistant)

        grid.addWidget(btn_gufw, 0, 0)
        grid.addWidget(btn_firetools, 0, 1)
        grid.addWidget(btn_users, 1, 0)
        grid.addWidget(btn_linux_assistant, 1, 1)

        group_security.setLayout(grid)
        main.addWidget(group_security)

        # -------------------------------------------------
        # EDITOR
        # -------------------------------------------------
        group_edit = QGroupBox("Edição de Arquivos")
        grid = QGridLayout()

        btn_kate = QPushButton("Editar /etc/default/grub")
        btn_kate.setIcon(QIcon.fromTheme("kate"))
        btn_kate.clicked.connect(lambda: run_polkit_command("kate /etc/default/grub"))

        grid.addWidget(btn_kate, 0, 0)
        group_edit.setLayout(grid)
        main.addWidget(group_edit)

    # -----------------------------------------------------
    # FUNCTIONS
    # -----------------------------------------------------

    # ---- hardinfo ----
    def open_hardinfo(self):
        if shutil.which("hardinfo2"):
            subprocess.Popen(["hardinfo2"])
        elif shutil.which("hardinfo"):
            subprocess.Popen(["hardinfo"])
        else:
            QMessageBox.warning(self, "Erro", "Hardinfo não instalado.")

    # ---- APT (com confirmação + terminal) ----

    def confirm_autoclean(self):
        if ask_question(self, "Confirmar", "Isto removerá TODOS os pacotes do cache.\nDeseja continuar?"):
            run_terminal_command("apt clean", "apt clean")

    def confirm_autoremove(self):
        if ask_question(
            self, "Confirmar", "Isto removerá somente os pacotes órfãos.\nDeseja continuar?"
        ):
            run_terminal_command("apt autoremove --purge -y", "apt autoremove --purge -y")

    def confirm_fixbroken(self):
        if ask_question(self, "Confirmar", "Esta ação corrigirá as dependências quebradas.\nDeseja continuar?"):
            run_terminal_command("apt fix-broken", "apt --fix-broken install -y")

    def confirm_upgrade(self):
        if ask_question(self, "Confirmar", "Atualizar todos os pacotes?"):
            run_terminal_command("apt update && sudo apt full-upgrade -y", "apt update && sudo apt full-upgrade -y")

    # ---- .deb viewer ----

    def open_deb_dialog(self):
        default_dir = "/var/cache/apt/archives"

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo .deb",
            default_dir,
            "Pacotes Debian (*.deb)"
        )

        if path:
            if shutil.which("deb-gview"):
                subprocess.Popen(["deb-gview", path])
            else:
                QMessageBox.warning(self, "Erro", "deb-gview não instalado.")

    # ---- sysd-manager ----

    def open_sysd_manager(self):
        if not shutil.which("flatpak"):
            QMessageBox.warning(self, "Erro", "Flatpak não instalado.")
            return

        cmd = [
            "flatpak",
            "run",
            "--branch=stable",
            "--arch=x86_64",
            "--command=sysd-manager",
            "io.github.plrigaux.sysd-manager"
        ]

        try:
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Não foi possível executar o sysd-manager:\n{e}"
            )

    # ---- resources ----
    def open_resources(self):
        if not shutil.which("flatpak"):
            QMessageBox.warning(self, "Erro", "Flatpak não instalado.")
            return

        cmd = [
            "flatpak",
            "run",
            "--branch=stable",
            "--arch=x86_64",
            "--command=resources",
            "net.nokyan.Resources"
        ]

        try:
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Não foi possível executar o Resources:\n{e}"
            )

    # ---- linux-assistant ----
    def open_linux_assistant(self):
        if not shutil.which("flatpak"):
            QMessageBox.warning(self, "Erro", "Flatpak não instalado.")
            return

        cmd = [
            "flatpak",
            "run",
            "--branch=stable",
            "--arch=x86_64",
            "--command=linux-assistant",
            "io.github.jean28518.Linux-Assistant"
        ]

        try:
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Não foi possível executar o Linux Assistant:\n{e}"
            )

    # ---- warehouse ----
    def open_warehouse(self):
        if not shutil.which("flatpak"):
            QMessageBox.warning(self, "Erro", "Flatpak não instalado.")
            return

        cmd = [
            "flatpak",
            "run",
            "--branch=stable",
            "--arch=x86_64",
            "--command=warehouse",
            "io.github.flattool.Warehouse"
        ]

        try:
            subprocess.Popen(cmd)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Não foi possível executar o Warehouse:\n{e}"
            )

# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    app_icon = QIcon("/usr/share/icons/hicolor/scalable/apps/debian-control-center.svg")
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.setWindowIcon(app_icon)    # NECESSÁRIO NO WAYLAND
    window.show()

    sys.exit(app.exec())
