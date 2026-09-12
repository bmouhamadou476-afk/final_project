import time

from netmiko import ConnectHandler

from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException,
)


class NetmikoService:

    def __init__(
        self,
        host,
        username=None,
        password=None,
        device_type="cisco_ios",
        secret=None,
        port=22,
    ):

        self.host = host
        self.username = username
        self.password = password
        self.device_type = device_type
        self.secret = secret
        self.port = port

        self.connection = None

    # ============================================================
    # CONNEXION SSH
    # ============================================================

    def connect(
        self,
        max_attempts=10,
        delay=10,
    ):

        last_error = None

        for attempt in range(
            1,
            max_attempts + 1,
        ):

            try:

                self.connection = ConnectHandler(
                    device_type=self.device_type,
                    host=self.host,
                    username=self.username,
                    password=self.password,
                    secret=self.secret,
                    port=self.port,
                    conn_timeout=30,
                    banner_timeout=60,
                    auth_timeout=30,
                    fast_cli=False,
                )

                if self.secret:

                    try:
                        self.connection.enable()
                    except Exception:
                        pass

                print(
                    f"[Netmiko SSH] "
                    f"Connexion réussie vers "
                    f"{self.host}:{self.port}"
                )

                return True

            except (
                NetmikoTimeoutException,
                NetmikoAuthenticationException,
                Exception,
            ) as error:

                last_error = error

                print(
                    f"[Netmiko SSH] Tentative "
                    f"{attempt}/{max_attempts} "
                    f"échouée pour "
                    f"{self.host}:{self.port} : "
                    f"{error}"
                )

                if attempt < max_attempts:
                    time.sleep(delay)

        raise ValueError(
            f"Impossible de se connecter "
            f"à {self.host}:{self.port} "
            f"après {max_attempts} tentatives. "
            f"Dernière erreur : "
            f"{last_error}"
        )

    # ============================================================
    # CONNEXION CONSOLE TELNET GNS3
    # ============================================================

    def connect_console(
        self,
        console_host,
        console_port,
        max_attempts=10,
        delay=5,
    ):

        last_error = None

        for attempt in range(
            1,
            max_attempts + 1,
        ):

            try:

                self.connection = ConnectHandler(
                    device_type="cisco_ios_telnet",
                    host=console_host,
                    port=console_port,
                    username="",
                    password="",
                    conn_timeout=30,
                    banner_timeout=60,
                    auth_timeout=30,
                    fast_cli=False,
                )

                time.sleep(2)

                print(
                    f"[Console GNS3] "
                    f"Connexion réussie vers "
                    f"{console_host}:{console_port}"
                )

                return True

            except Exception as error:

                last_error = error

                print(
                    f"[Console GNS3] Tentative "
                    f"{attempt}/{max_attempts} "
                    f"échouée pour "
                    f"{console_host}:{console_port} : "
                    f"{error}"
                )

                if attempt < max_attempts:
                    time.sleep(delay)

        raise ValueError(
            f"Impossible de se connecter "
            f"à la console GNS3 "
            f"{console_host}:{console_port}. "
            f"Dernière erreur : "
            f"{last_error}"
        )

    # ============================================================
    # PRÉPARATION DE LA CONSOLE IOS
    # ============================================================

    def prepare_console(self):

        if not self.connection:
            raise ValueError(
                "Aucune connexion console active"
            )

        try:

            output = self.connection.send_command_timing(
                "",
                strip_prompt=False,
                strip_command=False,
            )

            if (
                "initial configuration dialog"
                in output.lower()
            ):

                output += (
                    self.connection
                    .send_command_timing("no")
                )

            if (
                "press return to get started"
                in output.lower()
            ):

                output += (
                    self.connection
                    .send_command_timing("")
                )

            return output

        except Exception as error:

            print(
                f"[Console] "
                f"Préparation IOS : {error}"
            )

            return ""

    # ============================================================
    # COMMANDE SHOW
    # ============================================================

    def send_command(
        self,
        command,
    ):

        if not self.connection:
            raise ValueError(
                "Aucune connexion Netmiko active"
            )

        return self.connection.send_command(
            command
        )

    # ============================================================
    # COMMANDE INTERACTIVE
    # ============================================================

    def send_command_timing(
        self,
        command,
        delay_factor=1,
    ):

        if not self.connection:
            raise ValueError(
                "Aucune connexion Netmiko active"
            )

        return self.connection.send_command_timing(
            command,
            delay_factor=delay_factor,
        )

    # ============================================================
    # PLUSIEURS COMMANDES SHOW
    # ============================================================

    def send_commands(
        self,
        commands,
    ):

        results = {}

        for command in commands:

            results[command] = (
                self.send_command(
                    command
                )
            )

        return results

    # ============================================================
    # CONFIGURATION
    # ============================================================

    def send_config(
        self,
        commands,
    ):

        if not self.connection:
            raise ValueError(
                "Aucune connexion Netmiko active"
            )

        return self.connection.send_config_set(
            commands
        )

    # ============================================================
    # BOOTSTRAP VIA CONSOLE
    # ============================================================

    def bootstrap_configuration(
        self,
        commands,
    ):

        if not self.connection:
            raise ValueError(
                "Aucune connexion console active"
            )

        return self.connection.send_config_set(
            commands
        )

    # ============================================================
    # GÉNÉRATION DES CLÉS RSA
    # ============================================================

    def generate_rsa_keys(
        self,
        modulus=1024,
    ):

        if not self.connection:
            raise ValueError(
                "Aucune connexion active"
            )

        output = self.connection.send_command_timing(
            f"crypto key generate rsa modulus {modulus}",
            delay_factor=2,
        )

        # Gestion d'une éventuelle confirmation
        if (
            "yes/no" in output.lower()
            or "confirm" in output.lower()
            or "overwrite" in output.lower()
        ):

            output += (
                self.connection
                .send_command_timing(
                    "yes",
                    delay_factor=2,
                )
            )

        time.sleep(3)

        return output

    # ============================================================
    # CONFIGURATION SSH
    # ============================================================

    def configure_ssh(self):

        if not self.connection:
            raise ValueError(
                "Aucune connexion active"
            )

        return self.connection.send_config_set(
            [
                "ip ssh version 2",
            ]
        )

    # ============================================================
    # SAUVEGARDE
    # ============================================================

    def save_config(self):

        if not self.connection:
            raise ValueError(
                "Aucune connexion Netmiko active"
            )

        try:

            return self.connection.save_config()

        except Exception:

            return self.connection.send_command(
                "write memory"
            )

    # ============================================================
    # PING
    # ============================================================

    def ping(
        self,
        target,
    ):

        return self.send_command(
            f"ping {target}"
        )

    # ============================================================
    # DÉCONNEXION
    # ============================================================

    def disconnect(self):

        if self.connection:

            try:
                self.connection.disconnect()
            except Exception:
                pass

            self.connection = None