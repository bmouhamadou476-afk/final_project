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


    # ==================================================
    # CONNEXION SSH
    # ==================================================

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

                    banner_timeout=30,

                    auth_timeout=30,

                    fast_cli=False,

                )

                if self.secret:

                    self.connection.enable()

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

                    time.sleep(
                        delay
                    )


        raise ValueError(

            f"Impossible de se connecter "
            f"à {self.host}:{self.port} "
            f"après {max_attempts} tentatives. "
            f"Dernière erreur : "
            f"{last_error}"

        )


    # ==================================================
    # CONNEXION CONSOLE TELNET GNS3
    # ==================================================

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

                    secret="",

                    conn_timeout=30,

                    banner_timeout=30,

                    auth_timeout=30,

                    fast_cli=False,

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

                    time.sleep(
                        delay
                    )


        raise ValueError(

            f"Impossible de se connecter "
            f"à la console GNS3 "
            f"{console_host}:{console_port}. "
            f"Dernière erreur : "
            f"{last_error}"

        )


    # ==================================================
    # EXECUTION COMMANDE SHOW
    # ==================================================

    def send_command(
        self,
        command,
    ):

        if not self.connection:

            raise ValueError(

                "Aucune connexion Netmiko active"

            )


        return (

            self.connection.send_command(
                command
            )

        )


    # ==================================================
    # EXECUTION PLUSIEURS COMMANDES SHOW
    # ==================================================

    def send_commands(
        self,
        commands,
    ):

        results = {}


        for command in commands:

            results[
                command
            ] = (

                self.send_command(
                    command
                )

            )


        return results


    # ==================================================
    # ENVOI CONFIGURATION
    # ==================================================

    def send_config(
        self,
        commands,
    ):

        if not self.connection:

            raise ValueError(

                "Aucune connexion Netmiko active"

            )


        return (

            self.connection.send_config_set(
                commands
            )

        )


    # ==================================================
    # BOOTSTRAP VIA CONSOLE
    # ==================================================

    def bootstrap_configuration(
        self,
        commands,
    ):

        if not self.connection:

            raise ValueError(

                "Aucune connexion console active"

            )


        return (

            self.connection.send_config_set(
                commands
            )

        )


    # ==================================================
    # SAUVEGARDE CONFIGURATION
    # ==================================================

    def save_config(self):

        if not self.connection:

            raise ValueError(

                "Aucune connexion Netmiko active"

            )


        return (

            self.connection.save_config()

        )


    # ==================================================
    # PING
    # ==================================================

    def ping(
        self,
        target,
    ):

        return (

            self.send_command(

                f"ping {target}"

            )

        )


    # ==================================================
    # DECONNEXION
    # ==================================================

    def disconnect(self):

        if self.connection:

            self.connection.disconnect()

            self.connection = None